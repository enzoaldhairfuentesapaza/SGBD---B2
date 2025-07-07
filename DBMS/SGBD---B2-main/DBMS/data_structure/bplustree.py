import struct
import pickle
from disk_manager.disk_manager import DiskManager
from config import PAGE_SIZE, ORDER

class BPlusTree:
    def __init__(self, disk_manager, table_name=None):
        self.disk = disk_manager
        self.table_name = table_name or "?"
        self.root_page = self.disk.allocate_page()
        self._write_node(self.root_page, self._create_leaf_node())

    def insert(self, key, record):
        root = self._read_node(self.root_page)
        result = self._insert_into_node(root, key, record, self.root_page)
        if result is not None:
            new_key, left, right = result
            new_root = self._create_internal_node([new_key], [left, right])
            self.root_page = self.disk.allocate_page()
            self._write_node(self.root_page, new_root)

    def search(self, key):
        node = self._read_node(self.root_page)
        while not node["is_leaf"]:
            i = 0
            while i < len(node["keys"]) and key >= node["keys"][i]:
                i += 1
            node = self._read_node(node["children"][i])
        for i, k in enumerate(node["keys"]):
            if k == key:
                return pickle.loads(node["values"][i])
        return None

    def _create_leaf_node(self):
        return {
            "is_leaf": True,
            "keys": [],
            "values": [],
            "next": None
        }

    def _create_internal_node(self, keys, children):
        return {
            "is_leaf": False,
            "keys": keys,
            "children": children
        }

    def _write_node(self, page_id, node):
        data = bytearray(PAGE_SIZE)
        offset = 0

        data[offset] = 1 if node["is_leaf"] else 0
        offset += 1
        data[offset] = len(node["keys"])
        offset += 1

        for key in node["keys"]:
            data[offset:offset+4] = struct.pack("i", key)
            offset += 4

        if node["is_leaf"]:
            for val in node["values"]:
                val_bytes = pickle.dumps(val)
                val_size = len(val_bytes)
                data[offset:offset+4] = struct.pack("i", val_size)
                offset += 4
                data[offset:offset+val_size] = val_bytes
                offset += val_size
            data[offset:offset+4] = struct.pack("i", node["next"] if node["next"] is not None else -1)
        else:
            for child in node["children"]:
                data[offset:offset+4] = struct.pack("i", child)
                offset += 4

        self.disk.write_page(page_id, data)

    def _read_node(self, page_id):
        data = self.disk.read_page(page_id)
        offset = 0
        is_leaf = data[offset] == 1
        offset += 1
        num_keys = data[offset]
        offset += 1

        keys = []
        for _ in range(num_keys):
            key = struct.unpack("i", data[offset:offset+4])[0]
            offset += 4
            keys.append(key)

        if is_leaf:
            values = []
            for _ in range(num_keys):
                val_size = struct.unpack("i", data[offset:offset+4])[0]
                offset += 4
                val_bytes = data[offset:offset+val_size]
                offset += val_size
                values.append(val_bytes)
            next_ptr = struct.unpack("i", data[offset:offset+4])[0]
            return {
                "is_leaf": True,
                "keys": keys,
                "values": values,
                "next": None if next_ptr == -1 else next_ptr
            }
        else:
            children = []
            for _ in range(num_keys + 1):
                child = struct.unpack("i", data[offset:offset+4])[0]
                offset += 4
                children.append(child)
            return {
                "is_leaf": False,
                "keys": keys,
                "children": children
            }

    def _insert_into_node(self, node, key, value, page_id):
        if node["is_leaf"]:
            i = 0
            while i < len(node["keys"]) and key > node["keys"][i]:
                i += 1
            node["keys"].insert(i, key)
            node["values"].insert(i, pickle.dumps(value))

            if len(node["keys"]) > ORDER:
                return self._split_leaf(node, page_id)
            else:
                self._write_node(page_id, node)
                return None
        else:
            i = 0
            while i < len(node["keys"]) and key > node["keys"][i]:
                i += 1
            child_page = node["children"][i]
            child = self._read_node(child_page)
            result = self._insert_into_node(child, key, value, child_page)
            if result is None:
                return None

            new_key, left_page, right_page = result
            node["keys"].insert(i, new_key)
            node["children"][i] = left_page
            node["children"].insert(i+1, right_page)

            if len(node["keys"]) > ORDER:
                return self._split_internal(node, page_id)
            else:
                self._write_node(page_id, node)
                return None

    def _split_leaf(self, node, page_id):
        mid = len(node["keys"]) // 2
        new_node = self._create_leaf_node()
        new_node["keys"] = node["keys"][mid:]
        new_node["values"] = node["values"][mid:]
        node["keys"] = node["keys"][:mid]
        node["values"] = node["values"][:mid]

        new_page = self.disk.allocate_page()
        new_node["next"] = node["next"]
        node["next"] = new_page

        self._write_node(page_id, node)
        self._write_node(new_page, new_node)
        return new_node["keys"][0], page_id, new_page

    def _split_internal(self, node, page_id):
        mid = len(node["keys"]) // 2
        new_node = self._create_internal_node(
            node["keys"][mid+1:],
            node["children"][mid+1:]
        )
        new_key = node["keys"][mid]
        node["keys"] = node["keys"][:mid]
        node["children"] = node["children"][:mid+1]

        new_page = self.disk.allocate_page()
        self._write_node(page_id, node)
        self._write_node(new_page, new_node)
        return new_key, page_id, new_page

    def print_tree(self):
        def _print_page(page_id, level):
            node = self._read_node(page_id)
            indent = "  " * level
            if node['is_leaf']:
                values = [pickle.loads(val) for val in node['values']]
                print(f"{indent}Leaf[{page_id}] Keys: {node['keys']}, Values: {values}")
            else:
                print(f"{indent}Internal[{page_id}] Keys: {node['keys']}")
                for child_id in node['children']:
                    _print_page(child_id, level + 1)
        print("B+ Tree structure:")
        _print_page(self.root_page, 0)
