# -*- coding: utf-8 -*-

import os
import re

from typing import List, Dict

from deeptracy.plugins.store import deeptracy_plugin

REGEX_SEVERITY = r'''(severity[\s]*:[\s]*)([\w]+)(;)'''
DOCKER_IMAGE = 'deeptracy/retirejs'
OUTPUT_FILE = 'retirejs_task.txt'


@deeptracy_plugin("nodejs")
def retirejs_task(source_code_location: str) -> List[Dict]:

    output_path = os.path.join(source_code_location, OUTPUT_FILE)
    os.chdir(source_code_location)
    os.system('docker run -v $(pwd):/opt/app -e OUTPUT_FILE={} {}'
              .format(OUTPUT_FILE, DOCKER_IMAGE))

    f = open(output_path, "r").readlines()

    results = []

    for x in f:
        if "has known vulnerabilities" in x:
            # Find the start of string
            for i, y in enumerate(x):
                if y.isalnum():
                    break

            line = x[i:]

            library, version, _ = line.split(" ", maxsplit=2)
            try:
                severity = re.search(REGEX_SEVERITY, line).group(2)
            except AttributeError:
                severity = "unknown"

            if "summary:" in x:
                start = x.find("summary") + len("summary:")
            elif "advisory:":
                start = x.find("advisory") + len("advisory:")
            else:
                start = 0
            summary = x[start:].replace("\n", '').strip()
            if not summary:
                summary = "Unknown"

            results.append(dict(library=library,
                                version=version,
                                severity=severity,
                                summary=summary,
                                advisory=''))
    return results
