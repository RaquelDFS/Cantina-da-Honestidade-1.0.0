import os
import getpass
import mysql.connector

from controllers.usuario_controller import gerar_hash


def criar_admin_inicial():
    banco = os.getenv("MYSQL_DATABASE")

    if not banco:
        print("Informe MYSQL_DATABASE antes de executar.")
        return

    print("=== Cadastro do primeiro administrador ===")

    nome = input("Nome: ").strip()
    email = input("E-mail: ").strip().lower()
    matricula = input("Matricula (7 numeros): ").strip()
    senha = getpass.getpass("Senha (10 a 20 caracteres): ")

    if not nome or not email:
        print("Nome e e-mail sao obrigatorios.")
        return

    if not matricula.isdigit() or len(matricula) != 7:
        print("A matricula deve conter 7 numeros.")
        return

    if not 10 <= len(senha) <= 20:
        print("A senha deve ter entre 10 e 20 caracteres.")
        return

    conexao = None
    cursor = None

    try:
        conexao = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("MYSQL_PASSWORD"),
            database=banco,
        )

        cursor = conexao.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM usuarios WHERE perfil = %s", ("administrador",)
        )

        if cursor.fetchone()[0] > 0:
            print("Ja existe um administrador cadastrado.")
            return

        senha_hash = gerar_hash(senha)

        cursor.execute(
            """
            INSERT INTO usuarios
                (nome, email, senha, perfil, status, matricula)
            VALUES
                (%s, %s, %s, %s, %s, %s)
            """,
            (nome, email, senha_hash, "administrador", "ativo", matricula),
        )

        conexao.commit()
        print("Administrador cadastrado com sucesso!")

    except mysql.connector.Error as erro:
        if conexao:
            conexao.rollback()

        print(f"Erro ao cadastrar administrador: {erro}")

    finally:
        if cursor:
            cursor.close()

        if conexao and conexao.is_connected():
            conexao.close()


if __name__ == "__main__":
    criar_admin_inicial()
