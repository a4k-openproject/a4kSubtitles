# -*- coding: utf-8 -*-

import sys
import subprocess
import os
import json
import re
from xml.etree import ElementTree

github = json.loads(os.getenv('GITHUB_CONTEXT'))
is_pull_request = github['event_name'] == 'pull_request'

if is_pull_request:
    os.system('git fetch --deepen=1 --no-tags --quiet')
    sha = github['event']['pull_request']['head']['sha']
    command_args = ['git', 'log', '--format=%B', '-n', '1', sha]
else:
    command_args = ['git', 'show', '-s', '--format=%s']

git_last_commit_cmd = subprocess.Popen(command_args,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT)

git_stdout, _ = git_last_commit_cmd.communicate()
commit_message = git_stdout.strip().decode('utf8')
print('Commit: `%s`' % commit_message)
os.system('echo "commit=%s" >> %s' % (commit_message, os.getenv('GITHUB_OUTPUT')))

if is_pull_request and github['event']['pull_request']['commits'] > 1:
    print('Error: Ammend your commits!')
    sys.exit(1)

if commit_message.startswith('chore: ') or commit_message.startswith('test: '):
    sys.exit(os.EX_OK)

is_release = commit_message.startswith('release: v')
if not is_release:
    print('Error: Only release, test and chore commits allowed!')
    sys.exit(1)

semver_regex = r'^([0-9]+)\.([0-9]+)\.([0-9]+)$'
version = commit_message.replace('release: v', '')

if not re.match(semver_regex, version):
    print('Error: Only semver `major.minor.patch` allowed without additional labels!')
    sys.exit(1)

tree = ElementTree.parse(os.path.join(os.path.dirname(__file__), '..', 'addon.xml'))
root = tree.getroot()
addon_xml_version = root.get('version')

if addon_xml_version != version:
    print('Error: The version must match the version set in addon.xml!')
    sys.exit(1)

news = root.find('./extension/news').text.strip()
if not news.startswith('[v%s]:' % version):
    print('Error: Update changelog in the news element of addon.xml!')
    sys.exit(1)
