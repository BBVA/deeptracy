import json
import re

from washer.worker.actions import AppendStdout, AppendStderr
from washer.worker.actions import CreateNamedLog, AppendToLog
from washer.worker.actions import SetProperty
from washer.worker.commands import washertask


def odc_dependencies(report):
    pass


def odc_vulnerabilities(report):
    pass


@washertask
def dependency_check(repopath, path=".", **kwargs):
    import invoke
    c = invoke.Context()

    project_path = os.path.join(repopath, path)
    scan = c.run((f"./bin/dependency-check.sh "
           f"-d /usr/share/dependency-check/notavolume "
           f"--project deeptracyscan "
           f"--scan {project_path} "
           f"-f JSON -o /tmp "))

    yield AppendStdout(scan.stdout)
    yield AppendStderr(scan.stderr)

    with open("/tmp/dependency-check-report.json", "r") as f:
        report = json.load(f)
        yield SetProperty("dependencies", odc_dependencies(report))
        yield SetProperty("vulnerabilities", odc_vulnerabilities(report))

    return True
