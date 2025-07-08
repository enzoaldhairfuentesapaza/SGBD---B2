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
            elif cmd.lower().startswith("select * from"):
                parse_select_all(cmd)  # Detecta SELECT * FROM primero
            elif cmd.lower().startswith("select from"):
                parse_select_any(cmd)
            else:
                print("Comando no reconocido.")
        except Exception as e:
            print(f"Error: {e}")

def parse_create(cmd):
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

def parse_select_any(cmd):
    pattern = r'select\s+from\s+(\w+)\s+where\s+(\w+)\s*=\s*(?:"([^"]+)"|\'([^\']+)\'|([^\s;]+));?'
    match = re.match(pattern, cmd, re.IGNORECASE)
    if not match:
        raise Exception("Sintaxis inválida para SELECT.")

    table_name = match.group(1)
    field = match.group(2)
    value = match.group(3) or match.group(4) or match.group(5)

    schema = manager.catalog.get_table_schema(table_name)
    if not schema:
        raise Exception("Tabla no encontrada.")

    columns = [col["name"] for col in schema["columns"]]
    if field not in columns:
        raise Exception(f"Columna '{field}' no existe en la tabla '{table_name}'.")

    results = manager.search_by_field(table_name, field, value)
    if results:
        print("Resultados encontrados:")
        for record in results:
            print(record)
    else:
        print("No se encontraron registros.")

# ✅ NUEVA FUNCIÓN → SELECT * FROM
def parse_select_all(cmd):
    pattern = r"select\s+\*\s+from\s+(\w+);?"
    match = re.match(pattern, cmd, re.IGNORECASE)
    if not match:
        raise Exception("Sintaxis inválida para SELECT *.")

    table_name = match.group(1)
    schema = manager.catalog.get_table_schema(table_name)
    if not schema:
        raise Exception("Tabla no encontrada.")

    records = manager.select_all(table_name)
    if records:
        print(f"Todos los registros en '{table_name}':")
        for record in records:
            print(record)
    else:
        print(f"No hay registros en la tabla '{table_name}'.")
