from disk_manager.physical_disk import PhysicalDisk


class PhysicalDiskAdapter:
    def __init__(self, disk: PhysicalDisk, sectores_por_pagina=1):
        self.disk = disk
        self.sectores_por_pagina = sectores_por_pagina  # ⚠️ Configurable
        self.bytes_por_sector = disk.bytes_por_sector
        self.page_size = self.sectores_por_pagina * self.bytes_por_sector
        self.sectores_por_cara = disk.pistas * disk.sectores

    def _map_page_id(self, page_id):
        sector_inicio = page_id * self.sectores_por_pagina
        cara = sector_inicio // self.sectores_por_cara
        resto_pista = sector_inicio % self.sectores_por_cara
        pista = resto_pista // self.disk.sectores
        resto_sector = resto_pista % self.disk.sectores
        return cara, pista, resto_sector

    def write_page(self, page_id, data: bytes):
        if len(data) != self.page_size:
            raise ValueError(f"ERROR: Tamaño de página debe ser {self.page_size} bytes")
        cara, pista, sector = self._map_page_id(page_id)

        for i in range(self.sectores_por_pagina):
            offset = i * self.bytes_por_sector
            chunk = data[offset:offset + self.bytes_por_sector]
            s = sector + i
            p = pista + s // self.disk.sectores
            s = s % self.disk.sectores
            c = cara + p // self.disk.pistas
            p = p % self.disk.pistas
            if c >= self.disk.caras:
                raise ValueError("Disco lleno o page_id demasiado grande")
            self.disk.write_sector(c, p, s, chunk)

    def read_page(self, page_id):
        cara, pista, sector = self._map_page_id(page_id)
        result = bytearray(self.page_size)
        for i in range(self.sectores_por_pagina):
            s = sector + i
            p = pista + s // self.disk.sectores
            s = s % self.disk.sectores
            c = cara + p // self.disk.pistas
            p = p % self.disk.pistas
            if c >= self.disk.caras:
                raise ValueError("Lectura fuera del disco")
            chunk = self.disk.read_sector(c, p, s)
            offset = i * self.bytes_por_sector
            result[offset:offset + self.bytes_por_sector] = chunk
        return bytes(result)
