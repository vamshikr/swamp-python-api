import sys
import argparse
import os

from .api import SwampApi


def process_cli_args():

    main_parser = argparse.ArgumentParser(prog='swamp-api-client',
                                          description='''Use any of the sub commands:''')

    subparsers = main_parser.add_subparsers(help='sub-command help')

    login_parser = subparsers.add_parser('login', help='login into SWAMP')
    login_parser.add_argument('--user-info-file',
                              help='user credentials filepath')
    
    projects_parser = subparsers.add_parser('projects',
                                            help='Get the list of projects that you own')
    projects_parser.add_argument('--user-uuid', required=True, help='User UUID')

    pkg_parser = subparsers.add_parser('packages',
                                       help='Get the list of package for a project')
    pkg_parser.add_argument('--project-uuid', required=True, help='Project UUID')
    pkg_parser.add_argument('--with-versions', required=False,
                            action='store_true', help='With Versions')
    
    upload_parser = subparsers.add_parser('upload', help='Upload a package')
    upload_parser.add_argument('--archive', required=True, help='Package archive')
    upload_parser.add_argument('--pkg-conf', required=True, help='Package Conf')
    upload_parser.add_argument('--user-uuid', required=True, help='User UUID')
    upload_parser.add_argument('--project-uuid', required=True, help='Project UUID')
    upload_parser.add_argument('--package-uuid', required=False, help='Package UUID')
    
    subparsers.add_parser('package-types', help='Get package types')
    subparsers.add_parser('platforms', help='Get platforms list')

    tools_parser = subparsers.add_parser('tools', help='Get tools list')
    tool_group = tools_parser.add_mutually_exclusive_group(required=True)
    tool_group.add_argument('--public', action='store_true')
    tool_group.add_argument('--restricted', action='store_true')

    assess_parser = subparsers.add_parser('assess', help='Run assessments')
    assess_parser.add_argument('--project-uuid', required=True, help='Project UUID')
    assess_parser.add_argument('--package-uuid', required=True, help='Package UUID')
    assess_parser.add_argument('--package-version-uuid', required=True, help='Package Version UUID')
    assess_parser.add_argument('--tool-uuid', required=True, help='Tool UUID')
    assess_parser.add_argument('--plat-uuid', help='Platform UUID')
    assess_parser.add_argument('--notify-when-complete', default=False,
                               required=False, action='store_true',
                               help='Notify when complete')

    records_parser = subparsers.add_parser('execution-records',
                                            help='Get execution records for the project')
    records_parser.add_argument('--project-uuid', required=True, help='User UUID')
    
    return main_parser


def main():
    parser = process_cli_args()
    args = vars(parser.parse_args())
    task = None

    if len(sys.argv) > 1:
        task = sys.argv[1]
    else:
        parser.print_help()
        sys.exit(1)
        
    api_client = SwampApi(os.getcwd())
    
    if task == 'login':
        user_uuid = api_client.login(args)
        print(user_uuid)
    elif task == 'projects':
        for proj_name, proj_uuid in api_client.list_projects(args):
            print('%s (%s)' % (proj_name, proj_uuid))
    elif task == 'packages':

        api_client.list_pkg_versions(args)
        return
        for pkg in api_client.list_pkgs(args):
            print(pkg.name, pkg.package_type, pkg.package_uuid,
                  pkg.package_type_id, pkg.version_strings)
            api_client.list_pkg_versions(args)
            
    elif task == 'package-types':
        print(api_client.list_pkg_types())
    elif task == 'upload':
        print('package_version_uuid: %s\npackage_version_uuid: %s' % (api_client.upload(args)))
    elif task == 'tools':
        for tool_name, tool_uuid in api_client.list_tools(args['public']==True):
            print('%s (%s)' % (tool_name, tool_uuid))
    elif task == 'platforms':
        for plat_name, plat_uuid in api_client.list_platforms():
            print('%s (%s)' % (plat_name, plat_uuid))
    elif task == 'assess':
        print(api_client.run_assessment(args))
    elif task == 'execution-records':
        api_client.get_execution_records(args)
    else:
        raise NotImplementedError


if __name__ == '__main__':
    main()
