
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

        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.TABLE_CONSTRAINTS
            WHERE CONSTRAINT_SCHEMA = 'estoque'
              AND TABLE_NAME = 'produtos'
              AND CONSTRAINT_NAME = 'chk_estoque_ativo'
              AND CONSTRAINT_TYPE = 'CHECK'
        """)

        existe_restricao = cursor.fetchone()[0] > 0

        if existe_restricao:
            cursor.execute("""
                ALTER TABLE estoque.produtos
                DROP CHECK chk_estoque_ativo
            """)

        conexao.commit()

    finally:
        cursor.close()
        conexao.close()
