from collections import namedtuple

Package = namedtuple('Package', ['name', 'package_type', 'package_uuid',
                                 'package_type_id', 'version_strings',
                                 'json'])
