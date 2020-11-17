import shlex
import hfval
import time


def test_version(script_runner):
    command = "pyhf-validation --version"
    # Run once to ensure first time setup doesn't slow down
    script_runner.run(*shlex.split(command))
    start = time.time()
    ret = script_runner.run(*shlex.split(command))
    end = time.time()
    elapsed = end - start
    assert ret.success
    assert hfval.__version__ in ret.stdout
    assert ret.stderr == ""
    # make sure it took less than a second
    assert elapsed < 1.0
