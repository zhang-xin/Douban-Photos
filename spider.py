#!/usr/bin/env python

import argparse
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
        print(name)
        print(os.path.join(path, name))
        if os.path.exists(os.path.join(path, name)):
            os.remove(os.path.join(path, name))
        shutil.move(name, path)


def land_on(album, album_name):
    r = requests.get(album)
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
            print(image_link)
            if r.status_code == 200:
                print(image_name, album_name)
                save_file(image_name, r.content, album_name)

    link = soup.find(rel='next')
    if link is not None:
        land_on(link['href'], album_name)


def find_photos(homepage):
    r = requests.get('/'.join([homepage, 'photos']))
    if r.status_code != 200:
        print('Error: not found the user''s photos')
        return

    soup = BeautifulSoup(r.text, 'html.parser')
    for link in soup.find_all('div', class_='pl2'):
        comfirm = input('find album "%s", download? : ' % link.a.string).lower()
        if comfirm == 'y' or comfirm == 'yes':
            land_on(link.a['href'], link.a.string)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='spider')
    parser.add_argument('-i', '--image', action='store_const', const=True, dest='image')
    parser.add_argument('website', action='store')
    args = parser.parse_args()

    find_photos(args.website)
