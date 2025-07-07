import tkinter as tk
from tkinter import messagebox
import os
from page_manager.catalog import CATALOG_FILE  # Asegúrate que sea el correcto
from page_manager.table_manager import TableManager
from disk_manager.physical_disk import PhysicalDisk
from disk_manager.physical_adapter import PhysicalDiskAdapter
from disk_manager.disk_manager import DiskManager
from config import DISK_FILE


class InterfazPrincipal:
    def __init__(self, root):
        self.root = root
        self.root.title("Bienvenido(a) al MSDB")
        self.root.state("zoomed")
        self.root.configure(bg="white")

        titulo = tk.Label(root, text="Bienvenido(a) al MSDB",
                          font=("Helvetica", 28, "bold"), bg="white", fg="#333")
        titulo.pack(pady=50)

        btn_frame = tk.Frame(root, bg="white")
        btn_frame.pack(pady=30)

        crear_btn = tk.Button(btn_frame, text="Crear Disco",
                              font=("Helvetica", 14), width=20, height=2,
                              bg="#4CAF50", fg="white", command=self.abrir_configurador)
        crear_btn.grid(row=0, column=0, padx=20)

        gestionar_btn = tk.Button(btn_frame, text="Gestionar Tablas",
                                  font=("Helvetica", 14), width=20, height=2,
                                  bg="#2196F3", fg="white", command=self.abrir_gestor_tablas)
        gestionar_btn.grid(row=0, column=1, padx=20)

        eliminar_btn = tk.Button(btn_frame, text="Eliminar Disco",
                                 font=("Helvetica", 14), width=20, height=2,
                                 bg="#f44336", fg="white", command=self.eliminar_disco)
        eliminar_btn.grid(row=1, column=0, columnspan=2, pady=30)

        salir_btn = tk.Button(root, text="Salir",
                              font=("Helvetica", 12), width=10,
                              bg="gray", fg="white", command=self.root.destroy)
        salir_btn.pack(pady=10)

    def abrir_configurador(self):
        self.root.withdraw()
        self.configurador = tk.Toplevel()
        self.configurador.title("Configuración del Disco")
        self.configurador.state("zoomed")
        self.configurador.configure(bg="white")

        tk.Label(self.configurador, text="Configuración del Disco",
                 font=("Helvetica", 24, "bold"), bg="white").pack(pady=30)

        form_frame = tk.Frame(self.configurador, bg="white")
        form_frame.pack(pady=20)

        labels = ["Platos", "Pistas por plato", "Sectores por pista", "Bytes por sector"]
        self.entries = []
        for i, label in enumerate(labels):
            tk.Label(form_frame, text=label + ":", font=("Helvetica", 14), bg="white").grid(row=i, column=0, sticky="e", pady=10, padx=10)
            entry = tk.Entry(form_frame, font=("Helvetica", 14), width=10)
            entry.grid(row=i, column=1, pady=10, padx=10)
            self.entries.append(entry)

        boton_frame = tk.Frame(self.configurador, bg="white")
        boton_frame.pack(pady=30)

        crear_btn = tk.Button(boton_frame, text="Crear Disco", font=("Helvetica", 14),
                              bg="#4CAF50", fg="white", width=15, command=self.crear_disco)
        crear_btn.grid(row=0, column=0, padx=20)

        atras_btn = tk.Button(boton_frame, text="Atrás", font=("Helvetica", 14),
                              bg="#f0ad4e", fg="white", width=15, command=self.volver)
        atras_btn.grid(row=0, column=1, padx=20)

        # Mensaje de resultado
        self.resultado_label = tk.Label(self.configurador, text="", font=("Helvetica", 14), bg="white")
        self.resultado_label.pack(pady=10)

    def crear_disco(self):
        if os.path.exists(DISK_FILE):
            # Si el disco ya existe, no se vuelve a crear ni se calculan tamaños
            self.resultado_label.config(
                text="ℹ️ El disco ya ha sido creado previamente.", fg="#FFA500"
            )
            messagebox.showinfo("Disco existente", "El disco ya ha sido creado.")
            return

        try:
            platos = int(self.entries[0].get())
            pistas = int(self.entries[1].get())
            sectores = int(self.entries[2].get())
            bytes_sector = int(self.entries[3].get())

            # Crear disco físicamente
            disco = PhysicalDisk(DISK_FILE, platos, pistas, sectores, bytes_sector)
            adapter = PhysicalDiskAdapter(disco)
            self.disk_manager = DiskManager(adapter)

            # Calcular tamaño del disco
            total_bytes = platos * pistas * sectores * bytes_sector
            self.resultado_label.config(
                text=f"✅ Disco creado. Tamaño total: {total_bytes:,} bytes", fg="#2E8B57"
            )

        except Exception as e:
            self.resultado_label.config(
                text=f"❌ Error al crear el disco: {str(e)}", fg="red"
            )


    def eliminar_disco(self):
        mensajes = []
        if os.path.exists(DISK_FILE):
            os.remove(DISK_FILE)
            mensajes.append("✅ Disco eliminado.")
        else:
            mensajes.append("⚠️ No se encontró el archivo del disco.")

        if os.path.exists(CATALOG_FILE):
            os.remove(CATALOG_FILE)
            mensajes.append("✅ Catálogo eliminado.")
        else:
            mensajes.append("⚠️ No se encontró el archivo de catálogo.")

        messagebox.showinfo("Eliminación", "\n".join(mensajes))

    def abrir_gestor_tablas(self):
        gestor = tk.Toplevel()
        gestor.title("Gestor de Tablas")
        gestor.state("zoomed")
        gestor.configure(bg="white")

        tk.Label(gestor, text="Gestión de Tablas (pendiente de implementación)",
                 font=("Helvetica", 24), bg="white").pack(pady=100)

        atras_btn = tk.Button(gestor, text="Atrás", font=("Helvetica", 14),
                              bg="#f0ad4e", fg="white", width=15, command=gestor.destroy)
        atras_btn.pack(pady=20)

    def volver(self):
        self.configurador.destroy()
        self.root.deiconify()
        self.root.state("zoomed")


def lanzar_interfaz():
    root = tk.Tk()
    app = InterfazPrincipal(root)
    root.mainloop()
