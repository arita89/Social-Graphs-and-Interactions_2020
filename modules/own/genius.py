from __future__ import annotations

import json
import sys

import urllib3
from typing import Type

# Internal class
from own.cache import Cache


class DownloadFailedException(Exception):
    pass


class _GeniusBaseThing:

    _nickname = '_OVERRIDE_'
    _repository = '_OVERRIDE_'
    _cache_dir = '_OVERRIDE_'
    _cache_file = '_OVERRIDE_'

    @staticmethod
    def create_from_dicts(params, variables, data=None):
        raise Exception("Should be overridden!")

    def __init__(self):
        self._data = {}

    def __getattr__(self, variable):
        if variable in self._data:
            return self._data[variable]
        raise AttributeError

    def __getitem__(self, variable):
        if variable not in self._data:
            raise IndexError
        return self._data[variable]

    def __dir__(self):
        dir = list(super().__dir__())
        dir.extend(self._data.keys())
        return dir


class _GeniusBaseThing2(_GeniusBaseThing):

    def __init__(self, id):
        super().__init__()
        self._data.update({
            'id': id
        })

    def id(self):
        return self._data['id']


class Search(_GeniusBaseThing):

    _nickname = 'search'
    _repository = '/search'
    _cache_dir = 'search'
    _cache_file = '{q}.json'

    def __init__(self, query):
        super().__init__()
        self._data.update({
            'query': query
        })

    @classmethod
    def create_from_dicts(cls, params, variables, data=None):
        return cls._create(variables['q'], data)

    @classmethod
    def _create(cls, query, data=None):
        obj = Search(query)

        if data is not None:
            data = data['hits']
            obj._data.update({
                'hits': cls._unfold_hits(data),
            })

        return obj

    @staticmethod
    def _unfold_hits(data):
        hits = []
        for hit in data:

            # Convert song into object
            if hit['type'] == 'song':
                hits.append(Song.create_from_dicts(
                    {},
                    {'id': hit['result']['id']},
                    {'song': hit['result']}
                ))

            # What is this???
            else:
                hits.append(hit)

        return hits

    def hits(self):
        return self['hits']


class Artist(_GeniusBaseThing2):

    _nickname = 'artist'
    _repository = '/artists/{id}'
    _cache_dir = 'artist'
    _cache_file = '{id}.json'

    def __repr__(self):
        return '[Artist #{}: "{}"]'.format(self._data['id'], self._data['name'])

    @classmethod
    def create_from_dicts(cls, params, variables, data=None):
        return cls._create(variables['id'], data)

    @classmethod
    def _create(cls, id, data=None):
        obj = Artist(id)

        if data is not None:
            data = data['artist']
            obj._data.update({
                #'id': data['id'],
                'name': data['name'],
                'alternate_names': data['alternate_names'],
                'facebook_name': data['facebook_name'],
                'twitter_name': data['twitter_name'],
                'url': data['url'],
                'description': 'TODO?',
                'description_annotation': 'TODO?',
            })
        return obj


class _ArtistSongsPage(_GeniusBaseThing2):

    _nickname = 'songs'
    _repository = '/artists/{id}/songs'
    _cache_dir = 'artists-songs'
    _cache_file = '{id}-{page}.json'

    def __init__(self, id, page=1, per_page=50):
        super().__init__(id)
        self._data.update({
            'page': page,
            'per_page': per_page,
        })

    @classmethod
    def create_from_dicts(cls, params, variables, data=None):
        return cls._create(variables['id'], params['page'], params['per_page'], data)

    @classmethod
    def _create(cls, id, page=1, per_page=50, data=None):
        obj = _ArtistSongsPage(id, page, per_page)

        if data is not None:
            obj._data.update({
                'songs': [Song._create(song['id'], {'song': song}) for song in data['songs']],
                'next_page': data['next_page'],
            })

        return obj


class ArtistSongs(_GeniusBaseThing2):

# These are now used in the *Page class, so change or remove or something
#    _nickname = 'songs'
#    _repository = '/artists/{id}/songs'
#    _cache_dir = 'artists-songs'
#    _cache_file = '{id}-{page}.json'

    def __repr__(self):
        return '[Artist #{} has {} songs]'.format(self['id'], len(self['songs']))

    @classmethod
    def create_from_dicts(cls, params, variables, data=None):
        return cls._create(variables['id'], data)

    @classmethod
    def _create(cls, id, data=None):
        obj = ArtistSongs(id)

# TODO: Temporary hack
        obj._data.update({
            'songs': [],
        })

        if data is not None:
            data = data['songs']
            obj._data.update({
                'songs': data, #[Song.create(song['id'], {'song': song}) for song in data]
#                'songs': [Song.create(song['id'], {'song': song}) for song in data]
            })

        return obj


class Song(_GeniusBaseThing2):

    _nickname = 'song'
    _repository = '/songs/{id}'
    _cache_dir = 'songs'
# TODO: Add per_page and sort to the string (but first when filenames are changed)
    _cache_file = '{id}.json'

    def __repr__(self):
        return '[Song #{}: "{}" by "{}" (#{})]'.format(self['id'], self['title'], self['primary_artist_name'], self['primary_artist_id'])

    @classmethod
    def create_from_dicts(cls, params, variables, data=None):
        return cls._create(variables['id'], data)

    @classmethod
    def _create(cls, id, data=None):
        obj = Song(id)

        if data is not None:
            data = data['song']
            obj._data.update({
                "title":               data['title'],
                "title_with_featured": data['title_with_featured'],
                "full_title":          data['full_title'],
            })
            if 'album' in data and data['album'] is not None:
                obj._data.update({
                    "album_id":            data['album']['id'],
                    "album_name":          data['album']['name'],
                    "album_artist_id":     data['album']['artist']['id'],
                    "album_artist_name":   data['album']['artist']['name'],
                })
            obj._data.update({
                "release_date":        data['release_date'] if 'release_date' in data else None,

                "primary_artist_id":   data['primary_artist']['id'],
                "primary_artist_name": data['primary_artist']['name'],

                "featured_artists":    cls._unfold_artists(data, 'featured_artists'),
                "producer_artists":    cls._unfold_artists(data, 'producer_artists'),
                "writer_artists":      cls._unfold_artists(data, 'writer_artists'),

                "path":                data['path'],
                "url":                 data['url'],

                "lyrics_owner_id":     data['lyrics_owner_id'],

                "relationships":       cls._unfold_relationships(data),
                "custom_performances": cls._unfold_custom_performances(data),

                "spotify_track_id":    cls._find_spotify_track(data),

                'description': 'TODO?',
                'description_annotation': 'TODO?',
            })
        return obj

    @staticmethod
    def _unfold_artists(data, name):
        return {artist['id']: artist['name'] for artist in (data[name] if name in data else [])}

    @staticmethod
    def _unfold_relationships(data):
        if 'song_relationships' not in data:
            return []

        relationships = {}
        for type in data['song_relationships']:
            songs = []
            for song in type['songs']:
                songs.append(song['id'])

            relationships[type['relationship_type']] = songs if len(songs) > 0 else None

        return relationships

    @staticmethod
    def _unfold_custom_performances(data):
        if 'custom_performances' not in data:
            return []

        relationships = {}
        for type in data['custom_performances']:
            artists = {}
            for artist in type['artists']:
                artists[artist['id']] = artist['name']

            relationships[type['label']] = artists if len(artists) > 0 else None

        return relationships

    @staticmethod
    def _find_spotify_track(data):
        if 'media' not in data:
            return None

        for media in data['media']:
            if media['provider'] == 'spotify' and media['type'] == 'audio':
                # Remove the 'spotify:track:' prefix
                return media['native_uri'].split(':')[2]

        return None


class Genius:

    _base_url = 'https://api.genius.com'
    _token = 'ToKeN'
    _http = urllib3.PoolManager()

    debug = False

    def __init__(self):
        raise Exception("Nah, don't do that...")

    @classmethod
    def set_token(cls, token):
        cls._token = token

    @classmethod
    def _request(cls, path, params = None, variables = None, headers=None):
        # Add authentication header (and potentially overwrite)
        headers.update({
            # Add OAuth authentication
            'Authorization': 'bearer %s' % cls._token
        })
        # Do the request
        return cls._http.request(
            'GET',
            cls._base_url + path.format(path, **variables),  # TODO, what is this first path parameter in format()???
            fields = params,
            headers = headers
        )

    @classmethod
    def _request2(cls, clazz: Type[_GeniusBaseThing], params, variables, headers):

        response = cls._request(
            clazz._repository,
            params = params,
            variables = variables,
            headers = headers,
        )

        if response.status != 200:
            raise DownloadFailedException("Download failed: " + str(response.status) + " - " + response.geturl() + " - "+ str(response.data))

        # Decode the response
        data = json.loads(response.data)
        # Add the http response headers to the json content
        data['headers'] = dict(response.headers)

        return data

    @classmethod
    def _request3(cls, clazz: Type[_GeniusBaseThing], params, variables, headers):

        data = cls._request2(clazz, params, variables, headers)

        # Create new instance of given class
        return clazz.create_from_dicts(params, variables, data['response'])

    @classmethod
    def search(cls, query, clazz: Type[Search] = Search):
        params = {'q': query}
        variables = {'q': query}
        return cls._request3(clazz, params, variables, headers={})

    @classmethod
    def artist(cls, artist_id, clazz: Type[Artist] = Artist):
        params = {'text_format': 'html'}  # options: 'dom' (default), 'plain', and 'html'
        variables = {'id': artist_id}
        return cls._request3(clazz, params, variables, headers={})

    @classmethod
    def songs(cls, artist_id, max_pages = 100, sort='title', per_page=50, clazz: Type[ArtistSongs] = ArtistSongs):
        page_num = 1

        pages = []
        while True:
            if cls.debug:
                print("page", page_num)

            params = {'page': page_num, 'per_page': per_page, 'sort': sort}
            variables = {'id': artist_id, 'page': page_num, 'per_page': per_page, 'sort': sort}

            page_object = cls._request3(_ArtistSongsPage, params, variables, headers={})

            pages.append(page_object)

            if page_num >= max_pages:
                break
            if page_object['next_page'] is None:
                break

            page_num = page_object['next_page']

        songs = []
        for page in pages:
            for song in page['songs']:
                songs.append(song)

# TODO: CHECK!
        obj = clazz._create(artist_id, {'songs': songs})

        return obj

    @classmethod
    def song(cls, song_id, clazz: Type[Song] = Song):
        params = {'text_format': 'html'}  # options: 'dom' (default), 'plain', and 'html'
        variables = {'id': song_id}
        return cls._request3(clazz, params, variables, headers={})


class GeniusCached(Genius):

    # When saving locally, do json indentation of this number of spaces
    # (or keep compressed when None)
    indent = None

    _cache = Cache('')

    @classmethod
    def get_cache(cls):
        return cls._cache

    @classmethod
    def set_cache_location(cls, location):
        cls._cache = Cache(location)

    @classmethod
    def _request2(cls, clazz: Type[_GeniusBaseThing], params, variables, headers):

        filename = (clazz._cache_dir + '/' + clazz._cache_file).format(**variables)

        # If already caches, just load the data
        if cls.get_cache().cached(filename):
            try:
                data = json.loads(cls.get_cache().load(filename))

            except json.decoder.JSONDecodeError as error:
                print(error)
                print(filename)
                sys.exit(3)

        # Otherwise fetch, store and pass on data
        else:
            if cls.debug:
                print("[ Fetching {} (not cached) {} ]".format(clazz.__name__, filename))

            data = super()._request2(clazz, params, variables, headers)

            cls._cache.save(json.dumps(data, indent=cls.indent), filename)

        return data
