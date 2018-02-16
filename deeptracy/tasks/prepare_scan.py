# Copyright 2017 BBVA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import yaml
import docker

from shutil import copyfile
from celery import task
from celery.utils.log import get_task_logger

from deeptracy_core.dal.project.model import RepoAuthType
from deeptracy_core.dal.scan.manager import get_scan, update_scan_state, ScanState
from deeptracy_core.dal.database import db

import deeptracy.config as config
from .base_task import TaskException, DeeptracyTask
from .scan_deps import scan_deps

logger = get_task_logger('deeptracy')


@task(name="prepare_scan", base=DeeptracyTask)
def prepare_scan(scan_id: str):
    with db.session_scope() as session:
        logger.info('{} START SCAN'.format(scan_id))
        scan = get_scan(scan_id, session)
        project = scan.project

        logger.debug('{} for project({})'.format(scan_id, project.id))

        try:
            # clone the repository in a shared volume
            cloned_dir = clone_project(config.SHARED_VOLUME_PATH, scan_id, project.repo, project.repo_auth_type,
                                       scan.branch)
            scan.source_path = cloned_dir
            session.add(scan)
            logger.debug('{} cloned dir {}'.format(scan_id, cloned_dir))
        except Exception as e:
            update_scan_state(scan, ScanState.INVALID_BRANCH, session)
            session.commit()

            logger.error(str(e))
            raise e

        # if a .deeptracy.yml is found, parse it to a dictionary
        try:
            deeptracy_yml = parse_deeptracy_yml(cloned_dir)
            logger.debug('{} .deeptracy.yml {}'.format(scan_id, 'TRUE' if deeptracy_yml else 'FALSE'))
        except Exception as e:
            update_scan_state(scan, ScanState.INVALID_YML_ON_PROJECT, session)
            session.commit()
            logger.error('{} unable to parse .deeptracy.yml'.format(scan_id))
            raise e

        # the language for a scan can be specified on the scan of in the deeptracy file in the sources
        if scan.lang is None:
            if deeptracy_yml is None:
                update_scan_state(scan, ScanState.CANT_GET_LANGUAGE, session)
                session.commit()
                logger.debug('{} unable to retrieve language for scan'.format(scan_id))
                raise TaskException('unable to retrieve language for scan')
            else:
                lang = deeptracy_yml.get('lang')  # the parse ensures us a valid lang in the dict
                scan.lang = lang  # update the san object to store the language
                session.add(scan)

    # once the scan is ready continue with the dependency extraction

    scan_deps.delay(scan_id)


def prepare_path_to_list_branches_with_local_key(scan_path: str, repo: str, mounted_vol: str,
                                                 mounted_path_branches: str):
    """
    Prepare a folder to list a repository branches which needs a local private key.

    LOCAL_PRIVATE_KEY means we need to copy the local private key present in the host to the folder
    that is being mounted in to the container that is going to perform the actual repo to list branches

    We prepare a script with all the commands needed to perform the branches list, like adding the private key
    to the container ssh-agent and disabling host-key verification

    :param scan_path: (str) path that we need to prepare
    :param repo: (str) project repository to clone
    :param mounted_vol: (str) path to the mounted volume in the container that makes the clone
    :param mounted_path_branches: (str) name of the path at the file that contains the branches list
    :return: returns the script to create in the container that makes the branches list
    """

    logger.debug('prepare repo for list branches with local private key')
    key_name = 'local_id_rsa'
    dest_key_path = os.path.join(scan_path, key_name)
    copyfile(config.LOCAL_PRIVATE_KEY_FILE, dest_key_path)

    # Having the key in the mounted folder, prepare a script to activate the ssh-agent, disable the host
    # key verification and add the key to it after doing the branches list
    script_contents = '#!/bin/bash \n' \
                      'eval `ssh-agent -s` \n' \
                      'chmod 400 {mounted_vol}/{key} \n' \
                      'mkdir -p /root/.ssh \n' \
                      'touch /root/.ssh/config \n' \
                      'echo -e "StrictHostKeyChecking no" >> /root/.ssh/config \n' \
                      'ssh-add {mounted_vol}/{key} \n' \
                      'git  ls-remote --heads {repo} '.format(key=key_name, repo=repo, mounted_vol=mounted_vol)

    script_contents = script_contents + '| awk \'{n=split($2,a,"/"); print a[n]}\' ' \
        + '>> {mounted_path_branches}\n'.format(mounted_path_branches=mounted_path_branches)
    return script_contents


def prepare_path_to_clone_with_local_key(scan_path: str, repo: str, mounted_vol: str, source_folder: str, branch: str):
    """
    Prepare a folder to clone a repository which needs a local private key.

    LOCAL_PRIVATE_KEY means we need to copy the local private key present in the host to the folder
    that is being mounted in to the container that is going to perform the actual repo clone

    We prepare a script with all the commands needed to perform the clone, like adding the private key
    to the container ssh-agent and disabling host-key verification

    :param scan_path: (str) path that we need to prepare
    :param repo: (str) project repository to clone
    :param mounted_vol: (str) path to the mounted volume in the container that makes the clone
    :param source_folder: (str) name of the folder to made the actual clone
    :param branch: (str) name of the branch to clone
    :return: returns the command to pass to the container that makes the clone
    """
    logger.debug('prepare repo for clone with local private key')
    key_name = 'local_id_rsa'

    # Having the key in the mounted folder, preapre a script to activate the ssh-agent, disable the host
    # key verification and add the key to it after doing the clone
    script_contents = '#!/bin/bash \n' \
                      'eval `ssh-agent -s` \n' \
                      'chmod 400 {mounted_vol}/{key} \n' \
                      'mkdir -p /root/.ssh \n' \
                      'touch /root/.ssh/config \n' \
                      'echo -e "StrictHostKeyChecking no" >> /root/.ssh/config \n' \
                      'ssh-add {mounted_vol}/{key} \n' \
                      'git clone -b {branch} {repo} {mounted_vol}/{source_folder}\n' \
        .format(
            key=key_name,
            repo=repo,
            branch=branch,
            mounted_vol=mounted_vol,
            source_folder=source_folder
        )

    # create the script that makes the clone
    script = os.path.join(scan_path, 'clone.sh')
    with open(script, "w") as f:
        f.write(script_contents)
    os.system('chmod +x {}'.format(script))

    command = os.path.join(mounted_vol, 'clone.sh')
    return command


def clone_project(base_path: str, scan_id: str, repo_url: str, repo_auth_type: str, branch: str = None) -> str:
    """
    Clone a project repository.

    This method handles repository auth if the repo is not public. The repository is going to be cloned
    in "(base_path)/(scan_id)/sources" folder (it will be created).

    To do the clone a docker image is used: `bravissimolabs/alpine-git`

    :param base_path: (str) Base path to clone. Should be an absolute path
    :param scan_id: (str) Scan id that triggers the clone. Its going to be created as a folder inside the base_path
    :param repo_url: (str) project repository url to make the git clone
    :param repo_auth_type: (str) if the repo needs any kind of auth
    :param branch: (str, Optional) project branch to make the git clone

    :return: returns the sources path where the repo is cloned
    """

    branch_file = 'branches.txt'
    source_folder = 'sources'

    scan_path = os.path.join(base_path, scan_id)
    scan_path_sources = os.path.join(scan_path, source_folder)
    scan_path_branches = os.path.join(scan_path, branch_file)
    if not os.path.exists(scan_path):
        os.makedirs(scan_path)

    mounted_vol = '/opt/deeptracy'
    mounted_path_branches = os.path.join(mounted_vol, branch_file)

    if repo_auth_type == RepoAuthType.LOCAL_PRIVATE_KEY.name:
        # if the project is auth with LOCAL_PRIVATE_KEY prepare the path and get the new command to clone
        script_contents = prepare_path_to_list_branches_with_local_key(scan_path, repo_url, mounted_vol,
                                                                       mounted_path_branches)
    else:
        # Command to list public repos
        script_contents = '#!/bin/bash \n' \
                          + 'git  ls-remote --heads {repo} '.format(repo=repo_url) \
                          + '| awk \'{n=split($2,a,"/"); print a[n]}\' ' \
                          + '>> {}'.format(mounted_path_branches)

    # create the script that makes the clone
    script = os.path.join(scan_path, 'list_branches.sh')
    with open(script, "w") as f:
        f.write(script_contents)

    # Command to list public repos
    command_list_branches = 'bash /opt/deeptracy/list_branches.sh'

    logger.debug('list branches repo with command {}'.format(command_list_branches))

    docker_client = docker.from_env()

    # prepare mounted volumes
    docker_volumes = {
        scan_path: {
            'bind': mounted_vol,
            'mode': 'rw'
        }
    }

    # launch the container with a command that will clone the repo
    docker_client.containers.run(
        image='bravissimolabs/alpine-git',
        command=command_list_branches,
        remove=True,
        volumes=docker_volumes
    )

    branches = open(scan_path_branches, "r").read().splitlines()

    if branch not in branches:
        raise Exception('The branch {branch} for the scan {scan_id} in the repo {repo} not exits'.format(
            branch=branch,
            scan_id=scan_id,
            repo=repo_url
        ))

    logger.debug('repo {} branches listed'.format(repo_url))

    # TODO:  Parse the file and verify if the branch exists

    # Command to run for public repos
    command = 'git clone -b {branch} {repo} {mounted_vol}/{source_folder}/'.format(
        branch=branch,
        repo=repo_url,
        mounted_vol=mounted_vol,
        source_folder=source_folder
    )

    if repo_auth_type == RepoAuthType.LOCAL_PRIVATE_KEY.name:
        # if the project is auth with LOCAL_PRIVATE_KEY prepare the path and get the new command to clone
        command = prepare_path_to_clone_with_local_key(scan_path, repo_url, mounted_vol, source_folder, branch)

    logger.debug('clone repo with command {}'.format(command))

    docker_client = docker.from_env()

    # prepare mounted volumes
    docker_volumes = {
        scan_path: {
            'bind': mounted_vol,
            'mode': 'rw'
        }
    }

    # launch the container with a command that will clone the repo
    docker_client.containers.run(
        image='bravissimolabs/alpine-git',
        command=command,
        remove=True,
        volumes=docker_volumes
    )

    logger.debug('repo {} cloned'.format(repo_url))

    return scan_path_sources


def parse_deeptracy_yml(source_dir: str):
    """
    Find a .deeptracy.yml file inside source_dir and try to parse it.

    If the file is not found, return None

    :param source_dir:
    :return: None is the file is not found or cant be parsed, else it returns a dict with the key/values
    """
    logger.debug('try parse .deeptracy.yml at {}'.format(source_dir))
    yml_file = os.path.join(source_dir, '.deeptracy.yml')
    if os.path.isfile(yml_file):
        logger.info('.deeptracy.yml FOUND in {}'.format(source_dir))

        with open(yml_file, 'r') as contents:
            parsed = yaml.load(contents)

        assert type(parsed) is dict  # should be parsed as a dict
        assert 'lang' in parsed  # should have a lang attr
        assert type(parsed.get('lang')) is str  # TODO: assert against a valid lang ENUM

        return parsed

    return None
