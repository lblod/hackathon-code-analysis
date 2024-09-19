import argparse
import yaml
import logging
import pprint
import re
import os
from git import Repo, Git

# Helper functions
def name_from_url(url):
    p = re.compile('^.*\/(.*)\.git$')
    m = p.match(url)
    return m.group(1)

def clone_repos(config):
    for group_name in config:
        repos = config[group_name]['repo']
        for repo_url in repos:
            repo_name = name_from_url(repo_url)
            path = "repos/" + group_name + "/" + repo_name
            if not os.path.isdir(path):
                Repo.clone_from(repo_url, path)

def authors_in_group(group_name, config):
    repos = config[group_name]['repo']
    authors = set()
    for repo_url in repos:
        repo_name = name_from_url(repo_url)
        git = Git("repos/" + group_name + "/" + repo_name)
        authors_as_text = git.log('--since=2024-09-10','--pretty=tformat:%an')
        
        for line in authors_as_text.split('\n'):    
            authors.add(line.rstrip())
    # Some system user thing?
    authors.discard("x-m-el")
    authors.discard("")
    return authors


# Init -->
# Handle cli arguments, e.g. --log=DEBUG
parser = argparse.ArgumentParser()
parser.add_argument("-l", "--log",
                     help = "loglevel, e.g. INFO, DEBUG,...")
parser.add_argument("-c", "--config", help = "Allow specifying the config file. Defaults to config.yml")

args = parser.parse_args()
logger = logging.getLogger(__name__)
numeric_level = logging.INFO
if args.log:
    numeric_level = getattr(logging, args.log.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % args.log.upper())
logging.basicConfig(level=numeric_level)

# Config
config_file = 'config.yml'
if args.config:
    config_file = args.config
with open(config_file, 'r') as file:
    config = yaml.safe_load(file)

# Main -->
clone_repos(config)
for group_name in config:
    for author in authors_in_group(group_name, config):
        path = "code_by_author/" + group_name + "/" + author + ".diff"
        if os.path.isfile(path):
            os.remove(path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        individual_contrib = open(path, "w", encoding='UTF-8', errors='replace')
        
        for repo_url in config[group_name]['repo']:
            git = Git("repos/" + group_name + "/" + name_from_url(repo_url))
            code_by_author = git.log(
                '--since=2024-09-10', # Avoid commits in forked code made by employees before hackathon
                '--pretty=tformat:%an',
                '-p',
                '--author=' + author
            )
            individual_contrib.write(code_by_author)
        individual_contrib.close()

            #pprint.pprint(code_by_author)