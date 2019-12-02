"""
This module contains the vulnerability providers.

"""
# pylint: disable=no-member,no-else-return
import collections
import fnmatch
import functools
import requests

from playhouse.shortcuts import model_to_dict
import celery

from deeptracy import Config
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
    providers_by_artifact = get_providers_for_artifacts(artifacts)
    grouped_providers = group_artifacts_by_provider(providers_by_artifact)

    # group(provider1.s([artifact1{asdict}, artifact3{asdict}]),
    #       provider2.s([artifact1{asdict}, artifact2{asdict}]),
    #       provider3.s([artifact3{asdict}]))
    return celery.group(
        (provider.s([model_to_dict(a) for a in artifacts])
         for provider, artifacts
         in grouped_providers.items()))


def get_providers_for_artifacts(artifacts):
    """
    Return a set of providers for each given artifact.

    Given::

        [artifact1, artifact2, artifact3]

    Returns::

        [(artifact1, (provider1, provider2)),
         (artifact2, (provider2)),
         (artifact3, (provider1, provider3))]

    """
    for artifact in artifacts:
        yield (artifact, providers_for_source(artifact.source))


def group_artifacts_by_provider(artifacts_with_providers):
    """
    Return a dictionary with providers as keys and the set of artifact to check
    for each one.

    Given::

        [(artifact1, (provider1, provider2)),
         (artifact2, (provider2)),
         (artifact3, (provider1, provider3))]

    Returns::

        {provider1: {artifact1, artifact3},
         provider2: {artifact1, artifact2},
         provider3: {artifact3}}

    """
    def _group_by_provider(acc, entry):
        artifact, providers = entry
        for cprov in providers:
            acc[cprov].add(artifact)
        return acc

    return functools.reduce(
        _group_by_provider,
        artifacts_with_providers,
        collections.defaultdict(set))


def provider(pattern, enabled=True):
    """
    Decorator to register new providers by pattern.

    """
    def _provider(func):
        task = app.task(func)
        if enabled:
            PROVIDERS[pattern].add(task)
        return task
    return _provider


def providers_for_source(source):
    """
    Return the set of provider matching the given source.

    """
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
        json={"method": method,
              "libraries": [{"library": dependency['name'],
                             "version": dependency['version']}
                            for dependency in dependencies]},
        timeout=10)

    if response.status_code != 200:
        print("Something went wrong!", response.status_code, response.text)
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


@provider("pypi", enabled=bool(Config.PATTON_HOST))
def patton_python_provider(dependencies):
    """Pypi source is scanned with patton method `python`."""
    patton("python", dependencies)


@provider("npm")
def patton_npm_provider(dependencies, enabled=bool(Config.PATTON_HOST)):
    """NPM source is scanned with patton method `simple_parser`."""
    patton("simple_parser", dependencies)


@provider("pypi", enabled=WITH_SAFETY_LIB)
def safety_provider(dependencies):
    """Pypi source is scanned with `safety`."""
    for dependency in dependencies:
        packages = [safetyutil.Package(key=dependency['name'],
                                       version=dependency['version'])]
        vulns = safety.check(packages=packages,
                             key=Config.SAFETY_API_KEY,
                             db_mirror='',
                             cached=False,
                             ignore_ids=[],
                             proxy=None)
        for vuln in vulns:
            Vulnerability.get_or_create(
                artifact=dependency['id'],
                provider="safety",
                reference=vuln.vuln_id,
                details=vuln._asdict())
