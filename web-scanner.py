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

def print_usage():
    print("USAGE: ./web-scanner.py -t target [OPTIONS]")
    print("type:  ./web-scanner.py -h/--help for a help message")

def scan_for_files(url):
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
        if QUIET:
            print('Looking for Cookies')
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

def print_all_comments(url):
    conditional_print('Looking for comments in ' + url)
    response = requests.get(url)
    content = response.content.decode().split('\n')
    more_lines = False
    for line in content:
        if more_lines:
            if line.find('-->'):
                print(line.split('-->')[0] + '-->')
                more_lines = False
            else:
                print(line)

        if line.find('<!--') > 0:
            # If inline comment
            if line.find('-->'):
                print('<!--' + line.split('<!--')[1].split('-->')[0] + '-->')
            
            else:
                more_lines = True
                print('<!--' + line.split('<!--')[1])

def main(args):
    
    target_url = args.target
    if not (target_url.startswith('http://') or target_url.startswith('https://')):
        target_url = 'http://' + target_url

    # Scan for files
    if args.files:
        if not target_url.endswith('/'):
            target_url += '/'

        print('Start scanning', target_url, '\n')
        
        # Scan for files
        scan_for_files(target_url)
        conditional_print('\n')

    if args.cookies or args.all:
        # Scan for cookies
        scan_for_cookies(target_url)
        conditional_print('\n')

    # Search in a web page
    if args.search or args.all:
        search = args.search
        search_in_page(target_url, search)

    if args.comments or args.all:
        print_all_comments(target_url)


if __name__ == '__main__':
    # Setup the arguments accepted by the program
    parser = argparse.ArgumentParser(prog='WEB_SCANNER',
        description='Scan a website for sensitive files, cookies, comments, and search terms. Useful for CTF challenges')

    #Version
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.1')

    # Quiet
    parser.add_argument('-q', '--quiet', help='', action='store_true')
    # TODO: parser.add_argument('--verbose', help='', action='store_true')

    # Target URL 
    parser.add_argument('-t', '--target', help='define the target URL to scan', action='store')
    
    # Search Files
    parser.add_argument('-f', '--files', help='search for files in the target website', action='store_true')

    # Search Cookies
    parser.add_argument('-c', '--cookies', help='search for cookies on the target website', action='store_true')

    # Search all comments
    parser.add_argument('--comments', help='print all comments in the target website\'s code', action='store_true')
    
    # Search in page
    parser.add_argument('-s', '--search', help='search for a string in the target website\'s code', action='store', type=str, metavar=('\"SEARCH_TERM\"'))

    # Search for everything TODO
    parser.add_argument('-a', '--all', help='do everything', action='store', type=str, metavar=('\"SEARCH_TERM\"'))

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

    if args.target is not None:
        if args.files is None \
            and args.cookies is None \
            and args.comments is None \
            and args.search is None\
            and args.all is None:

            printUsage()
    else:
        print_usage()

    main(args)
