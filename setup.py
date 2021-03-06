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

from setuptools import setup
import os
import pkg_resources


version_file = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            'VERSION'))
with open(version_file) as v:
    VERSION = v.read().strip()


def get_install_reqs():
    res = []
    with open('requirements.txt') as reqs:
        res = [ str(r) for r in pkg_resources.parse_requirements(reqs) ]
    return res


SETUP = {
    'name': "ops_coordinator",
    'version': VERSION,
    'author': "phvalguima",
    'url': "https://github.com/phvalguima/ops-coordinator",
    'packages': [
        'ops_coordinator',
        'ops_coordinator.base_coordinator',
        'ops_coordinator.operator_libs_linux.v1'
    ],
    'install_requires': get_install_reqs(),
    'scripts': [
    ],
    'license': "Apache License 2.0",
    'long_description': open('README.md').read(),
    'description': 'Lib to manage locks between charm units peer relations',
}

if __name__ == '__main__':
    setup(**SETUP)
