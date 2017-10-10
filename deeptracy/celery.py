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
Module for deeptracy
"""
from celery import Celery
from deeptracy.config import BROKER_URI
from deeptracy_core.dal.database import db
from deeptracy.plugin_store import plugin_store

db.init_engine()  # Init database engine
plugin_store.load_plugins()  # Load analyzer plugins


# SETUP AND CREATE CELERY APP
celery = Celery('deeptracy',
                broker=BROKER_URI,
                backend=BROKER_URI,
                include=[
                    'deeptracy.tasks.start_scan',
                    'deeptracy.tasks.run_analyzer',
                    'deeptracy.tasks.merge_results'
                ])
