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

from dao.common import config
from dao.dhcp.db.session_api import get_session

opts = [config.StrOpt('common', 'location',
                      help='Abbreviation for environment location. '
                      'Common values are ASH, etc.'),]

config.register(opts)
CONF = config.get_config()


class API(object):
    @staticmethod
    def networks_list():
        session = get_session()
        try:
            sstr = ('SELECT * FROM subnet WHERE location="{0}" AND deleted=0'.
                    format(CONF.common.location))
            query = session.query('id', 'vlan_tag', 'ip', 'mask', 'gateway',
                                  'first_ip')
            return query.from_statement(sstr).all()
        finally:
            session.close()

    @staticmethod
    def lease_list(subnet_id):
        session = get_session()
        try:
            sstr = ('SELECT * FROM port WHERE subnet_id={0} and deleted=0'.
                    format(subnet_id))
            query = session.query('rack_name', 'ip', 'mac', 'device_id',
                                  'vlan_tag')
            return query.from_statement(sstr).all()
        finally:
            session.close()
