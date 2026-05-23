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

        # =====================================================
        # SPLIT EN HOJAS (B+ TREE REAL)
        # =====================================================

        if node.leaf:

            # dividir claves
            new_node.keys = node.keys[mid:]
            new_node.children = node.children[mid:]

            node.keys = node.keys[:mid]
            node.children = node.children[:mid]

            # la primera clave del nuevo nodo sube al padre
            promoted_key = new_node.keys[0]

            parent.keys.insert(index, promoted_key)
            parent.children.insert(index + 1, new_node)

            # mantener linked list de hojas
            new_node.next = node.next
            node.next = new_node

        # =====================================================
        # SPLIT EN NODOS INTERNOS
        # =====================================================

        else:

            promoted_key = node.keys[mid]

            new_node.keys = node.keys[mid + 1:]
            new_node.children = node.children[mid + 1:]

            node.keys = node.keys[:mid]
            node.children = node.children[:mid + 1]

            parent.keys.insert(index, promoted_key)
            parent.children.insert(index + 1, new_node)

    # 🔹 búsqueda de todos los duplicados
    def search_all(self, key):

        node = self.root

        # =================================================
        # BAJAR HASTA LA HOJA MÁS A LA IZQUIERDA POSIBLE
        # =================================================

        while not node.leaf:

            i = 0

            # IMPORTANTE:
            # usar > en vez de >=
            while i < len(node.keys) and key > node.keys[i]:
                i += 1

            node = node.children[i]

        # =================================================
        # BUSCAR DUPLICADOS
        # =================================================

        results = []

        while node:

            for i, k in enumerate(node.keys):

                if k == key:
                    results.append(node.children[i])

                elif k > key:
                    return results

            node = node.next

        return results