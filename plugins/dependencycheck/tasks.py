import json
import os
import re

from washer.worker.actions import AppendStdout, AppendStderr
from washer.worker.actions import CreateNamedLog, AppendToLog
from washer.worker.actions import SetProperty
from washer.worker.commands import washertask


def odc_dependencies(report):
    def select_maven_identifier(identifiers):
        # Get the maven identifier
        for identifier in identifiers:
            if identifier.get('type', None) == 'maven':
                return identifier

    def split_name(name):
        # Will raise ValueError if the number of fields doesn't match
        # unpacking.
        groupid, artifactid, version = name.split(':')
        return f'{groupid}:{artifact}', version

    dependencies = report.get('dependencies', [])
    for dependency in dependencies:
        identifier = select_maven_identifier(dependency)
        if identifier is not None:
            try:
                name, version = split_name(identifier['name'])
            except ValueError:
                continue
            else:
                yield {'installer': identifier['type'],
                       'spec': identifier['name'],
                       'source': 'central',  # ???
                       'name': name,
                       'version': version}


def odc_vulnerabilities(report):
    pass


@washertask
def dependency_check(repopath, path=".", **kwargs):
    import invoke
    c = invoke.Context()

    project_path = os.path.join(repopath, path)
    scan = c.run((f"/usr/share/dependency-check/bin/dependency-check.sh "
                  f"-d /usr/share/dependency-check/notavolume "
                  f"--project DEEPTRACY_SCAN "
                  f"--noupdate "
                  f"--scan {project_path} "
                  f"-f JSON -o /tmp "))

    yield AppendStdout(scan.stdout)
    yield AppendStderr(scan.stderr)

    with open("/tmp/dependency-check-report.json", "r") as f:
        report = json.load(f)
        yield SetProperty("dependencies", list(odc_dependencies(report)))
    #    yield SetProperty("vulnerabilities", odc_vulnerabilities(report))

    return True
