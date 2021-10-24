
import subprocess
import sys
import re
from datetime import datetime as dt

def get_date(dirname, commit_hash):
    date = subprocess.check_output(
            ['git', '-C', '{}'.format(dirname), 'show', '{0}'.format(commit_hash), '-s', '--format=%ai'],
            universal_newlines=True
            )
    return date.splitlines()[0]


def get_all_hash(repodir):
    hash_list = subprocess.check_output(
            ['git', '-C', '{}'.format(repodir), 'log', '--all', '--pretty=format:%H'],
            universal_newlines=True
            ).splitlines()
    return hash_list

def get_all_hash_without_merge(repodir):
    hash_list = subprocess.check_output(
            ['git', '-C', '{}'.format(repodir), 'log', '--all', '--no-merges', '--pretty=format:%H'],
            universal_newlines=True
            ).splitlines()
    return hash_list
