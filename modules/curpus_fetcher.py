import networkx as nx
import urllib3

from ..modules.own.cache import Cache
from ..modules.own.genius import GeniusCached
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

    song = GeniusCached.song(song_id)

    print('#',i, sep='')
    print('\t',song.url)
    print('\t',song.path)

    filename = '/' + str(song['id']) + '.html'

    if cache.cached(filename) or cache.cached(filename + '.nolyrics'):
        print("\t Already Cached...")

    else:
        response = http.request('GET', song.url,
            headers={'Authorization': 'bearer ' + 'uU0ZxCrlEHi1h204vNJV61g94QX896NMroRVyhQHTqmABPmnyJ5jEgD7wOnQde9Z'}
        )

        if response.status == 200:
            data = str(response.data)

            if str(response.data).find('Lyrics for this song have yet to be released. Please check back once the song has been released.') != -1:
                print("NO LYRICS YET")
                cache.save(data, filename + '.nolyrics')

            else:
                cache.save(data, filename)

        elif response.status == 404:
            if str(response.data).find('The lyrics for this song have yet to be transcribed.') == -1:
                print("NO LYRICS YET")
                data = str(response.data)
                cache.save(data, filename + '.nolyrics')
            else:
                print("Download failed: " + str(response.status) + " - " + response.geturl() + " - " + str(response.data))

        else:
            print("Download failed: " + str(response.status) + " - " + response.geturl() + " - " + str(response.data))
