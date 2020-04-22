#!/usr/bin/env python3

import argparse
import importlib
import json
import requests

VERBOSE = True
QUIET = False

# TODO: This goes in a file with possibility of comments
#   Add more files to check
files_list = ['robots.txt']

def conditional_print(str, end='\n'):
    if not QUIET:
        print(str, end=end)

def scan_for_file(url):
    # Check for files
    for file_name in files_list:
        conditional_print('Scanning for ' + file_name, end=' ... ')

        response = requests.get(url + file_name)

        if not response and not response.status_code == 400:
            conditional_print('Not found')
            return

        if response.status_code == 200:
            if QUIET:
                print(file_name, end=' ')
            print('Found!')
            print(response.content.decode())

            # TODO: optionally check all directories found in the robots.txt
        else:
            conditional_print('Not found')

def scan_for_cookies(url):
    # Check for Cookies
    conditional_print('Looking for Cookies')

    # TODO: put this in a function
    session = requests.Session()
    session.cookies.get_dict()
    response = session.get(url)
    cookies = session.cookies.get_dict()
    if cookies:
        conditional_print('Looking for Cookies')
        for cookie in cookies:
            print(cookie, cookies[cookie])
    else:
        conditional_print('No Cookies found')

def search_in_page(url, search):
    conditional_print('Looking for ' + search + ' in ' + url)
    response = requests.get(url)
    content = response.content.decode().split('\n')
    found = False
    for line in content:
        if line.find(search) > 0:
            found = True
            print('Found', search, ':', line)
    if not found:
        conditional_print(search + ' not found')

def main(args):
    # Scan for files, cookies and (TODO) directories
    if args.target:
        base_url = args.target
        if not (base_url.startswith('http://') or base_url.startswith('https://')):
            base_url = 'http://' + base_url

        if not base_url.endswith('/'):
            base_url += '/'

        print('Start scanning', base_url, '\n')
        
        # Scan for files
        scan_for_file(base_url)
        conditional_print('\n')

        # Scan for files
        scan_for_cookies(base_url)
        conditional_print('\n')

    # Search in a web page
    if args.search:
        try:
            web_page, search = args.search
        except:
            print('Something bad happened')
            return

        if not (web_page.startswith('http://') or web_page.startswith('https://')):
            web_page = 'http://' + web_page
        
        search_in_page(web_page, search)



if __name__ == '__main__':
    # Setup the arguments accepted by the program
    parser = argparse.ArgumentParser(prog='WEB SCANNER',
        description='Scan a website for sensitive files, cookies and optionally directories. Useful for CTF challenges')

    #Version
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.1')

    # Quiet
    parser.add_argument('-q', '--quiet', help='', action='store_true')
    # TODO: parser.add_argument('--verbose', help='', action='store_true')

    # Target URL 
    parser.add_argument('-t', '--target', help='define the target URL to scan for files and cookies', action='store')

    # Search in page
    parser.add_argument('--search', help='search for a string in a web page', action='store', nargs=2, type=str, metavar=('\"PAGE URL\"', '\"SEARCH TERM\"'))

    # Argcomplete support
    argcomplete = importlib.util.find_spec('argcomplete')
    if argcomplete is not None:
        import argcomplete
        argcomplete.autocomplete(parser)

    argcomplete.autocomplete(parser)

    # Parse arguments
    args = parser.parse_args()

    if args.quiet:
        QUIET = True

    if args.target is None and args.search is None:
        print("USAGE: ./web-scanner.py [OPTIONS] [TARGET URL]")
        print("type:  ./web-scanner.py -h/--help for a help message")

    main(args)

'''
TODO:
- Add possibility to call dirb directly from the program
    - Call dirb on the directories found in the robots.txt
'''