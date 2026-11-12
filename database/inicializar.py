import os
from pathlib import Path

import mysql.connector


def inicializar_banco():
    caminho_schema = Path(__file__).resolve().parent.parent / "schema.sql"

    conexao = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("MYSQL_PASSWORD")
    )

    cursor = conexao.cursor()

    try:
        comandos_sql = caminho_schema.read_text(encoding="utf-8")

        for comando in comandos_sql.split(";"):
            comando = comando.strip()

            if comando:
                cursor.execute(comando)

        conexao.commit()

    finally:
        cursor.close()
        conexao.close()
