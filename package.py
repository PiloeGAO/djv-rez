name = "djv"

version = "2.0.8"

authors = ["Barby Johnston", "Leo Depoix (@piloegao)"]

description = """
    A DJV rez package using the pre-build version.
    """

requires = ["python"]

uuid = "darbyjohnston.djv"

build_command = "python {root}/build.py {install}"


def commands():
    version_suffix = this.version.major if this.version.major > 1 else ""
    executables = {
        "windows": {
            "djv": "bin/djv.exe",
        },
        "osx": {"djv": f"DJV{version_suffix}.app/Contents/MacOS/DJV{version_suffix}"},
        "linux": {},
    }

    for exec_command, executable_file in executables.get(system.platform).items():
        alias(exec_command, "{root}/djv/%s" % executable_file)
