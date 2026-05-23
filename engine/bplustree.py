class Node:
    def __init__(self, leaf=False):
        self.leaf = leaf
        self.keys = []
        self.children = []
        self.next = None


class BPlusTree:
    def __init__(self, order=3):  # 🔥 grado 3
        self.root = Node(leaf=True)
        self.order = order

    # 🔹 búsqueda
    def search(self, key, node=None):
        if node is None:
            node = self.root

        if node.leaf:
            for i, k in enumerate(node.keys):
                if k == key:
                    return node.children[i]
            return None

        # 🔥 duplicados → derecha
        for i, k in enumerate(node.keys):
            if key < k:
                return self.search(key, node.children[i])

        return self.search(key, node.children[-1])

    # 🔹 inserción
    def insert(self, key, value):
        root = self.root

        if len(root.keys) == self.order - 1:
            new_root = Node()
            new_root.children.append(self.root)
            self.split_child(new_root, 0)
            self.root = new_root

        self._insert_non_full(self.root, key, value)

    def _insert_non_full(self, node, key, value):
        if node.leaf:
            i = 0

            # 🔥 duplicados → derecha
            while i < len(node.keys) and node.keys[i] < key:
                i += 1

            node.keys.insert(i, key)
            node.children.insert(i, value)

        else:
            i = 0

            # 🔥 duplicados → derecha
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1

            if len(node.children[i].keys) == self.order - 1:
                self.split_child(node, i)

                # 🔥 después del split decidir dirección correcta
                if key >= node.keys[i]:
                    i += 1

            self._insert_non_full(node.children[i], key, value)

    # 🔹 split
    def split_child(self, parent, index):
        node = parent.children[index]
        mid = len(node.keys) // 2

        new_node = Node(leaf=node.leaf)

        # 🔥 subir clave media
        parent.keys.insert(index, node.keys[mid])
        parent.children.insert(index + 1, new_node)

        # 🔹 dividir claves
        new_node.keys = node.keys[mid + 1:]
        node.keys = node.keys[:mid]

        if node.leaf:
            # 🔹 en hojas: los datos se reparten distinto
            new_node.children = node.children[mid:]
            node.children = node.children[:mid]

            # 🔥 mantener enlaces
            new_node.next = node.next
            node.next = new_node
        else:
            new_node.children = node.children[mid + 1:]
            node.children = node.children[:mid + 1]


    # 🔹 búsqueda de todos los duplicados
    def search_all(self, key):
        node = self.root

        # 🔹 1. bajar hasta hoja
        while not node.leaf:
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            node = node.children[i]

        # 🔹 2. buscar primer match dentro de la hoja
        results = []
        i = 0

        while i < len(node.keys) and node.keys[i] < key:
            i += 1

        # 🔹 3. recolectar duplicados en hojas consecutivas
        while node:
            while i < len(node.keys) and node.keys[i] == key:
                results.append(node.children[i])
                i += 1

            # si ya no hay más en esta hoja → ir a la siguiente
            if i < len(node.keys):
                break

            node = node.next
            i = 0

        return results