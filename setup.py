#!/usr/bin/env python3
# coding=utf-8
# Copyright 2019 YAM AI Machinery Limited
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

from setuptools import setup, find_packages
from yamas.config import VERSION

from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='yamas',
    version=VERSION,
    description='Yamas - Yet Another Mock API Server',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Testing :: Mocking',
    ],
    python_requires='>=3.6',
    keywords='rest api mocking server',
    url='https://github.com/yam-ai/yamas',
    author='Thomas Lee',
    author_email='thomaslee@yam.ai',
    zip_safe=True,
    scripts=['bin/yamas'],
    packages=find_packages(exclude=['tests']),
    install_requires=['jsonschema>=3.1.1,<3.2.0'],
    tests_require=['pytest>=5.2.2,<5.3.0', 'requests>=2.22.0,<2.23.0']
)
