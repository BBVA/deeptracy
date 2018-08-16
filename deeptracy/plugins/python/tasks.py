import json

from washer.worker.actions import AppendStdout, AppendStderr
from washer.worker.actions import CreateNamedLog, AppendToLog
from washer.worker.actions import SetProperty
from washer.worker.commands import washertask


@washertask
def pip_install(repopath, path=".", **kwargs):
    import invoke
    c = invoke.Context()

    with c.cd(repopath):
        with c.cd(path):
            res = c.run("pipenv install .")
            deps = c.run("pipenv graph --json")

    yield AppendStdout(res.stdout)
    yield AppendStderr(res.stderr)
    yield SetProperty("dependencies", json.loads(deps.stdout))

    return True


@washertask
def requirement_file(repopath, requirement="requirements.txt",
                     path=".", **kwargs):
    import invoke
    c = invoke.Context()

    with c.cd(repopath):
        with c.cd(path):
            res = c.run("pipenv install -r %s" % requirement)
            deps = c.run("pipenv graph --json")

    yield AppendStdout(res.stdout)
    yield AppendStderr(res.stderr)
    yield SetProperty("dependencies", json.loads(deps.stdout))

    return True
