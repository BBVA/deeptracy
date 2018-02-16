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

from unittest import TestCase, mock
from unittest.mock import ANY

from deeptracy.tasks.base_task import DeeptracyTask


class TestBaseTask(TestCase):

    @mock.patch('deeptracy.tasks.base_task.logger')
    def test_base_task_on_failure(self, mock_logger):
        """After initialization metadata should create all models"""
        base_task = DeeptracyTask()
        # on_failure(self, exc, task_id, args, kwargs, einfo):
        exc = ValueError('test_base_task_on_failure')
        base_task.on_failure(exc, 'task_id', None, None, None)

        self.assertTrue(mock_logger.exception.called)
        mock_logger.exception.assert_called_with(ANY, exc_info=exc)
