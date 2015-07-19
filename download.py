#!/usr/bin/env python

import argparse
import sys
import os
import os.path
import re
import shutil
import requests
from bs4 import BeautifulSoup


def save_file(name, content, path):
    if not os.path.exists(path):
        os.mkdir(path)
    with open(name, 'wb') as f:
        f.write(content)
        if os.path.exists(os.path.join(path, name)):
            os.remove(os.path.join(path, name))
        shutil.move(name, path)


def land_on(album_url, album_name):
    r = requests.get(album_url)
    if r.status_code != 200:
        return

    soup = BeautifulSoup(r.text, 'html.parser')

    for link in soup.find_all('a'):
        attr_class = link.get('class', [])
        if "photolst_photo" in attr_class:
            image_link = re.sub('thumb', 'large', link.img['src'])
            r = requests.get(image_link)
            if r.status_code != 200:
                image_link = re.sub('thumb', 'photo', link.img['src'])
                r = requests.get(image_link)

            image_name = re.sub('.*/', '', image_link)
            if r.status_code == 200:
                print(os.path.join(album_name, image_name))
                save_file(image_name, r.content, album_name)
            else:
                print("Error: failed to get %s" % image_link, file=sys.stderr)

    link = soup.find(rel='next')
    if link is not None:
        land_on(link['href'], album_name)


def find_photos(user_id, album=None, slient=False):

    homepage = 'http://www.douban.com/people/' + user_id + '/photos'

    r = requests.get(homepage)
    if r.status_code != 200:
        print('Error: cannot get user''s webpage', file=sys.stderr)
        return

    soup = BeautifulSoup(r.text, 'html.parser')

    albums = []
    for link in soup.find_all('div', class_='pl2'):
        if album is None and not slient:
            comfirm = input('find album "%s", download? : ' % link.a.string).lower()
            if comfirm != 'y' and comfirm != 'yes':
                continue
        elif album is not None:
            if album != link.a.string:
                continue

        albums.append((link.a['href'], link.a.string))

    if len(albums) == 0:
        print("Error: album not found", file=sys.stderr)

    for album in albums:
        print('downloading album %s' % album[1])
        land_on(album[0], album[1])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='spider')
    parser.add_argument('-y', '--yes', action='store_const', const=True, dest='yes', help='yes for all albums')
    parser.add_argument('user_id', action='store')
    parser.add_argument('album', action='store', nargs='?', default=None)
    args = parser.parse_args()

    find_photos(args.user_id, args.album, args.yes)
