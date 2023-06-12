import subprocess
import time

import pytest


@pytest.fixture
def app():
    with open("/logs/service.log", "a") as log:
        service = subprocess.Popen(
            ["/usr/local/bin/python", "-m" "app"],
            cwd="/",
            stdout=log,
            stderr=log,
        )
        time.sleep(1)

        yield

        service.terminate()
        service.wait()
