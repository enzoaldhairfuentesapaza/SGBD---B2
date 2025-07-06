import re
import pickle
from page_manager.table_manager import TableManager

manager = TableManager()

def run_console():
    print("MiniDB > Escribe comandos tipo SQL. Escribe EXIT para salir.")

    while True:
        cmd = input("MiniDB > ").strip()
        if cmd.lower() in ["exit", "quit"]:
            break

        try:
            if cmd.lower().startswith("create table"):
                parse_create(cmd)
            elif cmd.lower().startswith("insert into"):
                parse_insert(cmd)
            elif cmd.lower().startswith("select from"):
                parse_select(cmd)
#SELECT *
            else:
                print("Comando no reconocido.")
        except Exception as e:
            print(f"Error: {e}")

def parse_create(cmd):
    # CREATE TABLE clientes (id int, nombre str, edad int) PRIMARY KEY id;

    # CREATE TABLE PRODUCTO (index INTEGER(10) PRIMARY KEY,item VARCHAR(40) NOT NULL,cost DECIMAL(10, 2) NOT NULL,tax DECIMAL(10, 2) NOT NULL,total DECIMAL(10, 2) NOT NULL); 
    
    pattern = r"create table (\w+)\s*\((.*?)\)\s*primary key (\w+);?"
    match = re.match(pattern, cmd, re.IGNORECASE)
    if not match:
        raise Exception("Sintaxis inválida para CREATE TABLE.")

    table_name = match.group(1)
    columns_str = match.group(2)
    primary_key = match.group(3)

    columns = []
    for col in columns_str.split(","):
        name, col_type = col.strip().split()
        columns.append({"name": name, "type": col_type})

    manager.create_table(table_name, primary_key, columns)
    print(f"Tabla '{table_name}' creada.")

def parse_insert(cmd):
    # INSERT INTO clientes VALUES (1, "Enzo", 20);
    pattern = r"insert into (\w+)\s*values\s*\((.*?)\);?"
    match = re.match(pattern, cmd, re.IGNORECASE)
    if not match:
        raise Exception("Sintaxis inválida para INSERT.")

    table_name = match.group(1)
    values_str = match.group(2)

    values = eval(f"[{values_str}]")  # ⚠️ seguro solo si tú controlas el input

    schema = manager.catalog.get_table_schema(table_name)
    if not schema:
        raise Exception("Tabla no encontrada.")

    columns = [col["name"] for col in schema["columns"]]
    if len(columns) != len(values):
        raise Exception("Cantidad de valores no coincide con columnas.")

    record = dict(zip(columns, values))
    manager.insert(table_name, record)
    print("Registro insertado.")

#SELECT FROM *, que imprima todos los registros


def parse_select(cmd):
    # SELECT FROM clientes WHERE id = 1;
    pattern = r"select from (\w+)\s+where\s+(\w+)\s*=\s*(\d+);?"
def parse_select(cmd):
    # SELECT FROM clientes;
    pattern_all = r"select\s+\*\s+from\s+(\w+);?"
    match_all = re.match(pattern_all, cmd, re.IGNORECASE)
    if match_all:
        table_name = match_all.group(1)
        schema = manager.catalog.get_table_schema(table_name)
        if not schema:
            raise Exception("Tabla no encontrada.")
        registros = manager.scan_all(table_name)
        if registros:
            print(f"Registros en '{table_name}':")
            for r in registros:
                print(r)
        else:
            print("No hay registros.")
        return

    # SELECT FROM clientes WHERE id = 1;
    pattern = r"select from (\w+)\s+where\s+(\w+)\s*=\s*(\d+);?"
    match = re.match(pattern, cmd, re.IGNORECASE)
    if not match:
        raise Exception("Sintaxis inválida para SELECT.")

    table_name, field, value = match.groups()
    schema = manager.catalog.get_table_schema(table_name)
    if not schema:
        raise Exception("Tabla no encontrada.")

    if field != schema["primary_key"]:
        raise Exception("Solo puedes buscar por la clave primaria.")

    record = manager.select(table_name, int(value))
    if record:
        print("Resultado:", record)
    else:
        print("No encontrado.")
