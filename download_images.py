import pandas as pd
import subprocess
import os
import sys
import re
import glob
from generate_dzi import generate_dzi_file, get_info

def download_image(website, paint_id, info=None, download_largest=True):
    # check if dzi files exist
    # note that there may be multiple dzi files for an album
    dzi_files = glob.glob(f'paintings/{paint_id}*.dzi')
    if len(dzi_files) == 0:
        try:
            generate_dzi_file(website, paint_id, info=info)
        except Exception as e:
            print(f'Failed to generate dzi files for painting {paint_id}: {e}')
            # clean files
            dzi_files = glob.glob(f'paintings/{paint_id}*.dzi')
            for dzi_file in dzi_files: os.remove(dzi_file)
            return

    dzi_files = glob.glob(f'paintings/{paint_id}*.dzi')
    format = re.search('Format="(\w+)"', open(dzi_files[0], 'r').read()).group(1)

    for dzi_file in dzi_files:
        paint_file = dzi_file.replace('.dzi', f'.{format}')

        # check if image already exists
        if os.path.exists(paint_file):
            print(f'Painting {paint_file} already exists.')
            continue

        # dezoomify-rs
        dezoomify = os.environ.get('DEZOOMIFY_RS')
        if dezoomify is None: dezoomify = 'dezoomify-rs'

        command = f'{dezoomify} --dezoomer deepzoom "{dzi_file}" --header "Referer: https://www.dpm.org.cn" --retries 1 {"--largest " if download_largest else ""}{paint_file}'
        subprocess.run(command, shell=True)

def download_all(website):
    # read painting ids from csv
    df = pd.read_csv('paintings.csv')

    info = get_info()
    for index, row in df.iterrows():
        paint_id = row['id']
        print(f'Painting {paint_id} ({index + 1}/{len(df)}) ...')
        download_image(website, paint_id, info=info, download_largest=True)

if __name__ == '__main__':
    website = sys.argv[1]

    # create directory if not exists
    if not os.path.exists('paintings'): os.makedirs('paintings')

    download_all(website)