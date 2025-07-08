import os
import json

DATA_DIR = "data"  # ✅ Eliminado el import desde config.py, ahora usa este valor por defecto
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
            raise Exception("La tabla ya existe")
        self.catalog[table_name] = {
            "primary_key": primary_key,
            "columns": columns,
            "root_page": None  # ← esto lo inicializas aquí
        }
        self.save()

    def get_table_schema(self, table_name):
        return self.catalog.get(table_name, None)

    def list_tables(self):
        return list(self.catalog.keys())
