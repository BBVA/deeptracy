import requests
import os


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


def clone_repo(base_path: str, scan_id: str, repo_url: str) -> str:
    """Creates a folder to clone a repository and clone it

    Args:
        base_path (str): Base path to clone. Should be an absolute path
        scan_id (str): Scan that triggers the clone. Its going to be created as a folder inside the base_path
        repo_url (str): Repository URL to clone

    Returns:
        Final source path
    """
    scan_path = os.path.join(base_path, scan_id)

    if not os.path.exists(scan_path):
        os.makedirs(scan_path)

    os.system('git clone {} {}'.format(repo_url, scan_path))
    return scan_path
