import re
from decimal import Decimal, InvalidOperation


TAMANHO_NOME_USUARIO = 100
TAMANHO_EMAIL = 150
TAMANHO_MATRICULA = 7
SENHA_MINIMO = 10
SENHA_MAXIMO = 20
TAMANHO_NOME_PRODUTO = 50
TAMANHO_FORNECEDOR = 150
TAMANHO_DESCRICAO_CURTA = 255


_PADRAO_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def email_valido(email):
    return bool(email) and bool(_PADRAO_EMAIL.fullmatch(email.strip()))


def matricula_valida(matricula):
    if not isinstance(matricula, str):
        return False

    return bool(re.fullmatch(r"[0-9]{7}", matricula))


def nome_usuario_valido(nome):
    if not isinstance(nome, str):
        return False, "Informe um nome válido."

    if not nome.strip():
        return False, "O nome não pode estar vazio."

    if len(nome) > TAMANHO_NOME_USUARIO:
        return False, (
            f"O nome pode ter no máximo {TAMANHO_NOME_USUARIO} caracteres."
        )

    if nome != nome.strip():
        return False, "O nome não pode começar ou terminar com espaços."

    if "  " in nome:
        return False, "O nome não pode conter espaços consecutivos."

    return True, ""


def senha_valida(senha):
    if not isinstance(senha, str):
        return False, "Informe uma senha válida."

    if any(caractere.isspace() for caractere in senha):
        return False, "A senha não pode conter espaços em branco."

    if len(senha) < SENHA_MINIMO or len(senha) > SENHA_MAXIMO:
        return False, (
            f"A senha deve ter entre {SENHA_MINIMO} e "
            f"{SENHA_MAXIMO} caracteres."
        )

    return True, ""


def converter_valor(texto):
    if texto is None:
        return None

    texto = str(texto).strip().replace("R$", "").replace(" ", "")

    if not texto:
        return None

    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")

    elif texto.count(".") > 1 or re.search(r"\.\d{3}$", texto):
        texto = texto.replace(".", "")

    try:
        valor = Decimal(texto)
    except InvalidOperation:
        return None

    if not valor.is_finite():
        return None

    return valor.quantize(Decimal("0.01"))



def formatar_moeda(valor):
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"
