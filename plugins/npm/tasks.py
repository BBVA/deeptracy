import json

from washer.worker.actions import AppendStdout, AppendStderr
from washer.worker.actions import CreateNamedLog, AppendToLog
from washer.worker.actions import SetProperty
from washer.worker.commands import washertask


def npmjson2deps(rawgraph):
    graph = json.loads(rawgraph)

    def extract_dependencies(entries):
        for package_name, entry in entries.items():
            try:
                yield {'installer': 'npm',
                       'spec': entry['from'],
                       'source': entry.get('resolved', 'npm'),
                       'name': package_name,
                       'version': entry['version']}
            except KeyError as exc:
                print("Cannot get mandatory field %s" % exc)
            if 'dependencies' in entry:
                yield from extract_dependencies(entry['dependencies'])

    if 'dependencies' in graph:
        yield from extract_dependencies(graph['dependencies'])


@washertask
def npm_install(repopath, path=".", **kwargs):
    import invoke
    c = invoke.Context()

    with c.cd(repopath):
        with c.cd(path):
            res = c.run("npm install", warn=True)
            # Dump the output to a file to avoid 
            # https://github.com/npm/npm/issues/17331
            deps = c.run("npm ls --json > /tmp/npmdeps.json", warn=True)

    yield AppendStdout(res.stdout)
    yield AppendStderr(res.stderr)
    with open("/tmp/npmdeps.json", "r", encoding='utf-8') as f:
        yield SetProperty("dependencies",
                          list(npmjson2deps(f.read())))

    return True
