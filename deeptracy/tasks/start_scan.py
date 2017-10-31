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
from celery import task, chord
from celery.utils.log import get_task_logger

from deeptracy_core.dal.project.model import RepoAuthType
from deeptracy_core.dal.plugin.manager import get_plugins_for_lang
from deeptracy_core.dal.scan.manager import get_scan, update_scan_state, ScanState
from deeptracy_core.dal.scan_analysis.manager import add_scan_analysis
from deeptracy_core.dal.database import db

import deeptracy.config as config
from .run_analyzer import run_analyzer
from .merge_results import merge_results
from .base_task import TaskException, DeeptracyTask


logger = get_task_logger('deeptracy')


@task(name="start_scan", base=DeeptracyTask)
def start_scan(scan_id: str):
    with db.session_scope() as session:
        logger.info('{} START SCAN'.format(scan_id))
        scan = get_scan(scan_id, session)
        project = scan.project

        logger.debug('{} for project({})'.format(scan_id, project.id))

        # clone the repository in a shared volume
        cloned_dir = clone_project(config.SHARED_VOLUME_PATH, scan_id, project.repo, project.repo_auth_type)
        logger.debug('{} cloned dir {}'.format(scan_id, cloned_dir))

        # if a .deeprtacy.yml is found, parse it to a dictionary
        try:
            deeptracy_yml = parse_deeptracy_yml(cloned_dir)
            logger.debug('{} .deeptracy.yml {}'.format(scan_id, 'TRUE' if deeptracy_yml else 'FALSE'))
        except Exception:
            update_scan_state(scan, ScanState.INVALID_YML_ON_PROJECT, session)
            logger.debug('{} unable to parse .deeptracy.yml'.format(scan_id))
            raise

        # the language for a scan can be specified on the scan of in the deeptracy file in the sources
        if scan.lang is not None:
            lang = scan.lang
        elif deeptracy_yml is None:
            update_scan_state(scan, ScanState.CANT_GET_LANGUAGE, session)
            logger.debug('{} unable to retrieve language for scan'.format(scan_id))
            raise TaskException('unable to retrieve language for scan')
        else:
            lang = deeptracy_yml.get('lang')  # the parse ensures us a valid lang in the dict
            scan.lang = lang  # update the san object to store the language
            session.add(scan)

        # for the lang, get the plugins that can be run
        available_plugins_for_lang = get_plugins_for_lang(lang, session)
        analysis_count = len(available_plugins_for_lang)

        if analysis_count < 1:
            update_scan_state(scan, ScanState.NO_PLUGINS_FOR_LANGUAGE, session)
            logger.debug('{} no plugins found for language {}'.format(scan_id, lang))
            raise TaskException('no plugins found for language {}'.format(lang))

        # when we have the lang, the number of analysis to run and the source code dir, update the scan
        scan.analysis_count = analysis_count
        scan.analysis_done = 0
        scan.source_path = cloned_dir
        scan.state = ScanState.RUNNING.name
        session.add(scan)
        session.commit()  # save at this point as we need the ID for this scan

        # save each analysis to be ran for this scan in the database and collect its ids
        scan_analysis_ids = []
        for plugin in available_plugins_for_lang:
            scan_analysis = add_scan_analysis(scan.id, plugin.id, session)
            session.commit()  # Commit the session to persist the scan_analysis and get and id
            scan_analysis_ids.append(scan_analysis.id)

        # create a task for each analysis to run
        analyzers = [run_analyzer.s(scan_analysis_id)
                     for scan_analysis_id in scan_analysis_ids]

        # launch all jobs
        chord(analyzers)(merge_results.s(scan_id=scan.id))


def prepare_path_to_clone_with_local_key(scan_path: str, repo: str, mounted_vol: str, source_folder: str):
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
    :return: returns the command to pass to the container that makes the clone
    """
    logger.debug('prepare repo for clone with local private key')
    key_name = 'local_id_rsa'
    dest_key_path = os.path.join(scan_path, key_name)
    copyfile(config.LOCAL_PRIVATE_KEY_FILE, dest_key_path)

    # Having the key in the mounted folder, preapre a script to activate the ssh-agent, disable the host
    # key verification and add the key to it after doing the clone
    script_contents = '#!/bin/bash \n' \
                      'eval `ssh-agent -s` \n' \
                      'chmod 400 {mounted_vol}/{key} \n' \
                      'mkdir -p /root/.ssh \n' \
                      'touch /root/.ssh/config \n' \
                      'echo -e "StrictHostKeyChecking no" >> /root/.ssh/config \n' \
                      'ssh-add {mounted_vol}/{key} \n' \
                      'git clone {repo} {mounted_vol}/{source_folder}\n' \
        .format(
            key=key_name,
            repo=repo,
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


def clone_project(base_path: str, scan_id: str, repo_url: str, repo_auth_type: str) -> str:
    """
    Clone a project repository.

    This method handles repository auth if the repo is not public. The repository is going to be cloned
    in "(base_path)/(scan_id)/sources" folder (it will be created).

    To do the clone a docker image is used: `bravissimolabs/alpine-git`

    :param base_path: (str) Base path to clone. Should be an absolute path
    :param scan_id: (str) Scan id that triggers the clone. Its going to be created as a folder inside the base_path
    :param repo_url: (str) project repository url to make the git clone
    :param repo_auth_type: (str) if the repo needs any kind of auth


    :return: returns the sources path where the repo is cloned
    """
    source_folder = 'sources'
    scan_path = os.path.join(base_path, scan_id)
    scan_path_sources = os.path.join(scan_path, source_folder)
    if not os.path.exists(scan_path):
        os.makedirs(scan_path)

    mounted_vol = '/opt/deeptracy'

    # Command to run for public repos
    command = 'git clone {repo} {mounted_vol}/{source_folder}/'.format(
        repo=repo_url,
        mounted_vol=mounted_vol,
        source_folder=source_folder
    )

    if repo_auth_type == RepoAuthType.LOCAL_PRIVATE_KEY.name:
        # if the project is auth with LOCAL_PRIVATE_KEY prepare the path and get the new command to clone
        command = prepare_path_to_clone_with_local_key(scan_path, repo_url, mounted_vol, source_folder)

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
