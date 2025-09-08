import os
import tarfile
import zipfile

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

DAT_MESSAGE = """
======
Package should contain babel/global.dat and multiple locale .dat files.
* Make sure you've imported the CLDR data; `make import-cldr`.
------
To skip this check, set the environment variable BABEL_NO_CHECK_BUILD=1
======
""".strip()


def check_babel_artifact(artifact_path: str):
    if artifact_path.endswith(".whl"):
        with zipfile.ZipFile(artifact_path) as whl:
            filelist = whl.namelist()
    elif artifact_path.endswith(".tar.gz"):
        with tarfile.open(artifact_path) as tar:
            filelist = tar.getnames()
    dat_files = [f for f in filelist if f.endswith(".dat")]
    if len(dat_files) < 10 or not any(f.endswith("babel/global.dat") for f in dat_files):
        raise ValueError(DAT_MESSAGE)


class CustomBuildHook(BuildHookInterface):
    def finalize(self, version, build_data, artifact_path):
        if version == "editable":
            return
        if not os.environ.get("BABEL_NO_CHECK_BUILD"):
            check_babel_artifact(artifact_path)
