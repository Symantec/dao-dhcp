# Copyright 2012 Locaweb.
# Copyright 2016 Symantec Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import errno
import os
import tempfile
from dao.common import log
from dao.common import utils


LOG = log.getLogger(__name__)
run_sh = utils.run_sh


def delete_if_exists(path, remove=os.unlink):
    """Delete a file, but ignore file not found error.

    :param path: File to delete
    :param remove: Optional function to remove passed path
    """

    try:
        remove(path)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise


def ensure_dir(dir_path):
    """Ensure a directory with 755 permissions mode."""
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path, 0o755)


def replace_file(file_name, data, file_mode=0o644):
    """Replaces the contents of file_name with data in a safe manner.

    First write to a temp file and then rename. Since POSIX renames are
    atomic, the file is unlikely to be corrupted by competing writes.

    We create the tempfile on the same device to ensure that it can be renamed.
    """

    base_dir = os.path.dirname(os.path.abspath(file_name))
    tmp_file = tempfile.NamedTemporaryFile('w+', dir=base_dir, delete=False)
    tmp_file.write(data)
    tmp_file.close()
    os.chmod(tmp_file.name, file_mode)
    os.rename(tmp_file.name, file_name)


def get_value_from_file(filename, converter=None):

    try:
        with open(filename, 'r') as f:
            try:
                return converter(f.read()) if converter else f.read()
            except ValueError:
                LOG.error('Unable to convert value in %s', filename)
    except IOError:
        LOG.debug('Unable to access %s', filename)


class ProcessManager(object):
    def __init__(self, pid_file, unique_key, cmd_callback, sudo=False):
        self.pid_file = pid_file
        self.sudo = sudo
        self.cmd_callback = cmd_callback
        self.unique_key = unique_key

    def enable(self, reload_cfg=False):
        if not self.active:
            cmd = self.cmd_callback(self.get_pid_file_name())
            if self.sudo:
                cmd = ['sudo'] + cmd
            run_sh(cmd)
        elif reload_cfg:
            self.reload_cfg()

    def reload_cfg(self):
        self.disable('HUP')

    def disable(self, sig='9'):
        pid = self.pid

        if self.active:
            cmd = ['sudo', 'kill', '-%s' % (sig), str(pid)]
            run_sh(cmd)
            # In the case of shutting down, remove the pid file
            if sig == '9':
                delete_if_exists(self.get_pid_file_name())
        elif pid:
            LOG.debug('Process for %(uuid)s pid %(pid)d is stale, ignoring '
                      'signal %(signal)s', {'uuid': self.uuid, 'pid': pid,
                                            'signal': sig})
        else:
            LOG.debug('No process started for %s', self.uuid)


    @property
    def pid(self):
        """Last known pid for this external process spawned for this uuid."""
        return get_value_from_file(self.get_pid_file_name(), int)

    @property
    def active(self):
        pid = self.pid
        if pid is None:
            return False

        cmdline = '/proc/%s/cmdline' % pid
        try:
            with open(cmdline, "r") as f:
                return self.unique_key in f.readline()
        except IOError:
            return False

    def get_pid_file_name(self):
        """Returns the file name for a given kind of config file."""
        return self.pid_file
