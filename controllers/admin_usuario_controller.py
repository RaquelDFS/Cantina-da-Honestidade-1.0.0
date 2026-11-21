
import mysql.connector

from controllers.usuario_controller import gerar_hash
from controllers.validacoes import (
    TAMANHO_EMAIL,
    email_valido,
    matricula_valida,
    nome_usuario_valido,
    senha_valida,
)


def verificar_administrador(cursor, id_administrador):
    cursor.execute(
        """
        SELECT id_usuario
        FROM usuarios
        WHERE id_usuario = %s
          AND perfil = 'administrador'
          AND status = 'ativo'
        """,
        (id_administrador,),
    )

    return cursor.fetchone() is not None


def listar_usuarios(conexao, id_administrador):
    cursor = conexao.cursor(dictionary=True)

    try:
        if not verificar_administrador(cursor, id_administrador):
            return False, "Acesso não autorizado."

        cursor.execute("""
            SELECT id_usuario, nome, email, matricula, perfil, status
            FROM usuarios
            ORDER BY nome, id_usuario
            """)

        return True, cursor.fetchall()

    except mysql.connector.Error:
        return False, "Erro ao consultar usuários."

    finally:
        conexao.rollback()
        cursor.close()


def cadastrar_usuario_administrativo(
    conexao, id_administrador, nome, email, matricula, senha, perfil
):
    cursor = conexao.cursor()

    try:
        if not verificar_administrador(cursor, id_administrador):
            return False, "Acesso não autorizado."

        valido, mensagem = nome_usuario_valido(nome)
        if not valido:
            return False, mensagem

        valido, mensagem = senha_valida(senha)
        if not valido:
            return False, mensagem

        if not isinstance(email, str):
            return False, "Informe um e-mail válido."

        email = email.strip().lower()

        if len(email) > TAMANHO_EMAIL or not email_valido(email):
            return False, "Informe um e-mail válido."

        if not matricula_valida(matricula):
            return False, "A matrícula deve conter exatamente 7 números."

        if perfil not in ("administrador", "gerente"):
            return False, "Perfil inválido para cadastro administrativo."

        cursor.execute(
            "SELECT id_usuario FROM usuarios WHERE matricula = %s",
            (matricula,),
        )

        if cursor.fetchone():
            return False, "Matrícula já cadastrada."

        cursor.execute(
            "SELECT id_usuario FROM usuarios WHERE email = %s",
            (email,),
        )

        if cursor.fetchone():
            return False, "E-mail já cadastrado."

        cursor.execute(
            """
            INSERT INTO usuarios
                (nome, email, senha, perfil, status, matricula)
            VALUES (%s, %s, %s, %s, 'ativo', %s)
            """,
            (nome, email, gerar_hash(senha), perfil, matricula),
        )

        conexao.commit()
        return True, "Usuário cadastrado com sucesso!"

    except mysql.connector.IntegrityError as erro:
        conexao.rollback()

        if erro.errno == 1062:
            return False, "E-mail ou matrícula já cadastrados."

        return False, "Não foi possível concluir o cadastro."

    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"Erro ao cadastrar usuário: {erro}")
        return False, "Erro ao cadastrar usuário."

    finally:
        cursor.close()


def alterar_status_usuario(conexao, id_administrador, id_usuario, novo_status):
    cursor = conexao.cursor(dictionary=True)

    try:
        if novo_status not in ("ativo", "inativo"):
            return False, "Status inválido."

        id_administrador = int(id_administrador)
        id_usuario = int(id_usuario)

        if id_administrador == id_usuario and novo_status == "inativo":
            return False, "Você não pode desativar sua própria conta."

        # Bloqueia os administradores ativos antes da alteração.
        # Isso evita que duas desativações simultâneas deixem
        # o sistema sem administradores ativos.
        cursor.execute("""
            SELECT id_usuario
            FROM usuarios
            WHERE perfil = 'administrador'
              AND status = 'ativo'
            ORDER BY id_usuario
            FOR UPDATE
            """)

        administradores_ativos = {
            item["id_usuario"] for item in cursor.fetchall()
        }

        if id_administrador not in administradores_ativos:
            conexao.rollback()
            return False, "Acesso não autorizado."

        cursor.execute(
            """
            SELECT id_usuario, perfil, status
            FROM usuarios
            WHERE id_usuario = %s
            FOR UPDATE
            """,
            (id_usuario,),
        )

        usuario = cursor.fetchone()

        if not usuario:
            conexao.rollback()
            return False, "Usuário não encontrado."

        if usuario["status"] == novo_status:
            conexao.rollback()
            return False, "O usuário já possui esse status."

        if (
            usuario["perfil"] == "administrador"
            and novo_status == "inativo"
            and len(administradores_ativos) <= 1
        ):
            conexao.rollback()
            return False, "Não é possível desativar o último administrador ativo."

        cursor.execute(
            """
            UPDATE usuarios
            SET status = %s
            WHERE id_usuario = %s
            """,
            (novo_status, id_usuario),
        )

        conexao.commit()
        return True, "Status do usuário atualizado com sucesso!"

    except (mysql.connector.Error, ValueError, TypeError):
        conexao.rollback()
        return False, "Erro ao alterar o status do usuário."

    finally:
        cursor.close()
