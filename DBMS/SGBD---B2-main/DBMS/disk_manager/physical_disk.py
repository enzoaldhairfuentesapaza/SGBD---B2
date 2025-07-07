import os
from config import DATA_DIR

class PhysicalDisk:
    def __init__(self, nombre, platos, pistas, sectores_por_pista, bytes_por_sector):
        self.file_path = nombre
        self.platos = platos
        self.caras = platos * 2
        self.pistas = pistas
        self.sectores = sectores_por_pista
        self.bytes_por_sector = bytes_por_sector
        self.total_bytes = (self.platos * self.pistas * self.sectores * bytes_por_sector)
        if not os.path.exists(nombre): #Crea un archivo si este no existe
            with open(nombre, 'wb') as f:
                f.write(b'\x00' * self.total_bytes)


    def _offset(self, cara, pista, sector):
        if not (0 <= cara < self.caras and 0 <= pista < self.pistas and 0 <= sector < self.sectores):
            raise ValueError("Coordenadas fuera de rango")
        return ((cara * self.pistas * self.sectores) +
                (pista * self.sectores) + 
                (sector)) * self.bytes_por_sector

    def write_sector(self, cara, pista, sector, data: bytes):
        if len(data) > self.bytes_por_sector:
            raise ValueError("Tamaño excede el de un sector")
        data = data.ljust(self.bytes_por_sector, b'\x00')
        with open(self.file_path, 'r+b') as f:
            f.seek(self._offset(cara, pista, sector))
            f.write(data)

    def read_sector(self, cara, pista, sector):
        with open(self.file_path, 'rb') as f:
            f.seek(self._offset(cara, pista, sector))
            return f.read(self.bytes_por_sector)
