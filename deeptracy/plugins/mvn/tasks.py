import json
import re

from washer.worker.actions import AppendStdout, AppendStderr
from washer.worker.actions import CreateNamedLog, AppendToLog
from washer.worker.actions import SetProperty
from washer.worker.commands import washertask


def mvntgf2deps(rawgraph):
    # 65982709 org.springframework:spring-expression:jar:4.3.13.RELEASE:compile
    exp = re.compile((r'^\d+\s'
                      r'(?P<group_id>[^:]+):'
                      r'(?P<artifact_id>[^:]+):'
                      r'[^:]+:'
                      r'(?P<version>[^:]+):'
                      r'[^:]+$'))
    for line in rawgraph.splitlines():
        if line == '#\n':  # End of node definitions
            break
        else:
            match=exp.match(line)
            if match:
                name = ":".join([match.group('group_id'), 
                               match.group('artifact_id')])
                yield {'installer': 'mvn',
                       'spec': line.split()[1],
                       'source': 'central.maven.org',
                       'name': name,
                       'version': match.group('version')}


@washertask
def mvn_dependencytree(repopath, path=".", **kwargs):
    import invoke
    c = invoke.Context()

    with c.cd(repopath):
        with c.cd(path):
            deps = c.run(("mvn dependency:tree"
                          " -Doutput=/tmp/mvndeps.json"
                          " -DoutputType=tgf"),
                         warn=True)

    yield AppendStdout(deps.stdout)
    yield AppendStderr(deps.stderr)
    with open("/tmp/mvndeps.json", "r") as f:
        yield SetProperty("dependencies",
                          list(mvntgf2deps(f.read())))

    return True
