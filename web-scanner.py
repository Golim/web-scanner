#!/usr/bin/env python3

import argparse
import importlib
import json
import requests

VERBOSE = True
QUIET = False

# Cache the response
response = 0

# TODO: These should go in a file with possibility of comments starting with #
files_list = ['robots.txt', '.gitignore']
directories_list = ['.git/', '.well-known/']

def conditional_print(str, end='\n'):
    if not QUIET:
        print(str, end=end)

def print_usage():
    print("USAGE: ./web-scanner.py -t target [OPTIONS]")
    print("type:  ./web-scanner.py -h/--help for a help message")
    exit(1)

def scan_for_files(url):
    # Check for files
    for file_name in files_list:
        conditional_print(f'Searching for file {file_name}')
        response = requests.get(url + file_name)

        if not response and not response.status_code == 400:
            conditional_print('Not found')
            return

        if response.status_code == 200:
            print(f'{file_name} found! Content:')
            print(response.content.decode())
            print()
        else:
            conditional_print('Not found')

def scan_for_directories(url):
    # Check for files
    for dir_name in directories_list:
        conditional_print(f'Searching for directory {dir_name}')
        response = requests.get(url + dir_name)

        if not response and not response.status_code == 400:
            conditional_print('Not found')
            return

        if response.status_code == 200:
            print(f'{dir_name} found!')
        else:
            conditional_print('Not found')

def scan_for_cookies(url):
    # Check for Cookies
    conditional_print('Looking for Cookies')
    session = requests.Session()
    session.cookies.get_dict()
    global response
    if response == 0:
        response = session.get(url)
    cookies = session.cookies.get_dict()
    if cookies:
        print('Found Cookies')
        for cookie in cookies:
            print(cookie, cookies[cookie])
    else:
        conditional_print('No Cookies found')

def search_in_page(url, search):
    conditional_print(f'Looking for {search} in {url}')
    global response
    if response == 0:
        response = requests.get(url)
    content = response.content.decode().split('\n')
    found = False
    for line in content:
        if line.find(search) > 0:
            found = True
            print(f'Found {search}: {line}')
    if not found:
        conditional_print(f'{search} not found')

def print_all_comments(url):
    conditional_print('Looking for comments in ' + url)
    global response
    if response == 0:
        response = requests.get(url)
    content = response.content.decode().split('\n')
    more_lines = False
    found = False

    if url.endswith('.css') or url.endswith('.js'):
        for line in content:
            if more_lines:
                # End of multiple-lines comment
                if line.find('*/'):
                    print(line.split('*/')[0] + '*/')
                    more_lines = False
                else:
                    print(line)
            if line.find('/*') >= 0:
                found = True
                # If inline comment
                if line.find('*/'):
                    print('/*' + line.split('/*')[1].split('*/')[0] + '*/')
                # Comment split on more lines
                else:
                    print('more line ' + line)
                    more_lines = True
                    print('/*' + line.split('/*')[1])
            if line.find('#') >= 0:
                print(line)
        return

    for line in content:
        if more_lines:
            # End of multiple-lines comment
            if line.find('-->'):
                print(line.split('-->')[0] + '-->')
                more_lines = False
            if line.find('--!>'):
                print(line.split('--!>')[0] + '--!>')
                more_lines = False
            else:
                print(line)
        if line.find('<!--') >= 0:
            found = True
            # If inline comment
            if line.find('-->'):
                print('<!--' + line.split('<!--')[1].split('-->')[0] + '-->')
            if line.find('--!>'):
                print('<!--' + line.split('<!--')[1].split('--!>')[0] + '--!>')
            # Comment split on more lines
            else:
                more_lines = True
                print('<!--' + line.split('<!--')[1])
    if not found:
        conditional_print('No Comments found')

def main(args):
    target_url = args.target
    if not (target_url.startswith('http://') or target_url.startswith('https://')):
        target_url = 'http://' + target_url
    
    conditional_print(f'Start scanning { target_url}\n')

    # Scan for files
    if args.files or args.all:
        local_target_url = target_url
        if not target_url.endswith('/'):
            local_target_url += '/'

        scan_for_files(local_target_url)
        conditional_print('\n')

    # Scan for directories
    if args.directories or args.all:
        local_target_url = target_url
        if not target_url.endswith('/'):
            local_target_url += '/'

        scan_for_directories(local_target_url)
        conditional_print('\n')

    if args.cookies or args.all:
        # Scan for cookies
        scan_for_cookies(target_url)
        conditional_print('\n')

    # Search in a web page
    if args.search:
        search = args.search
        search_in_page(target_url, search)
        conditional_print('\n')

    if args.all and args.all != 'noterm':
        search = args.all
        search_in_page(target_url, search)
        conditional_print('\n')

    if args.comments or args.all:
        print_all_comments(target_url)
        conditional_print('\n')

if __name__ == '__main__':
    # Setup the arguments accepted by the program
    parser = argparse.ArgumentParser(prog='web-scanner',
        description='Scan a website for sensitive files, cookies, comments, and search terms. Useful for CTF challenges')

    #Version
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.1')

    # Quiet mode: print only findings
    parser.add_argument('-q', '--quiet', help='', action='store_true')

    # Target URL 
    parser.add_argument('-t', '--target', help='define the target URL to scan', action='store')
    
    # Search Files
    parser.add_argument('-f', '--files', help='search for files in the target website', action='store_true')

    # Search Directories
    parser.add_argument('-d', '--directories', help='search for directories in the target website', action='store_true')

    # Search Cookies
    parser.add_argument('-c', '--cookies', help='search for cookies on the target website', action='store_true')

    # Search all comments
    parser.add_argument('--comments', help='print all comments in the target website\'s code', action='store_true')
    
    # Search in page
    parser.add_argument('-s', '--search', help='search for a string in the target website\'s code', action='store', type=str, metavar=('\"search term\"'))

    # Search for everything
    parser.add_argument('-a', '--all', help='do everything (type noterm to skip search in page)', action='store', type=str, metavar=('\"search term\"'))

    # Argcomplete support
    argcomplete = importlib.util.find_spec('argcomplete')
    if argcomplete is not None:
        import argcomplete
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
