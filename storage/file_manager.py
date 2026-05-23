import struct

HEADER_FORMAT = "4s i ? q"
MAGIC = b'DB01'
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)


class FileManager:
    def __init__(self, filename):
        self.filename = filename
        self.file = open(filename, "a+b")

    def append(self, json_str):
        self.file.seek(0, 2)
        offset = self.file.tell()

        data = json_str.encode("utf-8")
        header = struct.pack(HEADER_FORMAT, MAGIC, len(data), False, -1)

        self.file.write(header)
        self.file.write(data)
        self.file.flush()

        return offset

    def read(self, offset):
        self.file.seek(offset)

        header_data = self.file.read(HEADER_SIZE)
        if not header_data or len(header_data) < HEADER_SIZE:
            return None

        try:
            magic, length, deleted, _ = struct.unpack(HEADER_FORMAT, header_data)
        except:
            return None

        # 🔥 validar magic
        if magic != MAGIC:
            return None

        # 🔥 validar longitud
        if length <= 0 or length > 10000:
            return None

        data = self.file.read(length)

        if deleted:
            return None

        try:
            return data.decode("utf-8")
        except:
            return None

    def mark_deleted(self, offset):
        self.file.seek(offset)

        header_data = self.file.read(HEADER_SIZE)
        magic, length, _, next_free = struct.unpack(HEADER_FORMAT, header_data)

        new_header = struct.pack(HEADER_FORMAT, MAGIC, length, True, next_free)

        self.file.seek(offset)
        self.file.write(new_header)
        self.file.flush()

    def debug(self):
        import struct

        self.file.seek(0)

        while True:
            pos = self.file.tell()
            header_data = self.file.read(HEADER_SIZE)

            # fin de archivo
            if not header_data or len(header_data) < HEADER_SIZE:
                break

            # intentar leer header
            try:
                magic, length, deleted, _ = struct.unpack(HEADER_FORMAT, header_data)
                if magic != MAGIC:
                    print(f"[{pos}] [INVALID MAGIC]")
                    print(f"[{pos}] [INVALID MAGIC] → fin de archivo lógico")
                    break
            except:
                print(f"[{pos}] [CORRUPTED HEADER]")
                break

            if length <= 0 or length > 10000:
                print(f"[{pos}] [INVALID HEADER: length={length}]")
                break

            # leer contenido
            data = self.file.read(length)

            if deleted:
                print(f"[{pos}] (DEL)")
            else:
                try:
                    print(f"[{pos}] {data.decode('utf-8')}")
                except:
                    print(f"[{pos}] [CORRUPTED DATA]")