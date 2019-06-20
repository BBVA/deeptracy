import json
import re

from washer.worker.actions import AppendStdout, AppendStderr
from washer.worker.actions import CreateNamedLog, AppendToLog
from washer.worker.actions import SetProperty
from washer.worker.commands import washertask

# Bigger size limit to allow whole results to be transmitted from the workers.
# TODO: Split big messages into chunks instead of raising this limit
from twisted.spread import banana
banana.SIZE_LIMIT *= 10


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
def mvn_dependencytree(repopath, path=".", maven_config=None, **kwargs):
    import invoke
    import tempfile

    c = invoke.Context()

    with c.cd(repopath):
        with c.cd(path):
            if maven_config is not None:
                maven_config_path = tempfile.mkstemp()

                with open(maven_config_path[1], mode="w") as config:
                    config.write(maven_config)
                deps = c.run(("mvn dependency:tree"
                              " -DoutputFile=/tmp/mvndeps.tgf"
                              " -DoutputType=tgf"
                              " -s ") + maven_config_path[1],
                             warn=True)
            else:
                deps = c.run(("mvn dependency:tree"
                              " -DoutputFile=/tmp/mvndeps.tgf"
                              " -DoutputType=tgf"),
                             warn=True)

    for line in deps.stdout.splitlines():
        yield AppendStdout(line)

    for line in deps.stderr.splitlines():
        yield AppendStderr(line)

    with open("/tmp/mvndeps.tgf", "r") as f:
        yield SetProperty("dependencies",
                          list(mvntgf2deps(f.read())))

    return True
