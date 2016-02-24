# Copyright 2016 Symantec, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import eventlet
import traceback
from dao.common import log
from dao.common import rpc
from dao.dhcp import isc


LOG = log.getLogger(__name__)
port = 5557


class Manager(rpc.RPCServer):
    """
    Class represents DHCP manager that servers two requests:
    1. Adding subnets
    2. Adding ipmi/mgmt ips to DHCP
    """
    def __init__(self):
        super(Manager, self).__init__(port)
        self.dhcp = isc.ISCController()
        self.reload_allocations()

    def update_networks(self):
        """
        Update subnets in DHCP configs and restart DHCP
        :return: None
        """
        self.reload_allocations()

    def reload_allocations(self):
        """
        """
        self.dhcp.reload_allocations()


def run():
    LOG.info('Started')
    try:
        eventlet.monkey_patch()
        manager = Manager()
        manager.do_main()
    except:
        LOG.warning(traceback.format_exc())
        raise
