#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='peek',
    version='0.1.0',
    author='David Cramer',
    author_email='dcramer@gmail.com',
    url='http://github.com/dcramer/peek',
    description='',
    packages=find_packages(exclude=["tests"]),
    zip_safe=False,
    install_requires=[
    ],
    tests_require=[
        'nose==1.1.2',
        'unittest2==2.0.5.1',
    ],
    license='Apache License 2.0',
    package_data={
        'peek': [
            'htmlfiles/*.*',
        ]
    },
    entry_points={
        'console_scripts': [
            'peek = peek.runner:main',
        ],
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
