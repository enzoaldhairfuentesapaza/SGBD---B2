from disk_manager.physical_adapter import PhysicalDiskAdapter

class DiskManager:
    def __init__(self, adapter):  # Ahora recibe el adaptador
        self.adapter = adapter
        self.page_counter = 0

    def read_page(self, page_id):
        return self.adapter.read_page(page_id)

    def write_page(self, page_id, data):
        self.adapter.write_page(page_id, data)
    def allocate_page(self):
        page_id = self.page_counter
        self.adapter.write_page(page_id, b'\x00' * self.adapter.bytes_por_sector)
        self.page_counter += 1
        return page_id
    def listar_paginas(self):
        print(">> DIR >> Páginas lógicas almacenadas:")
        for page_id in range(self.page_counter):
            print(f"  Página lógica {page_id}")



'''import os
from config import PAGE_SIZE, DATA_DIR

class DiskManager:
    def __init__(self, table_name):
        self.file_path = os.path.join(DATA_DIR, f"{table_name}.data")
        os.makedirs(DATA_DIR, exist_ok=True)
        if not os.path.exists(self.file_path):
            open(self.file_path, "wb").close()

    def read_page(self, page_id):
        with open(self.file_path, "rb") as f:
            f.seek(page_id * PAGE_SIZE)
            return f.read(PAGE_SIZE)

    def write_page(self, page_id, data):
        assert len(data) == PAGE_SIZE
        with open(self.file_path, "r+b") as f:
            f.seek(page_id * PAGE_SIZE)
            f.write(data)

    def allocate_page(self):
        with open(self.file_path, "ab") as f:
            f.write(bytes(PAGE_SIZE))
        size = os.path.getsize(self.file_path)
        if size == 0 or size % PAGE_SIZE != 0:
            raise Exception("Archivo dañado o PAGE_SIZE incorrecto")
        return (size // PAGE_SIZE) - 1'''
