import requests
import re
from bs4 import BeautifulSoup
import pandas as pd
import os
import sys

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

def fetch_page(page, xsrf_token):
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

# fetch all pages and save to csv
def fetch_all(start_page=1):
    # read the existing csv if available, otherwise create a new one
    csv_file = 'paintings.csv'
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
    else:
        df = pd.DataFrame(columns=['id', 'name', 'author', 'dynasty'])

    # fetch all pages
    xsrf_token = get_xsrf_token()
    page = start_page
    while True:
        print(f'Fetching page {page}...')
        paintings = fetch_page(page, xsrf_token)

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

# obtain more details about a specific painting
def fetch_detail(id):
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


# obtain more details for all paintings
def fetch_details():
    # read data
    csv_file = 'paintings.csv'
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
    else:
        raise ValueError(f'Cannot find {csv_file}')

    # create new columns
    for col in ['material', 'color', 'height', 'width']:
        if col not in df.columns: df[col] = ''

    # fetch details for each painting
    for idx, paint_id in df['id'].iteritems():
        info = fetch_detail(paint_id)
        for col in ['material', 'color', 'height', 'width']:
            df.loc[idx, col] = info[col]

    # save the dataframe to csv
    df.to_csv(csv_file, index=False)

if __name__ == '__main__':
    # start from the specified page
    start_page = int(sys.argv[1]) if len(sys.argv) > 1 else 1

    fetch_all(start_page)
    # fetch_details() # obtain more details