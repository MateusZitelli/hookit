#! /usr/bin/env python

import os
import json
import argparse
import logging

try:
    from urllib.parse import urlparse, urlencode, urljoin, urlsplit
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError
except ImportError:
    from urlparse import urlparse, urljoin, urlsplit
    from urllib import urlencode
    from urllib2 import urlopen, Request, HTTPError

FORMAT = """\033[94m%(asctime)s\033[0m - \033[94m%(name)s\033[0m -\
 \033[94m%(levelname)s\033[0m - \033[32m%(message)s\033[0m"""

logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger(__name__)

GITHUB_API_URL = "https://api.github.com/"


class Isca():
    """ Generic auto hooker for GitHub """
    def __init__(self):
        info = retrieve_info({
            'GITHUB_ACCESS_TOKEN': {
                "description": 'GitHub Access Token',
                "info_type": str},
            'REPOSITORY_NAME': {
                "description": 'Repository name',
                "info_type": str},
            'CALLBACK_URL': {
                "description": 'Callback URL',
                "info_type": str}
        })
        self.create_hook(info)
        # self.create_server()

    def create_hook(self, info):
        url = info['CALLBACK_URL']
        payload = {
            "name": "web",
            "active": True,
            "events": [
                "push"
            ],
            "config": {
                "url": url,
                "content_type": "json"
            }
        }
        hooks_url = get_repo_hooks_url(info['REPOSITORY_NAME'])
        response = post(hooks_url, payload, info['GITHUB_ACCESS_TOKEN'])
        print(response)


def post(url, payload, token):
    logging.debug("POST %s" % (url, ))
    data = json.dumps(payload).encode('utf-8')
    clen = len(data)
    header = {'Content-Type': 'application/json',
              'Content-Length': clen,
              'Authorization': 'token %s' % (token,)}
    req = Request(url, data, header)
    f = urlopen(req)
    response = f.read()
    f.close()
    return response


def get_repo_hooks_url(repository_name):
    return GITHUB_API_URL + "repos/" + repository_name + "/hooks"


def retrieve_info(schema):
    def parse_line(line):
        sline = line.strip()
        key, value = sline.split('=', 1)
        skey = key.strip().upper()
        svalue = value.strip()
        return skey, svalue

    def valid_line(line):
        return not line.strip().startswith('#') and '=' in line

    def load_from_file(filepath):
        with open(filepath) as env:
            loaded_vars = (parse_line(line) for line in env
                           if valid_line(line))

            required_vars_dict = {key_value[0]: key_value[1]
                                  for key_value in loaded_vars
                                  if key_value[0] in schema}

        for key in required_vars_dict:
            logger.info("Loaded %s from %s" % (key, filepath))

        return required_vars_dict

    def load_from_env():
        vars_dict = {key: os.environ[key] for key in schema
                     if key in os.environ}
        for key in vars_dict:
            logger.info("Loaded %s from environment variable." % (key,))
        return vars_dict

    def ask_user(variable):
        return input('\033[44m' + variable['description'] + ':\033[0m ')

    info_vars = {}

    if os.path.exists('.env'):
        info_vars = load_from_file('.env')
    else:
        info_vars = load_from_env()

    for key in schema:
        if key not in info_vars:
            info_vars[key] = ask_user(schema[key])

    return info_vars

if __name__ == "__main__":
    Isca()

