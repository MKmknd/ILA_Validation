
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

def get_all_modified_files(repodir, commit_hash):
    files = subprocess.check_output(
            ['git', '-C', '{}'.format(repodir), 'diff-tree', '--no-commit-id',
            '--name-only', '-r', commit_hash,  '--diff-filter=ACMRTUX'],
            universal_newlines=True
            ).splitlines()
    
    return files


def ignore_somecode(text):
    text = re.sub('\r', '', text)
    text = re.sub('\f', '', text)
    text = re.sub('\0', '', text)
    return text

def git_show_with_context(dirname, commit_hash, context):
    show = subprocess.check_output(
            ['git', '-C', '{}'.format(dirname), 'show',
             '--unified={0}'.format(context), commit_hash],
            ).decode('utf-8', errors='ignore')
    show = ignore_somecode(show)
    return show
