from __future__ import annotations

from pathlib import Path


class Cache:

    def __init__(self, directory):
        self._directory = directory
        # Ensure cache directory exists
        Path(self._directory).mkdir(parents=True, exist_ok=True)

    def save(self, data, filename, mode='w'):
        with open(self._directory + filename, mode) as outfile:
            outfile.write(data)
            outfile.close()

    def load(self, filename, mode='r', encoding=None):
        if not self.cached(filename):
            raise Exception("Should have been cached by now!")

        with open(self._directory + filename, mode=mode, encoding=encoding) as infile:
            data = infile.read()
            infile.close()

        return data

    def cached(self, filename) -> bool:
        return Path(self._directory + filename).exists()

    def purge(self, filename) -> None:
        raise Exception("Not implemented yet")

