#!/usr/bin/env python3
"""
ONIX-BOT Setup Script
Author: Ian Carter Kulani
Version: 2.0.0
"""

from setuptools import setup, find_packages
import os
import sys

# Read requirements
with open('requirements.txt', 'r') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Read long description
try:
    with open('README.md', 'r', encoding='utf-8') as f:
        long_description = f.read()
except:
    long_description = "ONIX-BOT - Advanced Security Testing Framework"

setup(
    name='onix-bot',
    version='2.0.0',
    author='Ian Carter Kulani',
    author_email='ian@onix-bot.com',
    description='Advanced Security Testing Framework with Multi-Platform Integration',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Iankulani/onix_bot',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: Other/Proprietary License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Security',
        'Topic :: System :: Networking',
    ],
    python_requires='>=3.7',
    install_requires=requirements,
    extras_require={
        'full': [
            'pytest>=7.4.0',
            'black>=23.0.0',
            'sphinx>=7.0.0',
            'prometheus-client>=0.17.0',
            'redis>=5.0.0',
        ],
        'dev': [
            'pytest>=7.4.0',
            'pytest-cov>=4.1.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.4.0',
            'pre-commit>=3.3.0',
        ],
        'docker': [
            'docker>=6.1.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'onix-bot=onix_bot:main',
            'onix=onix_bot:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords='security, pentesting, bot, phishing, ssh, traffic-generator',
    project_urls={
        'Documentation': 'https://docs.onix-bot.com',
        'Source': 'https://github.com/iankarl/onix-bot',
        'Tracker': 'https://github.com/Iankulani/onix_bot/issues',
    },
)