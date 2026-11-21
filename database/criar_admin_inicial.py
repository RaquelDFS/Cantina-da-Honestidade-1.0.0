
import os
import getpass
import mysql.connector

from controllers.usuario_controller import gerar_hash
from controllers.validacoes import (
    TAMANHO_EMAIL,
    email_valido,
    matricula_valida,
    nome_usuario_valido,
    senha_valida,
)


def criar_admin_inicial():
    banco = os.getenv("MYSQL_DATABASE")

    if not banco:
        print("Informe MYSQL_DATABASE antes de executar.")
        return

    print("=== Cadastro do primeiro administrador ===")

    nome = input("Nome: ")
    email = input("E-mail: ").strip().lower()
    matricula = input("Matricula (7 numeros): ")
    senha = getpass.getpass("Senha (10 a 20 caracteres): ")

    valido, mensagem = nome_usuario_valido(nome)
    if not valido:
        print(mensagem)
        return

    if len(email) > TAMANHO_EMAIL or not email_valido(email):
        print("Informe um e-mail valido.")
        return

    if not matricula_valida(matricula):
        print("A matricula deve conter exatamente 7 numeros.")
        return

    valido, mensagem = senha_valida(senha)
    if not valido:
        print(mensagem)
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
            "SELECT COUNT(*) FROM usuarios WHERE perfil = %s",
            ("administrador",),
        )

        if cursor.fetchone()[0] > 0:
            print("Ja existe um administrador cadastrado.")
            return

        cursor.execute(
            "SELECT 1 FROM usuarios WHERE matricula = %s",
            (matricula,),
        )

        if cursor.fetchone():
            print("Esta matricula ja esta cadastrada.")
            return

        cursor.execute(
            "SELECT 1 FROM usuarios WHERE email = %s",
            (email,),
        )

        if cursor.fetchone():
            print("Este e-mail ja esta cadastrado.")
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

    except mysql.connector.IntegrityError as erro:
        if conexao:
            conexao.rollback()

        if erro.errno == 1062:
            print("E-mail ou matricula ja cadastrados.")
        else:
            print(f"Erro de integridade ao cadastrar administrador: {erro}")

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
