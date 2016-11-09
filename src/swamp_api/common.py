# This code is copied from http://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-of-unicode-ones-from-json-in-python

from __future__ import print_function
import json
import re
import os.path as osp


def _decode_list(data):
    new_data = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _decode_list(item)
        elif isinstance(item, dict):
            item = _decode_dict(item)
        new_data.append(item)
    return new_data


def _decode_dict(data):
    new_data = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = _decode_list(value)
        elif isinstance(value, dict):
            value = _decode_dict(value)
        new_data[key] = value
    return new_data


def json_decode(json_obj):
    if isinstance(json_obj, list):
        return _decode_list(json_obj)
    else:
        return _decode_dict(json_obj)


def json_load(file_obj):
    return json.load(file_obj, object_hook=_decode_dict)


def json_loads(json_str):
    return json.loads(json_str, object_hook=_decode_dict)


def conf_to_dict(filepath):
    '''filepath can be a list or a filepath'''

    def get_line(filepath):

        if isinstance(filepath, str) and osp.isfile(filepath):
            with open(filepath) as fobj:
                for line in fobj:
                    yield line.strip('\n').strip()
        elif isinstance(filepath, set) or isinstance(filepath, list):
            # filepath is a list
            for line in filepath:
                yield line.strip('\n').strip()

    re0 = re.compile(r'((?P<comment>^\s*#.*)|(?P<keyval>^\s*[^\s]+\s*=\s*.+)|(?P<blankline>^\s*))')
    re1 = re.compile(r'^\s*(?P<key>[^\s]+?)\s*=(?P<value>\s*.+)')

    conf_dict = {}

    for line in get_line(filepath):
        match = re0.match(line)
        if match:
            if match.groupdict()['keyval']:
                m1 = re1.match(line)
                key = m1.groupdict()['key']
                value = m1.groupdict()['value'].strip('\n').strip()
                conf_dict[key] = value

    return conf_dict

def write_to_file(filepath, obj):
    '''write a dictionary or list object to a file'''

    with open(filepath, 'w') as fobj:

        if isinstance(obj, dict):
            for key in obj.keys():
                print('{0}={1}'.format(key, obj[key]), file=fobj)

        if isinstance(obj, list):
            for entity in obj:
                print(entity, file=fobj)


def print_curl_cmd(request):
    #print(vars(request))
    print('curl', end=' ')
    print("'%s'" % (request.url), end=' ')
    print(' '.join("-H '%s:%s'" % (key, request.headers[key])
                   for key in request.headers.keys()), end=' ')
    print("--data '%s'" % (request.body))
    print("\n\n")
