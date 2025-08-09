import datetime as dt
import shlex
import subprocess

import pytest
import pytz


@pytest.fixture
def run(capfd):

    def run_command(command, more_options=""):
        command = f'{command} {more_options}'
        subprocess.check_call(shlex.split(command))
        return capfd.readouterr()

    return run_command


@pytest.fixture
def timestamp_iso() -> str:
    now = dt.datetime.now(tz=pytz.timezone("Europe/Berlin"))
    now = now - dt.timedelta(microseconds=now.microsecond)
    return now.isoformat()


@pytest.fixture(autouse=True)
def prosody_register_user(run):
    run("docker compose --file=tests/compose.yml exec prosody prosodyctl register testdrive localhost secret")
