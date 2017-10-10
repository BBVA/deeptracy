import requests
import os
import uuid
import docker
from shutil import copyfile

import deeptracy.config as config
from deeptracy_core.dal.project.model import Project, RepoAuthType


def valid_repo(url: str):
    """Given a repository url checks if the repository is publicly accessible

    Args:
        url (str): Repository URL. Must be a full url, including schema.

    Returns:
        True for success, False otherwise

    Raises:
        requests.exceptions.RequestException
    """
    if url is None:
        raise ValueError('Missing repo url')

    # normalize repo url
    url = url.strip().replace(" ", "")
    # Check if remote is accessible
    if requests.get(url, timeout=20).status_code != 200:
        return False

    return True


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


def clone_project(base_path: str, scan_id: str, project: Project) -> str:
    """
    Clone a project repository.

    This method handles repository auth if the repo is not public. The repository is going to be cloned
    in "(base_path)/(scan_id)/sources" folder (it will be created).

    To do the clone a docker image is used: `bravissimolabs/alpine-git`

    :param base_path: (str) Base path to clone. Should be an absolute path
    :param scan_id: (str) Scan id that triggers the clone. Its going to be created as a folder inside the base_path
    :param project: (Project) project object with repo and auth type is not public

    :return: returns the sources path where the repo is cloned
    """
    source_folder = 'sources'
    scan_path = os.path.join(base_path, scan_id)
    scan_path_sources = os.path.join(scan_path, source_folder)
    if not os.path.exists(scan_path):
        os.makedirs(scan_path)

    mounted_vol = '/opt/deeptracy'

    # Command to run
    command = 'git clone {repo} {mounted_vol}/{source_folder}/'.format(
        repo=project.repo,
        mounted_vol=mounted_vol,
        source_folder=source_folder
    )

    if project.repo_auth_type == RepoAuthType.LOCAL_PRIVATE_KEY.name:
        # if the project is auth with LOCAL_PRIVATE_KEY prepare the path and get the new command to clone
        command = prepare_path_to_clone_with_local_key(scan_path, project.repo, mounted_vol, source_folder)

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

    return scan_path_sources


def make_uuid() -> str:
    return uuid.uuid4().hex
