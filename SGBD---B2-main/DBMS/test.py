from disk_manager.physical_disk import PhysicalDisk
from disk_manager.physical_adapter import PhysicalDiskAdapter
from disk_manager.disk_manager import DiskManager
from data_structure.bplustree import BPlusTree


disk = PhysicalDisk("disco_virtual.data", platos=1, pistas=10, sectores_por_pista=20, bytes_por_sector=512)
adapter = PhysicalDiskAdapter(disk)
disk_mang = DiskManager(adapter)

Miarbolito = BPlusTree(disk_mang)

Miarbolito.print_tree()