import os
import pickle
from page_manager.catalog import CatalogManager
from data_structure.bplustree import BPlusTree
from disk_manager.physical_disk import PhysicalDisk
from disk_manager.physical_adapter import PhysicalDiskAdapter
from disk_manager.disk_manager import DiskManager
from config import PLATOS, PISTAS, SECTORES_POR_PISTA, BYTES_POR_SECTOR

class TableManager:
    def __init__(self):
        self.catalog = CatalogManager()
        self.trees = {}

        # ⚠️ Si el disco no existe, no se inicializa nada (ni error, ni mensaje)
        if not os.path.exists("disco_general.bin"):
            self.disk = None
            return

        self.disk = PhysicalDisk(
            "disco_general.bin",
            platos=PLATOS,
            pistas=PISTAS,
            sectores_por_pista=SECTORES_POR_PISTA,
            bytes_por_sector=BYTES_POR_SECTOR
        )
        self.adapter = PhysicalDiskAdapter(self.disk)
        self.disk_manager = DiskManager(self.adapter)

    def _get_tree(self, table_name):
        if table_name not in self.trees:
            if table_name not in self.catalog.catalog:
                return None
            root = self.catalog.catalog[table_name].get("root_page")
            self.trees[table_name] = BPlusTree(self.disk_manager, table_name, root_page=root)
        return self.trees[table_name]

    def create_table(self, table_name, primary_key, columns):
        if self.disk is None:
            return
        self.catalog.create_table(table_name, primary_key, columns)
        tree = self._get_tree(table_name)
        if tree:
            self.catalog.catalog[table_name]["root_page"] = tree.root_page
            self.catalog.save()

    def insert(self, table_name, record):
        if self.disk is None:
            return
        schema = self.catalog.get_table_schema(table_name)
        if not schema:
            return
        expected_fields = {col["name"] for col in schema["columns"]}
        if set(record.keys()) != expected_fields:
            return
        key = record[schema["primary_key"]]
        tree = self._get_tree(table_name)
        if tree:
            tree.insert(key, record)

    def select(self, table_name, key):
        if self.disk is None:
            return None
        tree = self._get_tree(table_name)
        if not tree:
            return None
        result = tree.search(key)
        return pickle.loads(result) if result else None

    def select_all(self, table_name):
        if self.disk is None:
            return []
        tree = self._get_tree(table_name)
        if not tree:
            return []

        page_id = tree.root_page
        node = tree._read_node(page_id)
        while not node["is_leaf"]:
            page_id = node["children"][0]
            node = tree._read_node(page_id)

        results = []
        while True:
            results.extend([pickle.loads(val) for val in node["values"]])
            if node["next"] is None:
                break
            page_id = node["next"]
            node = tree._read_node(page_id)

        return results

    def list_tables(self):
        return self.catalog.list_tables() if self.disk else []
