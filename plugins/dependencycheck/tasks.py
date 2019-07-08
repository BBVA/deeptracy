import json
import os
import re

from washer.worker.actions import AppendStdout, AppendStderr
from washer.worker.actions import CreateNamedLog, AppendToLog
from washer.worker.actions import SetProperty
from washer.worker.commands import washertask

# jq '.dependencies[0].vulnerabilities[0] | [.name, .description, .source]' dependency-check-report.json
# jq '. | keys' dependency-check-report.json

def select_maven_identifier(identifiers):
    # Get the maven identifier
    for identifier in identifiers:
        if identifier.get('type', None) == 'maven':
            return identifier


def installation_from_identifier(identifier):
    try:
        spec = identifier['name']
        groupid, artifactid, version = spec.split(':')
        name = f'{groupid}:{artifactid}'
        installation = {'installer': identifier['type'],
                        'spec': spec,
                        'source': 'central',  # ???
                        'name': name,
                        'version': version}
    except Exception as exc:
        # TODO: Proper logging
        return None
    else:
        return installation


def odc_dependencies(report):
    dependencies = report.get('dependencies', [])
    for dependency in dependencies:
        identifier = select_maven_identifier(dependency.get('identifiers', []))
        installation = installation_from_identifier(identifier)
        if installation is not None:
            yield installation


def odc_vulnerabilities(report):
    dependencies = report.get('dependencies', [])
    for dependency in dependencies:
        identifier = select_maven_identifier(dependency.get('identifiers', []))
        vulnerabilities = dependency.get('vulnerabilities', [])
        installation = installation_from_identifier(identifier)
        if installation and vulnerabilities:
            for vulnerability in vulnerabilities:
                yield {'provider': 'owasp-dependency-check',
                       'reference': vulnerability['name'],
                       'details': vulnerability,
                       'installation': installation}


@washertask
def dependency_check(repopath, path=".", maven_config=None, **kwargs):
    import invoke
    import tempfile

    c = invoke.Context()

    if maven_config is not None:
        maven_config_path = tempfile.mkstemp()

        with open(maven_config_path[1], mode="w") as config:
            config.write(maven_config)

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
        yield SetProperty("vulnerabilities", list(odc_vulnerabilities(report)))

    return True
