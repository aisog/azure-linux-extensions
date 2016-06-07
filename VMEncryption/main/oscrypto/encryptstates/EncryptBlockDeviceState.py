#!/usr/bin/env python
#
# VM Backup extension
#
# Copyright 2015 Microsoft Corporation
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
#
# Requires Python 2.7+
#

import os
import sys

from inspect import ismethod
from time import sleep
from OSEncryptionState import *

class EncryptBlockDeviceState(OSEncryptionState):
    def __init__(self, context):
        super(EncryptBlockDeviceState, self).__init__('EncryptBlockDeviceState', context)

    def should_enter(self):
        self.context.logger.log("Verifying if machine should enter encrypt_block_device state")

        if not super(EncryptBlockDeviceState, self).should_enter():
            return False
        
        self.context.logger.log("Performing enter checks for encrypt_block_device state")
                
        return True

    def enter(self):
        if not self.should_enter():
            return

        self.context.logger.log("Entering encrypt_block_device state")

        self._find_bek_and_execute_action('_dump_passphrase')

    def should_exit(self):
        self.context.logger.log("Verifying if machine should exit encrypt_block_device state")

        return super(EncryptBlockDeviceState, self).should_exit()

    def _dump_passphrase(self, bek_path):
        proc_comm = ProcessCommunicator()

        self.command_executor.Execute(command_to_execute="od -c {0}".format(bek_path),
                                      raise_exception_on_failure=True,
                                      communicator=proc_comm)
        self.context.logger.log("Passphrase:")
        self.context.logger.log(proc_comm.stdout)

    def _find_bek_and_execute_action(self, callback_method_name):
        callback_method = getattr(self, callback_method_name)
        if not ismethod(callback_method):
            raise Exception("{0} is not a method".format(callback_method_name))

        bek_path = self.bek_util.get_bek_passphrase_file(self.encryption_config)
        callback_method(bek_path)        
