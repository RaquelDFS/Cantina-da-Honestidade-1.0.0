import mysql.connector
from pathlib import Path
config = {
    "host": "localhost",
    "user": "root",
    "password": "MYSQL_PASSWORD"
}


def inicializar_banco():

    conexao = None
    cursor = None

    try:
        conexao = mysql.connector.connect(**config)
        cursor = conexao.cursor()

        caminho = Path(__file__).with_name("schema.sql")
        schema = caminho.read_text(encoding="utf-8")

        comandos = schema.split(";")

        for comando in comandos:
            if comando.strip():
                cursor.execute(comando)

        conexao.commit()

        print("Banco de dados inicializado com sucesso!")
        return True

    except mysql.connector.Error as erro:
        if conexao:
            conexao.rollback()

        print(f"Erro ao inicializar banco: {erro}")
        return False

    except OSError as erro:
        print(f"Erro ao ler o arquivo schema.sql: {erro}")
        return False

    finally:
        if cursor:
            cursor.close()

        if conexao and conexao.is_connected():
            conexao.close()


def conectar():

    try:
        return mysql.connector.connect(
            database="cantina_honestidade",
            **config
        )

    except mysql.connector.Error as erro:
        print(f"Erro na conexão com o banco: {erro}")
        return None
