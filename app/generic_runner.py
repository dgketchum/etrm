# ===============================================================================
# Copyright 2017 ross
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===============================================================================

# ============= enthought library imports =======================
# ============= standard library imports ========================
# ============= local library imports  ==========================
from app.paths import paths
from config import Config
from recharge.etrm_processes import Processes
from recharge.preprocessing import generate_rew_tiff


def run_model():
    print 'Running Model'
    cfg = Config()
    for runspec in cfg.runspecs:
        paths.build(runspec.input_root, runspec.output_root)

        etrm = Processes(runspec)

        etrm.configure_run(runspec)

        etrm.run()


def run_rew():
    print 'Running REW'
    generate_rew_tiff()


def run_help():
    keys = ('model', 'rew', 'help')
    print 'Available Commands: {}'.format(','.join(keys))


COMMANDS = {'model': run_model, 'rew': run_rew, 'help': run_help}


def run():
    while 1:
        cmd = raw_input('>> ')
        try:
            func = COMMANDS[cmd]
        except KeyError:
            continue

        func()


if __name__ == '__main__':
    run()
# ============= EOF =============================================
