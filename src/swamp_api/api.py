from __future__ import print_function
import sys
import getpass
import pickle
import os.path as osp
from functools import wraps

import requests

from . import common
from . import types


class SwampApi:

    CSA_SERVER = "https://swa-csaweb-pd-01.mir-swamp.org"
    # CSA_SERVER = "https://swa-csaweb-dt-02.cosalab.org"

    JSON_HEADERS = {
        'Content-Type': 'application/json; charset=UTF-8'
    }

    FORM_HEADERS = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }

    CCPP_BUILD_FILES = {
        'make': 'Makefile',
    }

    JAVA_BUILD_FILES = {
        'ant+ivy': 'build.xml',
        'ant': 'build.xml',
        'maven': 'pom.xml',
        'gradle': 'build.gradle',
    }

    @classmethod
    def get_default_build_file(cls, build_sys):
        return SwampApi.JAVA_BUILD_FILES[build_sys]

    @classmethod
    def get_pkg_types(cls, build_sys):

        if build_sys in SwampApi.CCPP_BUILD_FILES.keys():
            return 1
        elif build_sys in SwampApi.JAVA_BUILD_FILES.keys():
            return 2
        elif build_sys == 'java-bytecode':
            return 3
        else:
            raise NotImplementedError

    @classmethod
    def print_request(cls, request):
        for key in request.headers.keys():
            print(key, " : ", request.headers[key])

    def __init__(self, cookie_dir):
        self.cookie_dir = cookie_dir
        self.csa_cookies = None

    def save_cookies(self):
        with open(osp.join(self.cookie_dir, '.csa_cookies'), 'wb') as fobj:
            pickle.dump(self.csa_cookies, fobj)

    def load_cookies(self):

        try:
            with open(osp.join(self.cookie_dir, '.csa_cookies'), 'rb') as fobj:
                self.csa_cookies = pickle.load(fobj)
        except IOError:
            print('ERROR: login into SWAMP to get session cookies',
                  file=sys.stderr)
            raise

    def use_cookies(func):

        @wraps(func)
        def wrapped(inst, *args, **kwargs):
            inst.load_cookies()
            ret_val = func(inst, *args, **kwargs)
            inst.save_cookies()
            return ret_val
        return wrapped

    def login(self, kwargs):

        if 'user_info_file' in kwargs and \
           kwargs['user_info_file']:
            user_info = common.conf_to_dict(kwargs['user_info_file'])
        elif 'username' in kwargs and 'password' in kwargs:
            user_info = dict()
            user_info['username'] = kwargs['username']
            user_info['password'] = kwargs['password']
        else:
            user_info = dict()
            print('Type in username:', end='', flush=True)
            user_info['username'] = sys.stdin.readline().strip()
            user_info['password'] = getpass.getpass()

        if 'username' in user_info and \
           'password' in user_info:

            resp = requests.post('%s/login' % (SwampApi.CSA_SERVER),
                                 json=user_info,
                                 headers=SwampApi.JSON_HEADERS)

            if resp.status_code != 200 or resp.reason != 'OK':
                raise Exception(resp.status_code, resp.reason)

            self.csa_cookies = resp.cookies

            # resp = requests.post('%s/login' % (SwampApi.CSA_SERVER),
            #                      json=user_info,
            #                      headers=SwampApi.JSON_HEADERS)

            # if resp.status_code != 200 or resp.reason != 'OK':
            #     raise Exception(resp.status_code, resp.reason)

            # self.csa_cookies = resp.cookies
            self.save_cookies()
            return resp.json()['user_uid']

    @use_cookies
    def list_projects(self, kwargs):

        resp = requests.get('%s/users/%s/projects' %
                            (SwampApi.CSA_SERVER, kwargs['user_uuid']),
                            headers=SwampApi.JSON_HEADERS,
                            cookies=self.csa_cookies)

        if resp.status_code != 200 or resp.reason != 'OK':
            raise Exception(resp.status_code, resp.reason)

        return [(project['full_name'], project['project_uid'])
                for project in resp.json()
                if project['owner']['user_uid'] == kwargs['user_uuid']]

    @use_cookies
    def list_pkgs(self, kwargs):

        resp = requests.get('%s/packages/protected/%s' %
                            (SwampApi.CSA_SERVER, kwargs['project_uuid']),
                            headers=SwampApi.JSON_HEADERS,
                            cookies=self.csa_cookies)

        if resp.status_code != 200 or resp.reason != 'OK':
            raise Exception(resp.status_code, resp.reason)

        return [types.Package(pkg['name'], pkg['package_type'], pkg['package_uuid'],
                              pkg['package_type_id'], pkg['version_strings'],
                              pkg)
                for pkg in common.json_decode(resp.json())]

    @use_cookies
    def list_pkg_versions(self, kwargs):

        for pkg in self.list_pkgs(kwargs):

            resp = requests.get('%s/packages/%s/versions' %
                                (SwampApi.CSA_SERVER, pkg.package_uuid),
                                headers=SwampApi.JSON_HEADERS,
                                cookies=self.csa_cookies)

            if resp.status_code != 200 or resp.reason != 'OK':
                raise Exception(resp.status_code, resp.reason)
            print(pkg.json)
            print("\t", common.json_decode(resp.json()))

    #@use_cookies
    def list_pkg_types(self):

        resp = requests.get('%s/packages/types' % (SwampApi.CSA_SERVER))

        if resp.status_code != 200 or resp.reason != 'OK':
            raise Exception(resp.status_code, resp.reason)

        return common.json_decode(resp.json())

    def list_platforms(self):

        resp = requests.get('%s/platforms/public' % (SwampApi.CSA_SERVER))

        if resp.status_code != 200 or resp.reason != 'OK':
            raise Exception(resp.status_code, resp.reason)

        return [(plat['name'], plat['platform_uuid']) for plat in resp.json()]

    def list_tools(self, public=True):

        if public:
            resp = requests.get('%s/tools/public' % (SwampApi.CSA_SERVER),
                                headers=SwampApi.JSON_HEADERS)

            if resp.status_code != 200 or resp.reason != 'OK':
                raise Exception(resp.status_code, resp.reason)

            return [(tool['name'], tool['tool_uuid']) for tool in resp.json()]

        else:
            resp = requests.get('%s/tools/restricted' % (SwampApi.CSA_SERVER),
                                headers=SwampApi.JSON_HEADERS)

            if resp.status_code != 200 or resp.reason != 'OK':
                raise Exception(resp.status_code, resp.reason)

            return [(tool['name'], tool['tool_uuid']) for tool in resp.json()]

    def _get_pkg_info(self, pkg_conf):

        pkg_info = {
            'version_string': pkg_conf.get('package-version', None),
            'notes' : None,
            'source_path': pkg_conf.get('package-dir', '.'),
            'config_dir': pkg_conf.get('config-dir', None),
            'config_cmd': pkg_conf.get('config-cmd', None),
            'config_opt': pkg_conf.get('config-opt', None),
            'build_file': pkg_conf.get('build-file',
                                       SwampApi.get_default_build_file(pkg_conf['build-sys'])),
            'build_system': pkg_conf['build-sys'],
            'build_target': pkg_conf.get('build-target', None),
            'build_dir': pkg_conf.get('build-dir', None),
            'build_opt': pkg_conf.get('build-opt', None),
        }

        return pkg_info

    @use_cookies
    def upload(self, kwargs):

        if not osp.isfile(kwargs['archive']):
            raise IOError(kwargs['archive'])

        resp = requests.post('%s/packages/versions/upload' %
                             (SwampApi.CSA_SERVER),
                             data={'user_uuid': kwargs['user_uuid']},
                             files={'file': open(kwargs['archive'], 'rb')},
                             cookies=self.csa_cookies)

        if resp.status_code != 200 or resp.reason != 'OK':
            raise Exception(resp.status_code, resp.reason)

        dest_path = common.json_decode(resp.json())['destination_path']
        uploaded_filename = common.json_decode(resp.json())['filename']

        if isinstance(kwargs['pkg_conf'], str):
            if not osp.isfile(kwargs['pkg_conf']):
                raise IOError(kwargs['pkg_conf'])
            pkg_conf = common.conf_to_dict(kwargs['pkg_conf'])
        else:
            pkg_conf = kwargs['pkg_conf']

        if 'package_uuid' not in kwargs or kwargs['package_uuid'] is None:
            pkg_data = {
                'package_sharing_status': 'private',
                'name': pkg_conf['package-short-name'],
                'description': pkg_conf.get('description',
                                            'Not Available'),
                'external_url': None,
                'package_type_id': SwampApi.get_pkg_types(pkg_conf['build-sys'])
            }

            resp = requests.post('%s/packages' % (SwampApi.CSA_SERVER),
                                 headers=SwampApi.JSON_HEADERS,
                                 json=pkg_data,
                                 cookies=self.csa_cookies)

            if resp.status_code != 200 or resp.reason != 'OK':
                raise Exception(resp.status_code, resp.reason)

            pkg_uuid = common.json_decode(resp.json())['package_uuid']
        else:
            for pkg in self.list_pkgs(kwargs):
                if pkg.name == pkg_conf['package-short-name']:
                    pkg_uuid = pkg.package_uuid
                    break

        pkg_info = self._get_pkg_info(pkg_conf)
        pkg_info['version_sharing_status'] = 'protected'
        pkg_info['package_uuid'] = pkg_uuid
        pkg_info['package_path'] = osp.join(dest_path, uploaded_filename)
        pkg_info['uploaded_file'] = uploaded_filename

        resp = requests.post('%s/packages/versions/store' %
                             (SwampApi.CSA_SERVER),
                             headers=SwampApi.JSON_HEADERS,
                             json=pkg_info,
                             cookies=self.csa_cookies)

        #self.print_curl_cmd(resp.request)
        if resp.status_code != 200 or resp.reason != 'OK':
            raise Exception(resp.status_code, resp.reason)

        package_version_uuid = common.json_decode(resp.json())['package_version_uuid']

        resp = requests.put('%s/packages/versions/%s/sharing' %
                            (SwampApi.CSA_SERVER, package_version_uuid),
                            headers=SwampApi.FORM_HEADERS,
                            params={'projects[0][project_uid]=': kwargs['project_uuid']},
                            cookies=self.csa_cookies)

        #common.print_curl_cmd(resp.request)
        if resp.status_code != 200 or resp.reason != 'OK':
            raise Exception(resp.status_code, resp.reason)

        return (pkg_uuid, resp.json()[0]['package_version_uuid'])

    @use_cookies
    def run_assessment(self, kwargs):

        assess_info = {
            'project_uuid': kwargs['project_uuid'],
            'package_version_uuid': kwargs['package_version_uuid'],
            'package_uuid': kwargs['package_uuid'],
            'tool_uuid': kwargs['tool_uuid'],
            # 'tool_version_uuid': None
        }

        if 'plat_uuid' in kwargs and kwargs['plat_uuid']:
            assess_info['platform_uuid'] = kwargs['plat_uuid']

        resp = requests.post('%s/assessment_runs' %
                             (SwampApi.CSA_SERVER),
                             headers=SwampApi.JSON_HEADERS,
                             cookies=self.csa_cookies,
                             json=assess_info)

        if resp.status_code != 200 or resp.reason != 'OK':
            raise Exception(resp.status_code, resp.reason)

        assessment_run_uuid = common.json_decode(resp.json())['assessment_run_uuid']

        params = {
            'notify-when-complete': 'true' if kwargs['notify_when_complete'] is True else 'false',
            'assessment-run-uuids[]': assessment_run_uuid
        }

        resp = requests.post('%s/run_requests/one-time' %
                             (SwampApi.CSA_SERVER),
                             headers=SwampApi.FORM_HEADERS,
                             cookies=self.csa_cookies,
                             data=params)

        if resp.status_code != 200 or resp.reason != 'OK':
            raise Exception(resp.status_code, resp.reason)

        return assessment_run_uuid

    @use_cookies
    def get_execution_records(self, kwargs):

        params = {
            'limit': 5
        }

        resp = requests.get('%s/projects/%s/execution_records' %
                            (SwampApi.CSA_SERVER,
                             kwargs['project_uuid']),
                            headers=SwampApi.FORM_HEADERS,
                            cookies=self.csa_cookies,
                            params=params)

        if resp.status_code != 200 or resp.reason != 'OK':
            raise Exception(resp.status_code, resp.reason)

        return [record for record in resp.json()]
