#!/usr/bin/env python3

import argparse
import importlib
import json
import requests

VERBOSE = True
QUIET = False
files_list = ['robots.txt']

def scan_for_file(url, file):
    try:
        r = requests.get(url + file)
    except:
        r = None

    return(r)

def main(base_url):
    if not (base_url.startswith('http://') or base_url.startswith('https://')):
        base_url = 'http://' + base_url

    if not base_url.endswith('/'):
        base_url += '/'

    print('Start scanning', base_url, '\n')

    # Check for files
    for file_name in files_list:
        if not QUIET:
            print('Scanning for', file_name, end=' ... ')

        response = scan_for_file(base_url, file_name)
        if not response:
            print('Something bad happened')
            continue
        
        if response.status_code == 200:
            if QUIET:
                print(file_name, end=' ')
            print('Found!')
            print(response.content.decode())

            # TODO: optionally check all directories found in the robots.txt
        else:
            if not QUIET:
                print(file_name, 'Not found')
    
    print('\n')

    # Check for Cookies
    if not QUIET:
        print('Looking for Cookies')

    # TODO: put this in a function
    session = requests.Session()
    session.cookies.get_dict()
    response = session.get(base_url)
    cookies = session.cookies.get_dict()
    if cookies:
        for cookie in cookies:
            print(cookie, cookies[cookie])
    else:
        print('No Cookies found')

if __name__ == '__main__':
    # Setup the arguments accepted by the program
    parser = argparse.ArgumentParser(prog='WEB SCANNER',
        description='Scan a website for sensitive files, cookies and optionally directories. Useful for CTF challenges')

    #Version
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.1')

    # Verbose and Quiet
    parser.add_argument('--verbose', help='', action='store_true')
    parser.add_argument('-q', '--quiet', help='', action='store_true')

    # Target URL
    parser.add_argument('-t', '--target', help='define the target URL', action='store')

    # Argcomplete support
    argcomplete = importlib.util.find_spec('argcomplete')
    if argcomplete is not None:
        import argcomplete
        argcomplete.autocomplete(parser)

    argcomplete.autocomplete(parser)

    # Parse arguments
    args = parser.parse_args()

    if args.quiet:
        VERBOSE = False

    if args.target is None:
        print("USAGE: ./web-scanner.py -t URL")

    main(args.target)

'''
TODO:
- Add possibility to call dirb directly from the program
    - Call dirb on the directories found in the robots.txt
'''