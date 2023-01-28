import pandas as pd
import subprocess
import os
from generate_dzi import generate_dzi_file, get_info

def download_image(paint_id, info=None, download_largest=False):
    # check if image already exists
    paint_file = f'paintings/{paint_id}.png'
    if os.path.exists(paint_file):
        print(f'Painting {paint_id} already exists.')
        return

    # check if dzi file exists
    dzi_file = f'paintings/{paint_id}.dzi'
    if not os.path.exists(dzi_file):
        generate_dzi_file(paint_id, info=info)

    # dezoomify-rs
    dezoomify = os.environ.get('DEZOOMIFY_RS')
    if dezoomify is None: dezoomify = 'dezoomify-rs'

    command = f'{dezoomify} --dezoomer deepzoom "{dzi_file}" --header "Referer: https://www.dpm.org.cn" --retries 10 {"--largest " if download_largest else ""}{paint_file}'
    subprocess.run(command, shell=True)

def download_all():
    # read painting ids from csv
    df = pd.read_csv('paintings.csv')

    info = get_info()
    for index, row in df.iterrows():
        paint_id = row['id']
        print(f'Painting {paint_id} ({index + 1}/{len(df)}) ...')
        download_image(paint_id, info=info, download_largest=True)

if __name__ == '__main__':
    # create directory if not exists
    if not os.path.exists('paintings'): os.makedirs('paintings')

    download_all()