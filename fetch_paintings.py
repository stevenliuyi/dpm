import requests
import re
from bs4 import BeautifulSoup
import pandas as pd
import os
import sys

################################################################
## Minghua Ji (https://minghuaji.dpm.org.cn/)
################################################################

def get_xsrf_token():
    url = 'https://minghuaji.dpm.org.cn/paint/list'
    response = requests.get(url)
    headers = response.headers
    cookie = headers["set-cookie"]

    # obtain the xsrf token from the cookie
    match = re.search(r'XSRF-TOKEN=(.*?);', cookie)
    if match:
        token = match.group(1)
        return token
    else:
        raise ValueError(f'Cannot find xsrf token in response headers from {url}')

def fetch_page_mhj(page, xsrf_token):
    url = f'https://minghuaji.dpm.org.cn/paint/queryList?page={page}&showType=0'
    headers = {
        'Connection': 'keep-alive',
        'Cookie': f'XSRF-TOKEN={xsrf_token}',
        'X-XSRF-TOKEN': xsrf_token
    }

    res = requests.post(url, headers=headers)
    # check for successful request
    if res.status_code != 200:
        raise ValueError(f'Encountered error when visiting {url}: {res.status_code}')

    # parse the response text and extract painting info
    html_string = res.text
    soup = BeautifulSoup(html_string, 'html.parser')
    paint_items = soup.find_all('li')

    paintings = []

    for paint_item in paint_items:
        img_box = paint_item.select_one('.img_box')
        if img_box is None: continue
        author = img_box.get('tagauthor')
        dynasty = img_box.get('tagdynasty')
        paint_id = img_box.get('tagid')
        name = img_box.get('tagname')
        print(f'{paint_id} {name} {author} {dynasty}')
        paintings.append({
            'id': paint_id,
            'name': name,
            'author': author,
            'dynasty': dynasty
        })

    return paintings

# obtain more details about a specific painting
def fetch_detail_mhj(id):
    url = f'https://minghuaji.dpm.org.cn/paint/detail?id={id}'

    res = requests.get(url)
    # check for successful request
    if res.status_code != 200:
        raise ValueError(f'Encountered error when visiting {url}: {res.status_code}')

    # parse the response text and extract painting info
    html_string = res.text
    soup = BeautifulSoup(html_string, 'html.parser')
    info = soup.select_one('.pf_main').select_one('h3')
    splitted = [x.strip() for x in info.text.split('，')]

    # extract details
    if splitted[2][0] == '纵':
        material = ''
        color = ''
        height = splitted[2]
        width = splitted[3]
    elif splitted[3][0] == '纵':
        material = splitted[2]
        color = ''
        height = splitted[3]
        width = splitted[4]
    elif splitted[4][0] == '纵':
        material = splitted[2]
        color = splitted[3]
        height = splitted[4]
        width = splitted[5]
    elif splitted[5][0] == '纵':
        material = splitted[2]
        color = f'{splitted[3]}，{splitted[4]}'
        height = splitted[5]
        width = splitted[6]

    # check width and height
    if height[0] != '纵': raise ValueError(f'Cannot find height in {info.text}')
    if width[0] != '横': raise ValueError(f'Cannot find width in {info.text}')

    # extract the numbers
    height = float(re.findall('[\d\.,]+',height)[0].replace(',',''))
    width = float(re.findall('[\d\.,]+',width)[0].replace(',',''))

    print(f'id: {id}, material: {material}, color: {color}, height: {height}, width: {width}')

    return {
        'material': material,
        'color': color,
        'height': height,
        'width': width
    }

################################################################
## Collection (https://www.dpm.org.cn/explore/collections.html)
################################################################

def fetch_page_collection(page):
    url = f'https://www.dpm.org.cn/searchs/paints/category_id/91/p/{page}.html'

    res = requests.post(url)
    # check for successful request
    if res.status_code != 200:
        raise ValueError(f'Encountered error when visiting {url}: {res.status_code}')

    # parse the response text and extract painting info
    html_string = res.text
    soup = BeautifulSoup(html_string, 'html.parser')
    paint_items = soup.select_one('.table1').find_all('tr')[1:]

    if len(paint_items) <=1: return []

    paintings = []

    for paint_item in paint_items:
        paint_id = paint_item.select_one('td:nth-child(1)').select_one('a').get('href').split('/')[-1].split('.')[0]
        name = paint_item.select_one('td:nth-child(1)').text.strip()
        dynasty = paint_item.select_one('td:nth-child(2)').text.strip()
        category = paint_item.select_one('td:nth-child(3)').text.strip()
        author = paint_item.select_one('td:nth-child(4)').text.strip()
        print(f'{paint_id} {name} {author} {dynasty}')
        paintings.append({
            'id': paint_id,
            'name': name,
            'author': author,
            'dynasty': dynasty,
            'category': category
        })

    return paintings

# obtain more details about a specific painting
def fetch_detail_collection(id):
    url = f'https://www.dpm.org.cn/collection/paint/{id}.html'

    res = requests.get(url)
    # check for successful request
    if res.status_code != 200:
        raise ValueError(f'Encountered error when visiting {url}: {res.status_code}')

    # parse the response text and extract painting info
    html_string = res.text
    soup = BeautifulSoup(html_string, 'html.parser')

    # extract minghuaji id
    links = soup.find_all('a')
    mhj_id = ''
    for link in links:
        if link.get('href') and 'minghuaji.dpm.org.cn/paint' in link.get('href'):
            mhj_id = link.get('href').split('=')[-1]
            break

    # extract inventory number
    scripts = soup.find_all('script')
    inventory_id = ''
    for script in scripts:
        if 'objno' in script.text:
            # fix encoding issue
            try:
                text = script.text.encode('latin-1').decode('utf-8').replace(' ','')
            except:
                text = script.text.replace(' ','')
            inventory_id = re.search('objno="([^"]+?)"', text).group(1)

    # extract details
    info = soup.select_one('.content_edit')
    # fix encoding issue
    try:
        text = info.text.encode('latin-1').decode('utf-8').replace(' ','')
    except:
        text = info.text.replace(' ', '')
    materials = ['绢本', '纸本', '金笺']
    colors = ['设色', '淡设色', '水墨', '墨笔']

    material = ''
    material_match = re.search(f'({"|".join(materials)})[，。]', text)
    if material_match is not None: material = material_match.group(1)

    color = ''
    color_match = re.search(f'[，。]({"|".join(colors)})[，。]', text)
    if color_match is not None: color = color_match.group(1)

    height = ''
    height_match = re.search('[，。]纵([\d\.,]+)厘米', text)
    if height_match is not None: height = float(height_match.group(1).replace(',',''))

    width = ''
    width_match = re.search('[，。]横([\d\.,]+)厘米', text)
    if width_match is not None: width = float(width_match.group(1).replace(',',''))

    print(f'id: {id}, mhj_id: {mhj_id}, inventory_id: {inventory_id}, material: {material}, color: {color}, height: {height}, width: {width}')

    return {
        'mhj_id': mhj_id,
        'inventory_id': inventory_id,
        'material': material,
        'color': color,
        'height': height,
        'width': width
    }

################################################################
## common functions
################################################################

# fetch all pages and save to csv
def fetch_all(website, start_page=1, details=False):
    # read the existing csv if available, otherwise create a new one
    csv_file = 'paintings.csv'
    columns = {
        'mhj': ['id', 'name', 'author', 'dynasty'],
        'collection': ['id', 'name', 'author', 'dynasty', 'category'],
    }
    if not website in columns:
        raise ValueError(f'Unknown website: {website}')

    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
    else:
        df = pd.DataFrame(columns=columns[website])

    # fetch all pages
    if website == 'mhj': xsrf_token = get_xsrf_token()
    page = start_page
    while True:
        print(f'Fetching page {page}...')
        if website == 'mhj':
            paintings = fetch_page_mhj(page, xsrf_token)
        elif website == 'collection':
            paintings = fetch_page_collection(page)

        # reach the end of the list
        if len(paintings) == 0: break

        # append the new paintings to the existing dataframe
        df = pd.concat([df, pd.DataFrame(paintings)], ignore_index=True)

        # next page
        page += 1

    # remove duplicates
    df = df.drop_duplicates(subset=['id'])

    # save the dataframe to csv
    df.to_csv(csv_file, index=False)

    if details: fetch_details(website)

# obtain more details for all paintings
def fetch_details(website):
    # read data
    csv_file = 'paintings.csv'
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
    else:
        raise ValueError(f'Cannot find {csv_file}')

    # create new columns
    columns = {
        'mhj': ['material', 'color', 'height', 'width'],
        'collection': ['mhj_id', 'inventory_id', 'material', 'color', 'height', 'width']
    }
    if not website in columns:
        raise ValueError(f'Unknown website: {website}')

    for col in columns[website]:
        if col not in df.columns: df[col] = ''

    # fetch details for each painting
    for idx, paint_id in df['id'].iteritems():
        if website == 'mhj':
            info = fetch_detail_mhj(paint_id)
        elif website == 'collection':
            info = fetch_detail_collection(paint_id)
        for col in columns[website]:
            df.loc[idx, col] = info[col]

    # save the dataframe to csv
    df.to_csv(csv_file, index=False)


if __name__ == '__main__':
    website = sys.argv[1]
    # start from the specified page
    start_page = int(sys.argv[2]) if len(sys.argv) > 2 else 1

    fetch_all(website=website, start_page=start_page, details=False)