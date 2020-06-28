"""Git module helps with everything around git management like pulling, cloning .. etc

# TODO: examples
"""
import urllib
import re
from jumpscale.loader import j

SSH_URL_MATCH = "^(git@)(?P<netloc>.*?)(:|/)(?P<path>.*?)/?$"


def rewrite_git_https_url_to_ssh(url):
    """
    :param url: (str) https url to rewrite as ssh
    :return (tuple) repo name and rewritten ssh url
    """
    parsed_url = urllib.parse.urlparse(url)
    if parsed_url.scheme != "https":
        raise j.exceptions.Input("not a https url: {}".format(url))
    return "git@{}:{}.git".format(parsed_url.netloc, parsed_url.path.lstrip("/"))


def rewrite_git_ssh_url_to_https(url, login=None, passwd=None):
    """
    :param url: (str) ssh url to rewrite ass https
    :param login: (str) authentication login name
    :param passwd: (str) authentication login password
    :return (tuple) repo name and rewritten https url
    """
    match = re.match(SSH_URL_MATCH, url)
    url_data = match.groupdict()
    if not match:
        raise j.exceptions.Input("not a ssh url: {}".format(url))
    if (login or passwd) and not (login and passwd):
        raise j.exceptions.Input("Need to specify both login and passwd if either one is specified")
    elif login and passwd:
        rewrite_url = "https://{login}:{passwd}@{netloc}/{path}".format(**match.groupdict(), login=login, passwd=passwd)
    else:
        rewrite_url = "https://{netloc}/{path}".format(**url_data)
    return rewrite_url


def ensure_repo(url: str, dest="", branch_or_tag="", commit_id="", discard_changes=False, depth=0):
    """Makes sure that repo exists in specified dest with correct branch

    Args:
        url (str): url of the repo
        dest (str, optional): the repo path, if it doesn't exist will clone it. Will get path from url if not specified.
        branch_or_tag (str, optional): clone from a specific branch or tag. Defaults to "".
        commit_id (str, optional): commit to checkout to. Defaults to "".
        discard_changes (bool, optional): Will remove changes in repo if True during pull. Defaults to False.
        depth (int, optional): specify the depth of the clone. Defaults to 0.
    """
    dest = dest or get_path_from_url(url)
    if j.sals.fs.exists(dest):
        revision = branch_or_tag or commit_id
        pull_repo(dest, discard_changes, revision)
    else:
        parent_dir = str(j.sals.fs.parent(dest))
        clone_repo(url, parent_dir, branch_or_tag, depth)
    return dest


def clone_repo(url: str, dest: str, branch_or_tag="", depth=0, commit_id=""):
    """Clones repo with sepcified url at specified dest

    Args:
        url (str): url of the repo
        dest (str): destination to clone in
        branch_or_tag (str, optional): clone from a specific branch or tag. Defaults to "".
        depth (int, optional): specify the depth of the clone. Defaults to 0.
        commit_id (int, optional): commit to checkout to. Defauls to "".
    """
    j.sals.fs.mkdirs(dest)
    prefix = f"cd {dest} && "
    cmd = prefix + f"git clone --single-branch {url}"
    if branch_or_tag:
        cmd += f" -b {branch_or_tag}"
    if depth != 0:
        cmd += f" --depth={depth}"
    rc, _, err = j.core.executors.run_local(cmd, warn=True)
    if rc > 0:
        raise j.exceptions.Runtime(f"Error in execute {cmd}\n{err}")
    repo_name = j.sals.fs.basename(url).split(".git")[0]
    if commit_id:
        prefix = f"cd {dest}/{repo_name} && "
        checkout_cmd = prefix + f"git checkout {commit_id}"
        rc, _, err = j.core.executors.run_local(checkout_cmd, warn=True)
        if rc > 0:
            raise j.exceptions.Runtime(f"Error in execute {checkout_cmd}\n{err}")
    return repo_name


def pull_repo(path: str, discard_changes=False, revision=""):
    """Pull repo at the given path

    Args:
        path (str): path of the git repo to pull.
        discard_changes (bool, optional): Will remove changes in repo if True. Defaults to False.
        revision (str, optional): change to specified branch, tag, commit. Defaults to "".
    """
    prefix = f"cd {path} && "
    if discard_changes:
        j.core.executors.run_local(prefix + "git checkout .")
    j.core.executors.run_local(prefix + "git pull")
    if revision:
        j.core.executors.run_local(prefix + f"git checkout {revision}")


def giturl_parse(url):
    """
    :return
    - repository_url the full url to the repo but rewritten
    - relpath: path inside the git repo
    - branch: branch specified in the url

    example Input
    - https://github.com/threefoldtech/jumpscale_/NOS/blob/master/specs/NOS_1.0.0.md
    - https://github.com/threefoldtech/jumpscale_/jumpscaleX_core/blob/8.1.2/lib/Jumpscale/tools/docsite/macros/dot.py
    - https://github.com/threefoldtech/jumpscale_/jumpscaleX_core/tree/8.2.0/lib/Jumpscale/tools/docsite/macros
    - https://github.com/threefoldtech/jumpscale_/jumpscaleX_core/tree/master/lib/Jumpscale/tools/docsite/macros

    """
    url_end = None
    branch = path = ""
    if "tree" in url:
        url, url_end = url.split("tree")
    elif "blob" in url:
        url, url_end = url.split("blob")
    if url_end is not None:
        url_end = url_end.strip("/")
        if url_end.find("/") == -1:
            path = ""
            branch = url_end
            if branch.endswith(".git"):
                branch = branch[:-4]
        else:
            branch, path = url_end.split("/", 1)
            if path.endswith(".git"):
                path = path[:-4]

    return url, path, branch


def get_path_from_url(url: str):
    """returns repo path in the filesystem based on the urk

    Args:
        url (str): repo url
    """

    def _get_path(netloc, path):
        return f"{j.core.dirs.CODEDIR}/{netloc.split('.')[0]}/{path.split('.git')[0]}"

    match = re.match(SSH_URL_MATCH, url)
    if match:
        url_data = match.groupdict()
        path = _get_path(**url_data)
    else:
        url = giturl_parse(url)[0]
        parsed_url = urllib.parse.urlparse(url)
        path = _get_path(parsed_url.netloc, parsed_url.path)
    return path


def find(account="", name=""):
    """find all repo paths in j.core.dirs.CODEDIR

    Args:
        account (str, optional): returns repos under this account only. Defaults to "".
        name (str, optional): retuns repos with this name only. Defaults to "".

    Returns:
        list: list of repos path
    """
    if name:
        name += "/.git"

    def _filter_paths(path):
        if f"{account}/{name}" in str(path):
            return True
        else:
            return False

    return [
        j.sals.fs.parent(path) for path in j.sals.fs.walk(j.core.dirs.CODEDIR, pat="*.git", filter_fun=_filter_paths)
    ]


def find_git_path(path, die=True):
    """
    given a path, check if this path or any of its parents is a git repo, return the first git repo
    :param path: (String) path from where to start search
    :returns (String) the first path which is a git repo
    :raises Exception when no git path can be found
    """
    while path != "":
        if j.sal.fs.exists(path=j.sal.fs.joinPaths(path, ".git")):
            return path
        path = j.sal.fs.getParent(path)
    if die:
        raise j.exceptions.Input("Cannot find git path in:%s" % path)
