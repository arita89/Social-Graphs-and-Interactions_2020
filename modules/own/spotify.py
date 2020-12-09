from __future__ import annotations

import json
import sys

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials  # To access authorised Spotify data

from own.cache import Cache


class SpotifyCached(spotipy.Spotify):

    debug = False

    # Simply mirror super's constructor...
    def __init__(
        self,
        auth=None,
        requests_session=True,
        client_credentials_manager=None,
        oauth_manager=None,
        auth_manager=None,
        proxies=None,
        requests_timeout=5,
        status_forcelist=None,
        retries=spotipy.Spotify.max_retries,
        status_retries=spotipy.Spotify.max_retries,
        backoff_factor=0.3,
        language=None
    ):
        super().__init__(
            auth,
            requests_session,
            client_credentials_manager,
            oauth_manager,
            auth_manager,
            proxies,
            requests_timeout,
            status_forcelist,
            retries,
            status_retries,
            backoff_factor,
            language
        )

    indent = None

    _cache = Cache('')

    @classmethod
    def get_cache(cls):
        return cls._cache

    @classmethod
    def set_cache_location(cls, location):
        cls._cache = Cache(location)

    def track(self, track_id):

        filename = 'track/' + track_id + '.json'

        # If already caches, just load the data
        if self.get_cache().cached(filename):
            try:
                data = json.loads(self.get_cache().load(filename))

            except json.decoder.JSONDecodeError as error:
                print(error)
                print(filename)
                sys.exit(3)

        # Otherwise fetch, store and pass on data
        else:
            if self.debug:
                print("[ Fetching {} (not cached) {} ]".format(track_id, filename))
            data = super().track(track_id)
            self._cache.save(json.dumps(data, indent=self.indent), filename)

        return data

    def artist(self, artist_id):

        filename = 'artist/' + str(artist_id) + '.json'

        # If already caches, just load the data
        if self.get_cache().cached(filename):
            try:
                data = json.loads(self.get_cache().load(filename))

            except json.decoder.JSONDecodeError as error:
                print(error)
                print(filename)
                sys.exit(3)

        # Otherwise fetch, store and pass on data
        else:
            if self.debug:
                print("[ Fetching {} (not cached) {} ]".format(artist_id, filename))
            data = super().artist(artist_id)
            self._cache.save(json.dumps(data, indent=self.indent), filename)

        return data


    def playlist(self, playlist_id, fields=None, market=None, additional_types=("track",)):

        filename = 'playlist/' + playlist_id + '.json'

        # If already caches, just load the data
        if self.get_cache().cached(filename):
            try:
                data = json.loads(self.get_cache().load(filename))

            except json.decoder.JSONDecodeError as error:
                print(error)
                print(filename)
                sys.exit(3)

        # Otherwise fetch, store and pass on data
        else:
            if self.debug:
                print("[ Fetching {} (not cached) {} ]".format(playlist_id, filename))
            data = super().playlist(playlist_id, fields, market, additional_types=additional_types)
            self._cache.save(json.dumps(data, indent=self.indent), filename)

        return data


class SpotifyFactory:

    _client_id = None
    _client_secret = None
    _caching = True

    def __init__(self):
        raise Exception("Don't do this!")

    @classmethod
    def set_identity(cls, client_id = None, client_secret = None):
        cls._client_id = client_id
        cls._client_secret = client_secret

    @classmethod
    def set_caching(cls, caching = True):
        cls._caching = caching

    @classmethod
    def create(cls):

        client_credentials_manager = SpotifyClientCredentials(client_id=cls._client_id, client_secret=cls._client_secret)

        # Determine to cache or not
        clazz = SpotifyCached if cls._caching else spotipy.Spotify

        # Initialize the chosen class
        return clazz(client_credentials_manager=client_credentials_manager)  # spotify object to access API
