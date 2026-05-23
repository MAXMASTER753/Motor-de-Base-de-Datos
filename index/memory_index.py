class MemoryIndex:
    def __init__(self):
        self.index = {}

    def insert(self, key, offset):
        self.index[key] = offset

    def search(self, key):
        return self.index.get(key)

    def delete(self, key):
        if key in self.index:
            del self.index[key]