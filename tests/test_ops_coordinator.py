# Copyright 2014-2021 Canonical Limited.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from datetime import datetime, timedelta
import unittest
from mock import call, patch

from ops_coordinator.base_coordinator import base_coordinator
from ops_coordinator import ops_coordinator as coordinator
from ops_coordinator.base_coordinator import hookenv


class TestOpsCoordinator(unittest.TestCase):

    def setUp(self):
        base_coordinator.Singleton._instances.clear()

    _last_utcnow = datetime(2015, 1, 1, 00, 00)

    def _utcnow(self, ts=base_coordinator._timestamp):
        self._last_utcnow += timedelta(minutes=1)
        return self._last_utcnow

    def test_is_singleton(self):
        self.assertTrue(base_coordinator.BaseCoordinator()
                        is base_coordinator.BaseCoordinator())
        self.assertTrue(base_coordinator.Serial() is base_coordinator.Serial())
        self.assertTrue(base_coordinator.Serial() is base_coordinator.Serial())
        self.assertTrue(coordinator.OpsCoordinator() is coordinator.OpsCoordinator())
        self.assertFalse(base_coordinator.BaseCoordinator() is base_coordinator.Serial())
        self.assertFalse(base_coordinator.BaseCoordinator() is coordinator.OpsCoordinator())

    @patch.object(hookenv, 'atstart')
    def test_implicit_initialize_and_handle(self, atstart):
        # When you construct a BaseCoordinator(), its initialize() and
        # handle() method are invoked automatically every hook. This
        # is done using hookenv.atstart
        c = base_coordinator.BaseCoordinator()
        atstart.assert_has_calls([call(c.initialize), call(c.handle)])
