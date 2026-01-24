import datetime as dt
import logging
import shlex
import subprocess

import pytest
import pytz

logger = logging.getLogger(__name__)

@pytest.fixture
def run(capfd):

    def run_command(command, more_options=""):
        command = "{command} {more_options}".format(command=command, more_options=more_options)
        subprocess.check_call(shlex.split(command))
        return capfd.readouterr()

    return run_command


@pytest.fixture
def timestamp_iso():
    now = dt.datetime.now(tz=pytz.timezone("Europe/Berlin"))
    now = now - dt.timedelta(microseconds=now.microsecond)
    return now.isoformat()


@pytest.fixture(autouse=True)
def prosody_register_user(run):
    try:
        run("docker compose --file=tests/compose.yml exec prosody prosodyctl register testdrive localhost secret")
    except subprocess.CalledProcessError:
        logger.error("Failed to register XMPP user. Subsequent tests will likely fail. Is Prosody running?")
