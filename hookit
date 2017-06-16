#! /usr/bin/env python

import os
import json
import argparse
import logging
import sys
import hashlib
import hmac
import subprocess
import shlex

try:
    from urllib.parse import urlparse, urlencode, urljoin, urlsplit
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError
    from http.server import BaseHTTPRequestHandler, HTTPServer
except ImportError:
    from urlparse import urlparse, urljoin, urlsplit
    from urllib import urlencode
    from urllib2 import urlopen, Request, HTTPError
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

GITHUB_API_URL = "https://api.github.com/"


class Hookit():
    """ Generic auto hooker for GitHub """
    def __init__(self):
        info = retrieve_info({
            'GITHUB_ACCESS_TOKEN': {
                "description": 'GitHub Access Token' },
            'REPOSITORY_NAME': {
                "description": 'Repository name' },
            'HOOK_SECRET': {
                "description": 'Hook secret' },
            'CALLBACK_URL': {
                "description": 'Callback URL' },
            'ON_PUSH_CALL': {
                "description": 'On push command' }
        })

        self.create_hook(info)
        self.start_server(info)

    def create_hook(self, info):
        url = info['CALLBACK_URL']
        repository_name = info['REPOSITORY_NAME']
        access_token = info['GITHUB_ACCESS_TOKEN']
        hook_secret = info['HOOK_SECRET']

        payload = {
            "name": "web",
            "active": True,
            "events": [
                "push"
            ],
            "config": {
                "url": url,
                "content_type": "json",
                "secret": hook_secret
            }
        }

        hooks_url = GITHUB_API_URL + "repos/" + repository_name + "/hooks"
        try:
            response = post(hooks_url, payload, access_token)
            hook_id = response['id']
            logger.info("Webhook for %s created with id %s" %
                        (repository_name, hook_id, ))
        except HTTPError as e:
            error_response = json.loads(e.read())
            if e.code == 422:
                logger.warning(error_response['errors'][0]['message'])
            else:
                logger.error(error_response['message'])
                raise

    def start_server(self, info):
        url_info = urlparse(info['CALLBACK_URL'])
        port = url_info.port
        if port is None:
            port = 80 if url_info.scheme == 'http' else 443

        host = url_info.hostname
        server_address = (host, port)
        httpd = HTTPServer(server_address, self.gen_request_handler(info))
        logger.info("Listening to POSTs at %s" % (info['CALLBACK_URL']))
        httpd.serve_forever()

    def gen_request_handler(self, info):
        hookit = self

        class S(BaseHTTPRequestHandler):
            def _set_headers(self, status=200):
                self.send_response(status)
                self.end_headers()

            def do_POST(self):
                content_length = int(self.headers['Content-Length'])
                client_address = self.client_address[0]
                if 'X-Hub-Signature' not in self.headers:
                    logger.warning("POST without signature from %s" %
                                   (client_address,))
                    return
                received_signature = self.headers['X-Hub-Signature']
                post_data = self.rfile.read(content_length)

                sha1 = hmac.new(info['HOOK_SECRET'], post_data, hashlib.sha1)
                signature = 'sha1=' + sha1.hexdigest()
                signatures_match = hmac.compare_digest(received_signature,
                                                       signature)

                if signatures_match:
                    self._set_headers(200)
                    logger.info("Valid POST from %s" % (client_address,))
                    hookit.on_push_call(info)
                else:
                    self._set_headers(401)
                    logger.warning("POST with wrong signature from %s" %
                                   (client_address,))
        return S

    def on_push_call(self, info):
        subprocess.call(shlex.split(info['ON_PUSH_CALL']))


def get_repo_path(repo_name):
    return repo_name.split('/')[-1]


def post(url, payload, token):
    logging.debug("POST %s" % (url, ))
    data = json.dumps(payload).encode('utf-8')
    clen = len(data)
    header = {
        'Content-Type': 'application/json',
        'Content-Length': clen,
        'Authorization': 'token %s' % (token,)
    }

    req = Request(url, data, header)
    f = urlopen(req)
    response = f.read()
    f.close()
    return json.loads(response)


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
    war_fmt  = """\033[94m%(asctime)s\033[0m - \033[94m%(name)s\033[0m -\
 \033[45m%(levelname)s\033[0m - \033[31m%(message)s\033[0m"""
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

        elif record.levelno == logging.WARNING:
            if has_style:
                self._style._fmt = ColorfulFormater.war_fmt
            else:
                self._fmt = ColorfulFormater.war_fmt

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
    Hookit()
