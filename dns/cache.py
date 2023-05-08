import pickle
import time


class Cache:
    def __init__(self):
        self.cache = dict()

    def save_cache(self, path):
        with open(path, "wb") as dump:
            pickle.dump(self.cache, dump)

    def load_cache(self, path):
        try:
            with open(path, "rb") as dump:
                data = pickle.load(dump)
                for key, (rdata, ttl) in data.items():
                    if time.time() < ttl:
                        self.cache[key] = (rdata, ttl)
        except FileNotFoundError:
            pass

    def update_cache(self, key, records, ttl):
        total_ttl = time.time() + ttl
        self.cache[key] = (records, total_ttl)

    def get_cache(self, key):
        data = self.cache.get(key)
        if data is None:
            return
        rdata, ttl = data
        if time.time() > ttl:
            del self.cache[key]
        return rdata
