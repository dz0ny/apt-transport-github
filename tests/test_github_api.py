import imp
import io
import os
import tempfile

import mock
import vcr

import unittest2


imp.load_source(
    'ghapt',
    os.path.join(os.path.dirname(os.path.realpath(__file__)),
                 '../github.py')
)

from ghapt import GithubPackages, generate_package_info, \
    generate_release_info  # noqa


class TestGHApi(unittest2.TestCase):

    @mock.patch('ghapt.GithubPackages.send')
    def setUp(self, patch):
        self.ghp = GithubPackages()

    def test_generate_package_info(self):
        self.maxDiff = None
        package = {
            'version': 'version',
            'arch': 'arch',
            'name': 'name',
            'maintainer': 'maintainer',
            'size': 'size',
            'download': 'download',
            'updated_at': 'updated_at',
        }
        info = generate_package_info(package)
        self.assertEquals(info,
                          'Package: name\nVersion: version\nArchitecture: arch\nMaintainer: maintainer\nSize: size\nFilename: download\n\n')  # noqa

    def test_generate_release_info(self):
        self.maxDiff = None
        release = {
            'distribution': 'distribution',
            'component': 'component',
            'updated_at': 'updated_at',
            'archs': 'archs',
        }
        info = generate_release_info(release)
        self.assertEquals(info,
                          'Origin: . distribution\nLabel: . distribution\nCodename: distribution\nDate: updated_at\nArchitectures: archs\nComponents: component\nDescription: Generated by GitHub\n\n')  # noqa

    @vcr.use_cassette('tests/fixtures/get_releases.yaml')
    def test_fetch_release(self):
        self.maxDiff = 4096
        tmpf = tempfile.mkstemp()[1]
        msg = {
            'Filename': tmpf,
            '_text': 'URI Acquire', 'Index-File': 'true',
            'URI': 'github://dz0ny/apt-transport-github/dists/any/Release',
            '_number': 600
        }
        self.ghp.fetch_release(msg)
        with io.open(tmpf) as _f:
            contents = _f.read()
        self.assertEquals(contents, 'Origin: . any\nLabel: . any\nCodename: any\nDate: 2014-12-09T12:33:57Z\nArchitectures: any\nComponents: latest\nDescription: Generated by GitHub\n\n')  # noqa

    @vcr.use_cassette('tests/fixtures/get_releases.yaml')
    def test_package_resolver(self):
        packages = []
        for package in self.ghp.packages('dz0ny/apt-transport-github'):
            packages.append(package)
        self.assertEquals(
            packages,
            [
                {
                    'size': 3762,
                    'maintainer': 'Janez Troha <dz0ny@ubuntu.si>',
                    'download': u'https://github.com/dz0ny/apt-transport-github/releases/download/latest/apt-transport-github_amd64.deb',
                    'version': u'latest', 'arch': u'any',
                    'name': u'apt-transport-github_amd64.deb',
                    'updated_at': u'2014-12-09T12:33:57Z'
                },
                {
                    'size': 3762,
                    'maintainer': 'Janez Troha <dz0ny@ubuntu.si>',
                    'download': u'https://github.com/dz0ny/apt-transport-github/releases/download/v0.0.1/apt-transport-github_amd64.deb',
                    'version': u'v0.0.1', 'arch': u'any',
                    'name': u'apt-transport-github_amd64.deb',
                    'updated_at': u'2014-12-09T12:33:55Z'
                }
            ]
        )