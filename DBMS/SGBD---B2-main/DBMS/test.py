from disk_manager.physical_disk import PhysicalDisk
from disk_manager.physical_adapter import PhysicalDiskAdapter

disk = PhysicalDisk("disco_virtual.data", platos=1, pistas=10, sectores_por_pista=20, bytes_por_sector=512)
adapter = PhysicalDiskAdapter(disk)

adapter.mostrar_mapa_ocupacion(10)  # Muestra mapa para las primeras 10 páginas
adapter.visualizar_todas_las_paginas(5)  # Muestra detalle completo para las 5 primeras