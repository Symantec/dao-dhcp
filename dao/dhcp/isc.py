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
import time
import os
from dao.common import config
from dao.common import log
from dao.common import utils
from dao.dhcp.db import api
from dao.dhcp import base


opts = [config.StrOpt('dhcp', 'leases_dir', '/etc/dhcp/conf.d',
                      help='Path to the directory with static leases'),
        config.IntOpt('dhcp', 'restart_delay', default=4,
                      help='Delay before restarting dhcp')
]
config.register(opts)
CONF = config.get_config()

LOG = log.getLogger(__name__)


Subnet = base.Subnet


class DHCPController(object):
    pending_restarts = False
    @classmethod
    def enable(cls):
        if cls.pending_restarts:
            return
        cls.pending_restarts = True
        time.sleep(CONF.dhcp.restart_delay)
        cls.pending_restarts = False
        LOG.info('DHCP to be restarted')
        ret_code = utils.run_sh('sudo service dhcpd restart'.split())


class ISCController(DHCPController):
    ipmi_template = (
        """subnet {ip} netmask {mask} {{\n"""
        """    range                       {first_ip} {last_ip};\n"""
        """    option subnet-mask          {mask};\n"""
        """    option routers              {gateway};\n"""
        """}}\n""")
    mgmt_template = (
        """subnet {ip} netmask {mask} {{\n"""
        """    option subnet-mask          {mask};\n"""
        """    option routers              {gateway};\n"""
        """}}\n""")

    templates = {'ipmi': ipmi_template,
                 'mgmt': mgmt_template}

    def __init__(self):
        self.db = api.API()

    @property
    def subnets(self):
        for (sid, vlan, ip, mask, gw, first_ip) in self.db.networks_list():
            subnet = Subnet(sid, vlan, ip, mask, gw, first_ip)
            if subnet.dhcp:
                yield subnet

    def _iter_hosts(self):
        """Iterate over hosts.
        @return iterator of (ip, mac, fqdn)
        """
        for subnet in self.subnets:
            for rack_name, ip, mac, device_id, vlan_tag \
                    in self.db.lease_list(subnet.subnet_id):
                mac = mac.replace('-', ':').lower()
                yield (rack_name, ip, mac, device_id, vlan_tag)

    def reload_allocations(self):
        self._reload_allocations()
        self.enable()

    @utils.Synchronized('dhcp')
    def _reload_allocations(self):
        leases_dir = CONF.dhcp.leases_dir
        nets = dict((k, []) for k in self.templates.keys())
        for net in self.subnets:
            net_type = 'mgmt' if net.mode == 'static' else 'ipmi'
            ip = net.subnet.ip
            mask = net.subnet.netmask
            gateway = net.gateway_ip
            temp = netaddr.IPNetwork('{0}/{1}'.format(ip, mask))
            first_ip = temp[CONF.dhcp.first_offset]
            last_ip = temp[CONF.dhcp.last_offset]
            template = self.templates[net_type]
            rec = template.format(**locals())
            nets[net_type].append(rec)

        for net_type, nets_list in nets.items():
            subnets_file = '.'.join((net_type, 'dhcp', 'conf'))
            subnets_file = os.path.join(CONF.dhcp.leases_dir, subnets_file)
            with open(subnets_file, 'w') as fd:
                fd.write('\n'.join(nets[net_type]))

        for (rack, ip, mac, serial, vlan) in self._iter_hosts():
            net_type = 'ipmi' if vlan in CONF.dhcp.dhcp_vlans else 'mgmt'

            subnets_file = '.'.join((net_type, 'dhcp', 'conf'))
            subnets_file = os.path.join(CONF.dhcp.leases_dir, subnets_file)
            template = "host %(hostname)s {\n" \
                       "hardware ethernet %(mac)s;\n" \
                       "fixed-address %(ip)s;\n}\n"
            with open(subnets_file, 'a') as fd:
                fd.write(template %
                         dict(mac=mac, ip=ip,
                              hostname='_'.join((serial, str(vlan)))))
