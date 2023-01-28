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

if __name__ == '__main__':
    # start from the specified page
    start_page = int(sys.argv[1]) if len(sys.argv) > 1 else 1

    fetch_all(start_page)