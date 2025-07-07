from disk_manager.physical_disk import PhysicalDisk
from config import PAGE_SIZE
class PhysicalDiskAdapter:
    def __init__(self, disk: PhysicalDisk):
        self.disk = disk
        self.sectores_por_cara = disk.pistas * disk.sectores
        self.bytes_por_sector = disk.bytes_por_sector
        self.page_size = PAGE_SIZE 
        self.sectores_por_pagina = self.page_size // self.bytes_por_sector

    def _map_page_id(self, page_id):
        # Devuelve el (cara, pista, sector) del primer sector de la página
        sector_inicio = page_id * self.sectores_por_pagina
        cara = sector_inicio // self.sectores_por_cara
        resto = sector_inicio % self.sectores_por_cara
        pista = resto // self.disk.sectores
        sector = resto % self.disk.sectores
        return cara, pista, sector

    def write_page(self, page_id, data: bytes):
        if len(data) != self.page_size:
            raise ValueError(f"Page size debe ser {self.page_size} bytes")
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
    def visualizar_page_sectores(self, page_id):
        cara, pista, sector = self._map_page_id(page_id)
        sectores = []

        for i in range(self.sectores_por_pagina):
            s = sector + i
            p = pista + s // self.disk.sectores
            s = s % self.disk.sectores
            c = cara + p // self.disk.pistas
            p = p % self.disk.pistas

            if c >= self.disk.caras:
                raise ValueError("La página excede el espacio disponible del disco")

            sectores.append((c, p, s))

        print(f">> PAGE >> Página lógica {page_id} ocupa los sectores físicos:")
        for i, (c, p, s) in enumerate(sectores):
            print(f"  Sector {i + 1}: Cara {c}, Pista {p}, Sector {s}")
    def mostrar_mapa_ocupacion(self, total_paginas):
        print(">> MAP >> Mapa de ocupación del disco (por página lógica):")
        for page_id in range(total_paginas):
            sectores = []
            cara, pista, sector = self._map_page_id(page_id)
            for i in range(self.sectores_por_pagina):
                s = sector + i
                p = pista + s // self.disk.sectores
                s = s % self.disk.sectores
                c = cara + p // self.disk.pistas
                p = p % self.disk.pistas
                sectores.append(f"(C{c},P{p},S{s})")
            print(f"  Página {page_id:3} → {', '.join(sectores)}")
    def visualizar_todas_las_paginas(self, total_paginas):
        print(">> DIR >> Visualización detallada de todas las páginas:")
        for page_id in range(total_paginas):
            self.visualizar_page_sectores(page_id)
