import collections
import datetime
import fnmatch
import json
import requests
import time

import decorator
import scalpl

from deeptracy import Config
from deeptracy import model
from deeptracy.model import InstalledDependency
from deeptracy.model import VulnerableDependencies

import logging

# These two lines enable debugging at httplib level
# (requests->urllib3->http.client)
# You will see the REQUEST, including HEADERS and DATA, and RESPONSE with
# HEADERS but without DATA.
# The only thing missing will be the response.body which is not logged.
try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client
    http_client.HTTPConnection.debuglevel = 1

# You must initialize logging, otherwise you'll not see debug output.
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True


PROVIDERS = collections.defaultdict(set)  # {inst: {prov1, prov2}}


def analyze_dependency(dependency_id):
    with Config.DATABASE:
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


def patton(method, dependency_id):
    with Config.DATABASE:
        dependency = InstalledDependency.get(id=dependency_id)

        response = requests.post(
            f"http://{Config.PATTON_HOST}/api/v1/check-dependencies?cpeDetailed=1",
            json={"method": "python",
                  "libraries": [{"library": dependency.package_name,
                                 "version": dependency.version}]})

        if response.status_code != 200:
            print("Something went wrong!", response.staus_code, response.text)
            return
        else:
            try:
                cpes, *_ = list(response.json().values())
                vulns = 0
                for cpe in cpes["cpes"]:
                    for cve in cpe.get("cves", []):
                        vulns += 1
                        print("lalala", cve['cve'])
                        VulnerableDependencies.get_or_create(
                            dependency=dependency,
                            provider="patton",
                            ref=cve['cve'],
                            details=json.dumps(dict(cve)))
                        dependency
            except Exception as exc:
                print("Error parsing result", exc)
            else:
                print("Finish, %d vulns inserted" % vulns)


@provider("deeptracy-python:*")
def patton_python(dependency_id):
    patton("python", dependency_id)
