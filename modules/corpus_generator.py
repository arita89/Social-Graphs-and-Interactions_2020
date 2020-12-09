import networkx as nx
import urllib3
import re
from bs4 import BeautifulSoup

from ..modules.own.cache import Cache
from ..modules.own.graph_utils import *

import setup


cache = Cache('../data/cache/lyrics')
corpus = Cache('../data/corpus')

http = urllib3.PoolManager()


#
# Reload graph
#
B = nx.read_gpickle('../data/graph.pickle')

all_songs = list(get_bipartite_nodes(B, 1))


for i, song_id in enumerate(all_songs):

    song_id = song_id[2:]
#        song_id = '1177689'

    print('#', i, ': ', song_id, sep='', end='')

    data_filename = '/' + str(song_id) + '.html'
    corpus_filename = '/' + str(song_id) + '.txt'

    if corpus.cached(corpus_filename):
        print("   Already Cached...")

    else:
        print()

        if cache.cached(data_filename + '.nolyrics'):
            print("\t\t\tNo lyrics for song #%s" % song_id)
            continue

        if not cache.cached(data_filename):
            print('\t\t\tNot already cached: #', song_id, sep='')
#           raise Exception('Not already cached:', song_id, '  -  ', data_filename)
            continue

        data = cache.load(data_filename, mode='r')

        html = BeautifulSoup(data, "html.parser")

        # Scrape the song lyrics from the HTML
        node = html.find("div", class_="lyrics")
        if node is None:
            node = html.find("div", class_=re.compile(r'^Lyrics__Container'))

        if node is None:
            print('\t\t\tUPS !!!!!!')
#           print(data)

        else:
            text = node.get_text(separator="\n", strip=False)

            if True:  # Change to test if text contains stuff like  \\n
                text = re.sub(r'\n\\n', '\n', text)
                text = re.sub(r'\\n\\n', '\n', text)
                text = re.sub(r'\\n\s\\n', '\n', text)
                text = re.sub(r'\\n', '\n', text)
                text = re.sub(r"\\'", "'", text)
                text = re.sub(r"\n\[", "\n\n[", text)

            text = text.strip(' \t\n')
#           print(text)

            corpus.save(text, corpus_filename)
