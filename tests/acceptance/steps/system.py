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

import os
import shutil

from behave import given
from sqlalchemy import text

from deeptracy_core.dal.database import db


@given(u'a clean system')
def step_impl(context):
    db.init_engine(db_uri=os.environ['DATABASE_URI'])
    clean_directory(context.SHARED_VOLUME_PATH)

    sql = text('DELETE FROM vulnerabilities_in_scans')
    context.engine.execute(sql)

    sql = text('DELETE FROM vulnerability')
    context.engine.execute(sql)

    sql = text('DELETE FROM scan_vulnerability')
    context.engine.execute(sql)

    sql = text('DELETE FROM scan_dep')
    context.engine.execute(sql)

    sql = text('DELETE FROM scan')
    context.engine.execute(sql)

    sql = text('DELETE FROM project')
    context.engine.execute(sql)

    context.redis_db.delete('celery')


def clean_directory(folder: str):
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)
