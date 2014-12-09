#!/usr/bin/python -u

# The MIT License (MIT)
# Copyright (c) 2014 Janez Troha <dz0ny@ubuntu.si>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import urllib2
import urlparse
import time
import hashlib
import hmac
import json
import sys
import os
from configobj import ConfigObj
import requests
import syslog

import logging
logger = logging.getLogger('github')
hdlr = logging.FileHandler('/var/tmp/apt-github.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.DEBUG)

class GithubAPI(object):
    def __init__(self):
        self.seddion = requests.Session()
        

class APTMessage(object):
    MESSAGE_CODES = {
        100: 'Capabilities',
        102: 'Status',
        200: 'URI Start',
        201: 'URI Done',
        400: 'URI Failure',
        600: 'URI Acquire',
        601: 'Configuration',
    }

    def __init__(self, code, headers):
        self.code = code
        self.headers = headers

    def process(self, lines):
        status_line = lines.pop(0)
        self.code = int(status_line.split()[0])
        self.headers = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            parts = [p.strip() for p in line.split(':', 1)]
            if len(parts) != 2:
                continue
            self.headers.append(parts)
        return self(code, headers)

    def encode(self):
        result = '{0} {1}\n'.format(self.code, self.MESSAGE_CODES[self.code])
        for item in self.headers.keys():
            if self.headers[item] is not None:
                result += '{0}: {1}\n'.format(item, self.headers[item])
        return result + '\n'


class Github_method(object):
    __eof = False

    def __init__(self):
        self.send_capabilities()

    def fail(self, message='Failed'):
        self.send_uri_failure({'URI': self.uri, 'Message': message})

    def _read_message(self):
        """
        Apt uses for communication with its methods the text protocol similar
        to http. This function parses the protocol messages from stdin.
        """
        if self.__eof:
            return None
        result = {}
        line = sys.stdin.readline()
        while line == '\n':
            line = sys.stdin.readline()
        if not line:
            self.__eof = True
            return None
        s = line.split(" ", 1)
        result['_number'] = int(s[0])
        result['_text'] = s[1].strip()

        while not self.__eof:
            line = sys.stdin.readline()
            if not line:
                self.__eof = True
                return result
            if line == '\n':
                return result
            s = line.split(":", 1)
            result[s[0]] = s[1].strip()

    def send(self, code, headers):
        message = APTMessage(code, headers)
        sys.stdout.write(message.encode())

    def send_capabilities(self):
        self.send(100, {'Version': '1.0', 'Single-Instance': 'true'})

    def send_status(self, headers):
        self.send(102, headers)

    def send_uri_start(self, headers):
        self.send(200, headers)

    def send_uri_done(self, headers):
        self.send(201, headers)

    def send_uri_failure(self, headers):
        self.send(400, headers)

    def run(self):
        """Loop through requests on stdin"""
        while True:
            message = self._read_message()
            logger.debug(message)
            if message is None:
                return 0
            if message['_number'] == 600:
                try:
                    if message['URI'].endswith('binary-amd64/Packages'):
                        self.fetch_packages('amd64')
                    if message['URI'].endswith('binary-i386/Packages'):
                        self.fetch_packages('i386')
                    else:
                        self.fetch(message)
                except Exception, e:
                    self.fail(e.__class__.__name__ + ": " + str(e))
            else:
                return 100
    def fetch_packages(arch):
        pass

    def fetch(self, msg):
        self.uri = msg['URI']
        self.uri_parsed = urlparse.urlparse(self.uri)
        self.uri_updated = 'https://' + self.uri_parsed.netloc +\
            self.uri_parsed.path
        self.filename = msg['Filename']

        response = self.iam.urlopen(self.uri_updated)
        self.send_status({'URI': self.uri, 'Message': 'Waiting for headers'})

        if response.code != 200:
            self.send_uri_failure({
                'URI': self.uri,
                'Message': str(response.code + '  ' + response.msg),
                'FailReason': 'HttpError' + str(response.code)})
            while True:
                data = response.read(4096)
                if not len(data):
                    break
            response.close()
            return

        self.send_uri_start({
            'URI': self.uri,
            'Size': response.headers.getheader('content-length'),
            'Last-Modified': response.headers.getheader('last-modified')})

        f = open(self.filename, "w")
        hash_sha256 = hashlib.sha256()
        hash_md5 = hashlib.md5()
        while True:
            data = response.read(4096)
            if not len(data):
                break
            hash_sha256.update(data)
            hash_md5.update(data)
            f.write(data)
        response.close()
        f.close()

        self.send_uri_done({
            'URI': self.uri,
            'Filename': self.filename,
            'Size': response.headers.getheader('content-length'),
            'Last-Modified': response.headers.getheader('last-modified'),
            'MD5-Hash': hash_md5.hexdigest(),
            'MD5Sum-Hash': hash_md5.hexdigest(),
            'SHA256-Hash': hash_sha256.hexdigest()})

if __name__ == '__main__':
    try:
        method = S3_method()
        ret = method.run()
        sys.exit(ret)
    except KeyboardInterrupt:
        pass