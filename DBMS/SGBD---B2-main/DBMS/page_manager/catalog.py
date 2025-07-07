import os
import json
from config import DATA_DIR

CATALOG_FILE = os.path.join(DATA_DIR, "catalog.json")

class CatalogManager:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        if not os.path.exists(CATALOG_FILE):
            with open(CATALOG_FILE, "w") as f:
                json.dump({}, f)
        with open(CATALOG_FILE, "r") as f:
            self.catalog = json.load(f)

    def save(self):
        with open(CATALOG_FILE, "w") as f:
            json.dump(self.catalog, f, indent=2)

    def create_table(self, table_name, primary_key, columns):
        if table_name in self.catalog:
            raise Exception(f"La tabla '{table_name}' ya existe.")

        if not any(col["name"] == primary_key for col in columns):
            raise Exception("La clave primaria debe ser uno de los atributos definidos.")

        self.catalog[table_name] = {
            "primary_key": primary_key,
            "columns": columns
        }
        self.save()

    def get_table_schema(self, table_name):
        return self.catalog.get(table_name, None)

    def list_tables(self):
        return list(self.catalog.keys())