import collections
import datetime
import fnmatch
import time

import decorator

from deeptracy import Config
from deeptracy.model import InstalledDependency


PROVIDERS = collections.defaultdict(set)  # {inst: {prov1, prov2}}


def analyze_dependency(dependency_id):
    dependency = InstalledDependency.get(id=dependency_id)
    jobs = []
    for provider in providers_for_installer(dependency.installer):
        jobs.append(Config.QUEUE.enqueue(provider, dependency.id))

    while any([not j.is_finished for j in jobs]):
        time.sleep(1)

    dependency.last_checked = datetime.datetime.utcnow()
    dependency.save()


def provider(pattern):
    def _provider(f):
        PROVIDERS[pattern].add(f)
        return f
    return _provider


def providers_for_installer(installer):
    providers = set()
    for pattern, fns in PROVIDERS.items():
        if fnmatch.fnmatch(installer, pattern):
            providers |= fns
    return providers


@provider("*")
def patton(dependency):
    pass
