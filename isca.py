#! /usr/bin/env python

import os
import json
import argparse
import logging
import random
import sys

try:
    from urllib.parse import urlparse, urlencode, urljoin, urlsplit
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError
except ImportError:
    from urlparse import urlparse, urljoin, urlsplit
    from urllib import urlencode
    from urllib2 import urlopen, Request, HTTPError

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer


class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self.wfile.write("<html><body><h1>hi!</h1></body></html>")

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        print(post_data)
        self._set_headers()
        self.wfile.write("<html><body><h1>POST!</h1></body></html>")


def run_server(server_class=HTTPServer, handler_class=S, host='', port=80):
    server_address = (host, port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

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
        self.start_server(info)

    def create_hook(self, info):
        url = info['CALLBACK_URL']
        repository_name = info['REPOSITORY_NAME']
        access_token = info['GITHUB_ACCESS_TOKEN']

        payload = {
            "name": "web",
            "active": True,
            "events": [
                "push"
            ],
            "config": {
                "url": url,
                "content_type": "json",
                "secret": random.getrandbits(128)
            }
        }

        hooks_url = get_repo_hooks_url(repository_name)
        response = post(hooks_url, payload, access_token)
        hook_id = response['id']

        logger.info("Webhook for %s created with id %s" %
                    (repository_name, hook_id, ))

    def start_server(self, info):
        url_info = urlparse(info['CALLBACK_URL'])
        port = url_info.port
        if port is None:
            port = 80 if url_info.scheme == 'http' else 443
        print(url_info.hostname)
        run_server(host=url_info.hostname, port=port)


def post(url, payload, token):
    logging.debug("POST %s" % (url, ))
    data = json.dumps(payload).encode('utf-8')
    clen = len(data)
    header = {'Content-Type': 'application/json',
              'Content-Length': clen,
              'Authorization': 'token %s' % (token,)}
    try:
        req = Request(url, data, header)
        f = urlopen(req)
        response = f.read()
        f.close()
        return json.loads(response)
    except HTTPError as e:
        error_response = json.loads(e.read())
        logger.exception(error_response['errors'][0]['message'])


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


class ColorfulFormater(logging.Formatter):
    err_fmt  = """\033[94m%(asctime)s\033[0m - \033[94m%(name)s\033[0m -\
 \033[41m%(levelname)s\033[0m - \033[31m%(message)s\033[0m"""
    dbg_fmt  = """\033[94m%(asctime)s\033[0m - \033[94m%(name)s\033[0m -\
 \033[94m%(levelname)s\033[0m - \033[32m%(message)s\033[0m"""
    info_fmt = """\033[94m%(asctime)s\033[0m - \033[94m%(name)s\033[0m -\
 \033[94m%(levelname)s\033[0m - \033[32m%(message)s\033[0m"""

    def __init__(self):
        FORMAT = """\033[94m%(asctime)s\033[0m - \033[94m%(name)s\033[0m -\
 \033[94m%(levelname)s\033[0m - \033[32m%(message)s\033[0m"""
        logging.Formatter.__init__(self, FORMAT)

    def format(self, record):

        # Save the original format configured by the user
        # when the logger formatter was instantiated
        format_orig = None
        has_style = hasattr(self, '_style')
        if has_style:
            format_orig = self._style._fmt
        else:
            format_orig = self._fmt

        # Replace the original format with one customized by logging level
        if record.levelno == logging.DEBUG:
            if has_style:
                self._style._fmt = ColorfulFormater.dbg_fmt
            else:
                self._fmt = ColorfulFormater.dbg_fmt

        elif record.levelno == logging.INFO:
            if has_style:
                self._style._fmt = ColorfulFormater.info_fmt
            else:
                self._fmt = ColorfulFormater.info_fmt

        elif record.levelno == logging.ERROR:
            if has_style:
                self._style._fmt = ColorfulFormater.err_fmt
            else:
                self._fmt = ColorfulFormater.err_fmt

        # Call the original formatter class to do the grunt work
        result = logging.Formatter.format(self, record)

        # Restore the original format configured by the user
        if has_style:
            self._style._fmt = format_orig
        else:
            self._fmt = format_orig

        return result


handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(ColorfulFormater())
logging.root.addHandler(handler)
logging.root.setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    Isca()
