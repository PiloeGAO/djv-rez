import os
import platform
import shutil
import subprocess
import sys
import urllib.request
import zipfile

DOWNLOAD_URL = "https://sourceforge.net/projects/djv/files/djv-{release_type}/{MAJOR}.{MINOR}.{PATCH}/{filename}/download"

FILE_NAME = "DJV-{MAJOR}.{MINOR}.{PATCH}-{os}.{ext}"

DOWNLOAD_TYPES = {"win64": "zip", "Darwin": "dmg"}

BETA_VERSIONS = [
    "2.0.8",
    "2.0.7",
    "2.0.6",
    "2.0.5",
    "2.0.4",
    "2.0.3",
    "2.0.2",
    "2.0.1",
    "2.0.0",
    "1.2.8",
    "1.2.7",
]
"""Some versions of the tool are considered beta and hosted during a different URL."""


def get_os_information():
    """Get the os name and the architecture.

    Returns:
        tuple: OS name and architecture.
    """
    os_names = {
        "Windows": "win64",
        "Darwin": "Darwin",
    }
    os_platform = platform.system()

    return os_names.get(os_platform, "linux")


def build(source_path, build_path, install_path, targets):
    """Build/Install function.

    Args:
        source_path (str): Path to the rez package root.
        build_path (str): Path to the rez build directory.
        install_path (str): Path to the rez install directory.
        targets (str): Target run by the command, i.e. `build`, `install`...

    Raises:
        RuntimeError: Your current OS is not supported.
    """
    os_name = get_os_information()
    package_major, package_minor, package_patch = os.environ.get(
        "REZ_BUILD_PROJECT_VERSION", "0.0.0"
    ).split(".")
    version_suffix = "" if package_major == 1 else package_major

    release_type = "stable"
    if os.environ.get("REZ_BUILD_PROJECT_VERSION", "0.0.0") in BETA_VERSIONS:
        release_type = "beta"

    if os_name == "linux":
        raise RuntimeError(f"Your current OS is not supported ({os_name}).")

    djv_archive = FILE_NAME.format(
        MAJOR=package_major,
        MINOR=package_minor,
        PATCH=package_patch,
        os=os_name,
        ext=DOWNLOAD_TYPES.get(os_name),
    )
    download_url = DOWNLOAD_URL.format(
        MAJOR=package_major,
        MINOR=package_minor,
        PATCH=package_patch,
        release_type=release_type,
        filename=djv_archive,
    )

    # MacOS specific filename.
    mac_os_app_filename = f"DJV{version_suffix}.app"

    def _build():
        """Build the package locally."""
        archive_path = os.path.join(build_path, djv_archive)

        if not os.path.isfile(archive_path):
            print(f"Downloading DJV archive from: {download_url}")
            with open(archive_path, "wb") as file:
                with urllib.request.urlopen(download_url) as request:
                    file.write(request.read())

        print("Extracting the archive.")
        match os_name:
            case "win64":
                with zipfile.ZipFile(archive_path) as archive_file:
                    archive_file.extractall(build_path)
            case "Darwin":
                mac_mountpoint = os.path.join(
                    "/Volumes", os.path.splitext(djv_archive)[0]
                )

                subprocess.run(["hdiutil", "attach", archive_path])
                shutil.copytree(
                    os.path.join(mac_mountpoint, mac_os_app_filename),
                    os.path.join(build_path, mac_os_app_filename),
                )
                subprocess.run(["hdiutil", "detach", mac_mountpoint])
            case _:
                pass

    def _install():
        """Install the package."""
        print("Installing the package.")
        extracted_archive_path = os.path.join(
            build_path, os.path.splitext(djv_archive)[0]
        )
        install_directory = os.path.join(install_path, "djv")

        if os.path.isdir(install_directory):
            shutil.rmtree(install_directory)
        os.mkdir(install_directory)

        match os_name:
            case "win64":
                for element in os.listdir(extracted_archive_path):
                    element_path = os.path.join(extracted_archive_path, element)
                    shutil.move(element_path, install_directory)
            case "Darwin":
                shutil.move(
                    os.path.join(build_path, mac_os_app_filename),
                    os.path.join(install_directory, mac_os_app_filename),
                )
            case _:
                pass

    _build()

    if "install" in (targets or []):
        _install()


if __name__ == "__main__":
    build(
        source_path=os.environ["REZ_BUILD_SOURCE_PATH"],
        build_path=os.environ["REZ_BUILD_PATH"],
        install_path=os.environ["REZ_BUILD_INSTALL_PATH"],
        targets=sys.argv[1:],
    )
