import collections
import datetime
import fnmatch
import functools
import json
import requests
import time

from playhouse.shortcuts import model_to_dict
import celery

from deeptracy import Config
from deeptracy import model
from deeptracy.model import Analysis
from deeptracy.model import Artifact
from deeptracy.model import Vulnerability
from deeptracy.tasks import app


try:
    from safety import safety
    import safety.util as safetyutil
except ImportError:
    WITH_SAFETY_LIB = False
else:
    WITH_SAFETY_LIB = True


PROVIDERS = collections.defaultdict(set)  # {inst: {prov1, prov2}}


def analyze_artifacts(artifacts):
    """
    Given a list of `Artifact` objects return a Celery group to analyze them.

    """
    def group_by_provider(acc, entry):
        artifact, providers = entry
        for provider in providers:
            acc[provider].add(artifact)
        return acc

    # [(artifact1, (provider1, provider2)),
    #  (artifact2, (provider2)),
    #  (artifact3, (provider1, provider3))]
    providers_by_artifact = get_providers_for_artifacts(artifacts)

    # {provider1: {artifact1, artifact3},
    #  provider2: {artifact1, artifact2},
    #  provider3: {artifact3}}
    grouped_providers = functools.reduce(
        group_by_provider,
        providers_by_artifact,
        collections.defaultdict(set))

    # group(provider1.s([artifact1{asdict}, artifact3{asdict}]),
    #       provider2.s([artifact1{asdict}, artifact2{asdict}]),
    #       provider3.s([artifact3{asdict}]))
    return celery.group(
        (provider.s([model_to_dict(a) for a in artifacts])
         for provider, artifacts
         in grouped_providers.items()))


def get_providers_for_artifacts(artifacts):
    for artifact in artifacts:
        yield (artifact, providers_for_source(artifact.source))


def provider(pattern, enabled=True, **kwargs):
    def _provider(f):
        task = app.task(f)
        if enabled:
            PROVIDERS[pattern].add(task)
        return task
    return _provider


def providers_for_source(source):
    providers = set()
    for pattern, fns in PROVIDERS.items():
        if fnmatch.fnmatch(source, pattern):
            providers |= fns
    return providers


def patton(method, dependencies):
    """Analyze `dependency_id` using patton `method`."""

    response = requests.post(
        (f"http://{Config.PATTON_HOST}/api/v1/"
         f"check-dependencies?cpeDetailed=1"),
        json={"method": "python",
              "libraries": [{"library": dependency['name'],
                             "version": dependency['version']}
                            for dependency in dependencies]},
        timeout=10)

    if response.status_code != 200:
        print("Something went wrong!", response.staus_code, response.text)
        return
    else:
        vulns = response.json()
        for dep in dependencies:
            cpes = vulns.get(f"{dep['name'].lower()}:{dep['version']}", None)
            if cpes is not None:
                for cpe in cpes["cpes"]:
                    for cve in cpe.get("cves", []):
                        Vulnerability.get_or_create(
                            artifact=dep['id'],
                            provider="patton",
                            reference=cve['cve'],
                            details=dict(cve))


@provider("pypi")
def patton_python_provider(dependencies):
    patton("python", dependencies)


@provider("npm")
def patton_npm_provider(dependencies):
    patton("simple_parser", dependencies)


@provider("pypi", enabled=WITH_SAFETY_LIB)
def safety_provider(dependencies):
    for dependency in dependencies:
        packages = [safetyutil.Package(key=dependency['name'],
                                       version=dependency['version'])]
        vulns = safety.check(packages=packages,
                             key=Config.SAFETY_API_KEY,
                             db_mirror='',
                             cached=False,
                             ignore_ids=[])
        for vuln in vulns:
            Vulnerability.get_or_create(
                artifact=dependency['id'],
                provider="safety",
                reference=vuln.vuln_id,
                details=vuln._asdict())
