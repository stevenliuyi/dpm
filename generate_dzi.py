import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import requests
import re
import xml.dom.minidom
import sys
import os

################################################################
## Minghua Ji (https://minghuaji.dpm.org.cn/)
################################################################

# get text from url
def get_text_from_url(url):

    # get response from the url
    res = requests.get(url)

    # check for successful request
    if res.status_code != 200:
        raise ValueError(f'Encountered error when visiting {url}: {res.status_code}')

    return res.text

# get gv info from url
def get_info():
    gv_url = 'https://minghuaji.dpm.org.cn/js/gve.js'

    # get response from the url
    res_text = get_text_from_url(gv_url)

    # find all substrings surrounded by double quotes
    info = re.findall(r'"(.*?)"', res_text)

    # get key and iv from the substrings
    if len(info) < 5:
        raise ValueError(f'Encountered error when parsing {gv_url}')

    return info

# convert info to bytes
def info2bytes(info):
    return bytes.fromhex(info.replace('\\x',''))

# decrypt the encrypted string
def decrypt(encrypted, key, iv):
    # create cipher object
    cipher = AES.new(key, AES.MODE_CBC, iv)

    # decrypt the encrypted string
    decrypted = cipher.decrypt(base64.b64decode(encrypted))
    decrypted = unpad(decrypted, 16).decode('utf-8').split('^')

    return decrypted

# get the encrypted string from the paint url
def get_encrypted_text(paint_url):
    # get response from the url
    res_text = get_text_from_url(paint_url)

    # find the first substring that matches the encrypted string
    match = re.search(r'gv.init\("(.*?)"', res_text)
    if match:
        encrypted = match.group(1)
        return encrypted
    else:
        raise ValueError(f'Cannot find encrypted string in {paint_url}')

# generate the dzi file
def generate_dzi_file_mhj(paint_id, info=None):
    paint_url = f'https://minghuaji.dpm.org.cn/paint/appreciate?id={paint_id}'

    # get info
    if info is None: info = get_info()

    # get key and vi and use them to decrypt the encrypted string
    key = info2bytes(info[1])
    iv = info2bytes(info[4])
    encrypted = get_encrypted_text(paint_url)
    decrypted = decrypt(encrypted, key, iv)

    # get xmlns and overlap
    xmlns = info2bytes(info[28]).decode('utf-8')
    overlap = info2bytes(info[29]).decode('utf-8')

    # create dzi file
    dzi_info = {
        'xmlns': xmlns,
        'url': decrypted[0],
        'overlap': overlap,
        'tilesize': decrypted[4],
        'format': decrypted[1],
        'width': str(int(float(decrypted[2]))),
        'height': str(int(float(decrypted[3])))
    }
    write_dzi_file(paint_id, dzi_info)

################################################################
## Collection (https://www.dpm.org.cn/explore/collections.html)
################################################################

def generate_dzi_file_collection(paint_id):
    url = f'https://www.dpm.org.cn/collection/paint/{paint_id}.html'
    html_string = get_text_from_url(url)
    soup = BeautifulSoup(html_string, 'html.parser')

    # get dzi url
    item = soup.select_one('#hl_content')
    image_item = item.select_one('img')
    tilegenerator_url = image_item.get('custom_tilegenerator').replace('dyx.html?path=/', '')
    tilegenerator = get_text_from_url(tilegenerator_url)

    # get dzi info
    root = ET.fromstring(tilegenerator)
    dzi_info = {
        'xmlns': root.attrib['xmnls'],
        'url': tilegenerator_url.replace('http:','https:').replace('.xml', '_files/'),
        'overlap': root.attrib['Overlap'],
        'tilesize': root.attrib['TileSize'],
        'format': root.attrib['Format'],
        'width': root[0].attrib['Width'],
        'height': root[0].attrib['Height']
    }
    write_dzi_file(paint_id, dzi_info)

################################################################
## common functions
################################################################

def generate_dzi_file(website, paint_id, info=None):
    if website == 'mhj':
        generate_dzi_file_mhj(paint_id, info)
    elif website == 'collection':
        generate_dzi_file_collection(paint_id)
    else:
        raise ValueError(f'Unknown website {website}')

def write_dzi_file(paint_id, dzi_info):
    # check if paintings folder exists
    if not os.path.exists('paintings'):
        os.makedirs('paintings')

    # create dzi file
    file = open(f'paintings/{paint_id}.dzi', 'wb')
    doc = xml.dom.minidom.Document()
    image = doc.createElementNS(dzi_info['xmlns'], 'Image')
    image.setAttribute('xmlns', dzi_info['xmlns'])
    image.setAttribute('Url', dzi_info['url'])
    image.setAttribute('Overlap', dzi_info['overlap'])
    image.setAttribute('TileSize', dzi_info['tilesize'])
    image.setAttribute('Format', dzi_info['format'])
    size = doc.createElementNS(dzi_info['xmlns'], 'Size')
    size.setAttribute('Width', dzi_info['width'])
    size.setAttribute('Height', dzi_info['height'])
    image.appendChild(size)
    doc.appendChild(image)
    descriptor = doc.toxml(encoding='UTF-8')
    file.write(descriptor)
    file.close()


if __name__ == '__main__':
    # create the directory to store the dzi files
    if not os.path.exists('paintings'): os.makedirs('paintings')

    website = sys.argv[1]
    paint_id = sys.argv[2]

    generate_dzi_file(website=website, id=paint_id)