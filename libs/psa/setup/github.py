from hashlib import sha1

import requests

from mylogger import logger


def get_github_sha_from_file(user, repo, directory, filename):
    res = requests.get("https://api.github.com/repos/{}/{}/git/trees/main:{}".format(user, repo, directory)).json()
    file_info = next((file for file in res["tree"] if file['path'] == filename))
    return file_info["sha"]


def github_file_need_to_be_downloaded(user, repo, directory, filename):
    try:
        with open(filename, 'rb') as file_for_hash:
            data = file_for_hash.read()
            filesize = len(data)
        prefix = "blob " + str(filesize) + "\0"
        sha_of_downloaded_file = sha1(prefix.encode("utf-8") + data).hexdigest()
        sha_of_git_file = get_github_sha_from_file(user, repo, directory, filename)
        if sha_of_downloaded_file == sha_of_git_file:
            logger.debug("locale file is the latest version")
            return False
        logger.debug("download last version of file")
    except FileNotFoundError:
        logger.debug("File not found, download file")
    return True


def urlretrieve_from_github(user, repo, directory, filename, branch="main"):
    if github_file_need_to_be_downloaded(user, repo, directory, filename):
        with open(filename, 'wb') as f:
            r = requests.get("https://github.com/{}/{}/raw/{}/{}{}".format(user, repo, branch, directory, filename),
                             headers={
                                 "Accept": "application/vnd.github.VERSION.raw"
                             },
                             stream=True
                             )

            r.raise_for_status()
            for chunk in r.iter_content(1024):
                f.write(chunk)
