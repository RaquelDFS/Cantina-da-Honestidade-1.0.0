
import mysql.connector
import hashlib
import hmac
import secrets
import base64

from controllers.validacoes import (
    SENHA_MAXIMO,
    SENHA_MINIMO,
    TAMANHO_EMAIL,
    TAMANHO_NOME_USUARIO,
    email_valido,
    matricula_valida,
)


def gerar_hash(senha):
    salt = secrets.token_bytes(16)

    senha_hash = hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode("utf-8"),
        salt,
        600000
    )

    salt_texto = base64.b64encode(salt).decode("utf-8")
    hash_texto = base64.b64encode(senha_hash).decode("utf-8")

    return f"pbkdf2_sha256${salt_texto}${hash_texto}"


def verificar_senha(senha, senha_armazenada):
    try:
        algoritmo, salt_texto, hash_texto = senha_armazenada.split("$")

        if algoritmo != "pbkdf2_sha256":
            return False

        salt = base64.b64decode(salt_texto)
        hash_original = base64.b64decode(hash_texto)

        hash_digitado = hashlib.pbkdf2_hmac(
            "sha256",
            senha.encode("utf-8"),
            salt,
            600000
        )

        return hmac.compare_digest(hash_original, hash_digitado)

    except (ValueError, TypeError):
        return False


def cadastrar_cliente(conexao, nome, email, senha, matricula):

    cursor = conexao.cursor()

    try:
        nome = nome.strip()
        email = email.strip().lower()
        matricula = matricula.strip()

        if not nome or not email:
            return False, "Preencha todos os campos."

        if len(nome) > TAMANHO_NOME_USUARIO:
            return False, f"O nome pode ter no máximo {TAMANHO_NOME_USUARIO} caracteres."

        if len(email) > TAMANHO_EMAIL or not email_valido(email):
            return False, "Informe um e-mail válido. Exemplo: nome@email.com"

        if len(senha) < SENHA_MINIMO or len(senha) > SENHA_MAXIMO:
            return False, (
                f"A senha deve ter entre {SENHA_MINIMO} e {SENHA_MAXIMO} caracteres."
            )

        if not matricula_valida(matricula):
            return False, "A matrícula deve conter 7 números."

        # A coluna matricula não é UNIQUE no banco, mas o login é feito
        # pela matrícula. Então não pode existir duas pessoas com a mesma.
        cursor.execute(
            "SELECT 1 FROM usuarios WHERE matricula = %s",
            (matricula,)
        )

        if cursor.fetchone():
            return False, "Esta matrícula já está cadastrada."

        senha_armazenada = gerar_hash(senha)

        sql_usuario = """
            INSERT INTO usuarios
            (nome, email, senha, perfil, status, matricula)
            VALUES (%s, %s, %s, 'cliente', 'ativo', %s)
        """

        cursor.execute(
            sql_usuario,
            (nome, email, senha_armazenada, matricula)
        )

        id_usuario = cursor.lastrowid

        sql_carteira = """
            INSERT INTO carteiras (id_usuario, saldo_atual)
            VALUES (%s, 0.00)
        """

        cursor.execute(sql_carteira, (id_usuario,))

        conexao.commit()

        return True, "Cadastro realizado com sucesso!"

    except mysql.connector.IntegrityError:
        conexao.rollback()
        return False, "Este e-mail já está cadastrado."

    except mysql.connector.Error as erro:
        conexao.rollback()
        # O detalhe técnico vai para o terminal; o usuário vê uma mensagem clara.
        print(f"Erro ao cadastrar cliente: {erro}")
        return False, "Não foi possível concluir o cadastro. Tente novamente."

    finally:
        cursor.close()


def autenticar_usuario(conexao, matricula, senha):

    cursor = conexao.cursor()

    try:
        sql = """
            SELECT id_usuario, nome, senha, perfil, status
            FROM usuarios
            WHERE matricula = %s
        """

        cursor.execute(sql, (matricula,))
        usuario = cursor.fetchone()

        if not usuario:
            return False, "Matrícula ou senha incorretas."

        id_usuario, nome, senha_armazenada, perfil, status = usuario

        if not verificar_senha(senha, senha_armazenada):
            return False, "Matrícula ou senha incorretas."

        if status != "ativo":
            return False, "Usuário inativo. Acesso não permitido."

        dados_usuario = {
            "id_usuario": id_usuario,
            "nome": nome,
            "perfil": perfil,
            "matricula": matricula
        }

        return True, dados_usuario

    except mysql.connector.Error as erro:
        print(f"Erro na autenticação: {erro}")
        return False, "Erro ao acessar o banco de dados."

    finally:
        cursor.close()


def listar_usuarios_gerente(conexao):
    cursor = conexao.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT id_usuario, nome, email, matricula, perfil, status, motivo_inativacao
            FROM usuarios
            WHERE perfil IN ('cliente', 'gerente')
            ORDER BY nome, id_usuario
            """)

        return True, cursor.fetchall()

    except mysql.connector.Error as erro:
        print(f"Erro ao consultar usuários: {erro}")
        return False, "Não foi possível carregar os usuários."

    finally:
        cursor.close()
