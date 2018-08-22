import json

from washer.worker.actions import AppendStdout, AppendStderr
from washer.worker.actions import CreateNamedLog, AppendToLog
from washer.worker.actions import SetProperty
from washer.worker.commands import washertask


def pipenv_graph2deps(rawgraph):
    graph = json.loads(rawgraph)

    def build_entry(data):
        if 'required_version' in data:
            spec = data['key'] + data['required_version']
        else:
            spec = data['key']

        return {'installer': 'pipenv',
                'spec': spec,
                'source': 'pypi',
                'name': data['package_name'],
                'version': data['installed_version']}

    def extract_dependencies(entries):
        for entry in entries:
            if 'package' in entry:
                package = entry['package']
                dependencies = entry.get('dependencies', [])
                yield build_entry(package)
                yield from extract_dependencies(dependencies)
            else:
                yield build_entry(entry)

    yield from extract_dependencies(graph)


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
    yield SetProperty("dependencies", list(pipenv_graph2deps(deps.stdout)))

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
    yield SetProperty("dependencies", list(pipenv_graph2deps(deps.stdout)))

    return True
