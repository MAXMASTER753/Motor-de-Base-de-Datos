import json
import struct
from storage.file_manager import FileManager, HEADER_FORMAT, HEADER_SIZE, MAGIC
from engine.bplustree import BPlusTree


class Database:
    def __init__(self, filename):
        self.fm = FileManager(filename)
        self.index = BPlusTree(order=4)
        self.free_list = []

        self.rebuild_index()
        self.rebuild_free_list()

    def rebuild_index(self):
        self.index = BPlusTree(order=4)
        self.fm.file.seek(0)

        while True:
            pos = self.fm.file.tell()
            header_data = self.fm.file.read(HEADER_SIZE)

            if not header_data or len(header_data) < HEADER_SIZE:
                break

            try:
                magic, length, deleted, _ = struct.unpack(HEADER_FORMAT, header_data)

                if magic != MAGIC:
                    break
            except:
                break

            if length <= 0 or length > 10000:
                break

            data = self.fm.file.read(length)

            if deleted:
                continue

            try:
                obj = json.loads(data.decode("utf-8"))
                key = obj["id"]
                self.index.insert(key, pos)
            except:
                pass

    def rebuild_free_list(self):
        self.free_list = []
        self.fm.file.seek(0)

        while True:
            pos = self.fm.file.tell()
            header_data = self.fm.file.read(HEADER_SIZE)

            if not header_data or len(header_data) < HEADER_SIZE:
                break

            try:
                magic, length, deleted, _ = struct.unpack(HEADER_FORMAT, header_data)

                if magic != MAGIC:
                    break
            except:
                break

            if length <= 0 or length > 10000:
                break

            if deleted:
                self.free_list.append((pos, length))

            self.fm.file.seek(length, 1)

    def insert(self, json_str):
        obj = json.loads(json_str)
        key = obj["id"]

        if self.index.search(key) is not None:
            print(f"Error: id {key} ya existe")
            return

        data = json_str.encode("utf-8")

        for i, (pos, block_size) in enumerate(self.free_list):
            if block_size >= len(data):
                self.free_list.pop(i)

                self.fm.file.seek(pos)
                header = struct.pack(HEADER_FORMAT, MAGIC, block_size, False, -1)
                self.fm.file.write(header)
                self.fm.file.write(data)

                remaining = block_size - len(data)
                if remaining > 0:
                    self.fm.file.write(b'\x00' * remaining)

                self.fm.file.flush()

                self.index.insert(key, pos)

                print(f"Inserted (reused) id={key} at offset={pos}")
                return

        offset = self.fm.append(json_str)
        self.index.insert(key, offset)

        print(f"Inserted id={key} at offset={offset}")

    def get(self, key):
        offset = self.index.search(key)

        if offset is None:
            print("Not found")
            return

        data = self.fm.read(offset)

        if data is None:
            print("Record deleted")
            return

        print(data)

    def delete(self, key):
        offset = self.index.search(key)

        if offset is None:
            print("Not found")
            return

        self.fm.mark_deleted(offset)
        self.rebuild_index()

        print(f"Deleted id={key}")

    def update(self, json_str):
        obj = json.loads(json_str)
        key = obj["id"]

        offset = self.index.search(key)

        if offset is None:
            print("No existe")
            return

        self.fm.mark_deleted(offset)

        new_offset = self.fm.append(json_str)

        self.rebuild_index()

        print(f"Updated id={key}")

    def get_all(self, key):
        offsets = self.index.search_all(key)

        if not offsets:
            print("Not found")
            return

        for offset in offsets:
            data = self.fm.read(offset)
            if data:
                print(data)

    def debug(self):
        self.fm.debug()