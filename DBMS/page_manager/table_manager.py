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

    def _get_tree(self, table_name):
        if table_name not in self.trees:
            if table_name not in self.catalog.catalog:
                raise Exception(f"La tabla '{table_name}' no está registrada.")
            
            # Crear el disco y adaptador
            disk = PhysicalDisk(
                table_name,
                platos=PLATOS,
                pistas=PISTAS,
                sectores_por_pista=SECTORES_POR_PISTA,
                bytes_por_sector=BYTES_POR_SECTOR
            )
            adapter = PhysicalDiskAdapter(disk)
            disk_manager = DiskManager(adapter)

            # Obtener root_page guardado
            root = self.catalog.catalog[table_name].get("root_page")

            # Crear árbol con root_page persistente
            self.trees[table_name] = BPlusTree(disk_manager, table_name, root_page=root)
        return self.trees[table_name]


    def create_table(self, table_name, primary_key, columns):
        self.catalog.create_table(table_name, primary_key, columns)
        
        tree = self._get_tree(table_name)
        
        # Guardar root_page recién asignado
        self.catalog.catalog[table_name]["root_page"] = tree.root_page
        self.catalog.save()

    def insert(self, table_name, record):
        schema = self.catalog.get_table_schema(table_name)
        if not schema:
            raise Exception(f"Tabla '{table_name}' no existe.")
        
        # Validar que estén todos los campos
        expected_fields = {col["name"] for col in schema["columns"]}
        if set(record.keys()) != expected_fields:
            raise Exception(f"Los campos del registro no coinciden con el esquema: {expected_fields}")

        key = record[schema["primary_key"]]
        tree = self._get_tree(table_name)
        tree.insert(key, record)

    def select (self, table_name, key):
        tree = self._get_tree(table_name)
        result = tree.search(key)
        return result 

    def list_tables(self):
        return self.catalog.list_tables()
