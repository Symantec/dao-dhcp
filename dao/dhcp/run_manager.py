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

import daemon


def _run():
    try:
        from dao.common import config
        config.setup('dhcp', [])

        from dao.common import log
        log.setup('dhcp')
        from dao.dhcp import manager
        manager.run()
    except Exception, exc:
        with open('/tmp/dao.log', 'w') as fd:
            fd.write(repr(exc))
        raise

def run():
    """
    Logically is needed only to not handle closed descriptors which are
    created on imports
    """
    with daemon.DaemonContext():
        _run()
