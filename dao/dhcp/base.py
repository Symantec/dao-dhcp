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

import netaddr

from dao.common import config
from dao.common import log


opts = [config.JSONOpt('dhcp', 'vlans', [100, 101],
                       help='Subnet vlans to be pulled from DB.'),
        config.JSONOpt('dhcp', 'dhcp_vlans', [100],
                       help='Subnet vlans to allow dynamic leases. '
                            'For us this is IPMI vlan only'),

        config.IntOpt('dhcp', 'first_offset', default=4,
                      help='First address offset available for leasing'),
        config.IntOpt('dhcp', 'last_offset', default=-2,
                      help='Last address offset available for leasing'),

]
config.register(opts)
CONF = config.get_config()

LOG = log.getLogger(__name__)


class Subnet(object):
    def __init__(self, subnet_id, vlan, ip, mask, gw, first_ip):
        self.subnet_id = subnet_id
        self.vlan = vlan
        self.subnet = netaddr.IPNetwork('{0}/{1}'.format(ip, mask))
        self.gateway_ip = gw
        self.ip_version = self.subnet.version
        self.mode = 'static' if self.vlan not in CONF.dhcp.dhcp_vlans else ''
        self.dhcp = self.vlan in CONF.dhcp.vlans
        self.first_ip = first_ip or str(self.subnet[CONF.dhcp.first_offset])
