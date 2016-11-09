# This code is copied from http://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-of-unicode-ones-from-json-in-python

from __future__ import print_function
import json


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


def write_to_file(filename, obj):
    '''write a dictionary or list object to a file'''

    with open(filename, 'w') as fobj:

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
