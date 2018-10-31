import os
import urllib.request
import gzip
import shutil

host = 'https://datasets.imdbws.com/'
files = ['title.akas.tsv', 'title.episode.tsv', 'title.ratings.tsv', 'title.basics.tsv']

for file_name in files:
    urllib.request.urlretrieve(host+file_name+'.gz', file_name+'.gz')
    with gzip.open(file_name+'.gz', 'rb') as f_in:
        with open(file_name, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
            os.remove(file_name+'.gz')


