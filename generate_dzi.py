import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import requests
import re
import xml.dom.minidom
import sys
import os

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
def generate_dzi_file(paint_id, info=None):
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

    # check if paintings folder exists
    if not os.path.exists('paintings'):
        os.makedirs('paintings')

    # create dzi file
    file = open(f'paintings/{paint_id}.dzi', 'wb')
    doc = xml.dom.minidom.Document()
    image = doc.createElementNS(xmlns, 'Image')
    image.setAttribute('xmlns', xmlns)
    image.setAttribute('Url', decrypted[0])
    image.setAttribute('Overlap', overlap)
    image.setAttribute('TileSize', decrypted[4])
    image.setAttribute('Format', decrypted[1])
    size = doc.createElementNS(xmlns, 'Size')
    size.setAttribute('Width', str(int(float(decrypted[2]))))
    size.setAttribute('Height', str(int(float(decrypted[3]))))
    image.appendChild(size)
    doc.appendChild(image)
    descriptor = doc.toxml(encoding='UTF-8')
    file.write(descriptor)
    file.close()

if __name__ == '__main__':
    # create the directory to store the dzi files
    if not os.path.exists('paintings'): os.makedirs('paintings')

    paint_id = sys.argv[1]
    generate_dzi_file(paint_id)