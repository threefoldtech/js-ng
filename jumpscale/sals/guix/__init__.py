from jumpscale.god import j


def ensure_guix():
    pass


def check_for_guix():
    """Checks for existence of guix binary on system.

    Returns:
        (bool) -- True if exists, False otherwise.
    """
    rc, out, err = j.sals.process.execute("guix")
    if rc != 0:
        print(
            "Please install guix first http://guix.gnu.org/download/ or call ensure_guix. remember you need root permissions for that."
        )
        return False
    return True


def _guix_cmd(cmd):
    rc, out, err = j.sals.process.execute(cmd, showout=True, timeout=6000)
    if rc != 0:
        raise j.exceptions.Runtime(f"couldn't execute {cmd}\nout:{out}\nerr:{err}")
    return True


def pull():
    """Pulls guix channels.

    Returns:
        (bool) -- True on success or raises `j.exceptions.Runtime`
    """
    cmd = "guix pull"
    return _guix_cmd(cmd)


def upgrade():
    """upgrade guix packages.

    Returns:
        (bool) -- True on success or raises `j.exceptions.Runtime`
    """
    cmd = "guix upgrade"
    return _guix_cmd(cmd)


def install_package(pkg_name):
    """Installs a package `pkg_name`

    Returns:
        (bool) -- True on success or raises `j.exceptions.Runtime`
    """
    cmd = f"guix install {pkg_name}"
    return _guix_cmd(cmd)


add_package = install_package


def uninstall_package(pkg_name):
    """Uninstall a package `pkg_name`.

    Returns:
        (bool) -- True on success or raises `j.exceptions.Runtime`
    """
    cmd = f"guix remove {pkg_name}"
    return _guix_cmd(cmd)


delete_package = remove_package = uninstall_package


def search(pkg_name):
    """Searches for a package `pkg_name`

    Returns:
        (bool) -- True on success or raises `j.exceptions.Runtime`
    """
    cmd = f"guix search {pkg_name}"
    return _guix_cmd(cmd)


def cleanup_filesystem():
    """Cleans up previous generations to free up disk space.

    Returns:
        (bool) -- True on success or raises `j.exceptions.Runtime`
    """
    cmd = f"guix package --delete-generations"
    return _guix_cmd(cmd)


delete_generations = cleanup_filesystem
