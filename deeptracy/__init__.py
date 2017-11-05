# Copyright 2017 BBVA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Deeptracy Workers Project.

This package contains celery workers and tasks to process the deeptracy flow for scanning projects.
"""

import logging

from .config import LOG_LEVEL

__version__ = '0.0.7'


logger = logging.getLogger('deeptracy')
logger.setLevel(LOG_LEVEL)
logger.addHandler(logging.StreamHandler())
