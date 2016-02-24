#!/bin/env python
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

import sys
import zmq.green as zmq
import ConfigParser


CONFIG_PATH = '/etc/dao/dhcp.cfg'

context = zmq.Context()


class RPCApi(object):

    def __init__(self, connect_url, reply_addr=None):
        self.push = context.socket(zmq.PUSH)
        self.push.connect(connect_url)
        if reply_addr is not None:
            self.pull = context.socket(zmq.PULL)
            reply_port = self.pull.bind_to_random_port(reply_addr)
            self.reply_url = ':'.join((reply_addr, str(reply_port)))

    def send(self, func, *args, **kwargs):
        self.push.send_pyobj({'function': func,
                              'args': args,
                              'kwargs': kwargs})


def main():
    c = ConfigParser.SafeConfigParser({'worker_url': 'tcp://127.0.0.1:5556'})
    c.read(CONFIG_PATH)
    url = c.get('common', 'worker_url')
    op, mac, ip = sys.argv[1:4]
    if op in ('add', 'old'):
        rpc = RPCApi(url)
        rpc.send('dhcp_hook', ip, mac)
