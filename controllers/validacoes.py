# São só funções que conferem e formatam dados.

import re
from decimal import Decimal, InvalidOperation


# Limites iguais aos do schema.sql
TAMANHO_NOME_USUARIO = 100
TAMANHO_EMAIL = 150
TAMANHO_MATRICULA = 7
SENHA_MINIMO = 10
SENHA_MAXIMO = 20
TAMANHO_NOME_PRODUTO = 50
TAMANHO_FORNECEDOR = 150
TAMANHO_DESCRICAO_CURTA = 255

# Formato simples de e-mail
_PADRAO_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def email_valido(email):
    return bool(email) and bool(_PADRAO_EMAIL.match(email.strip()))


# True se a matrícula tem exatamente 7 números.
def matricula_valida(matricula):
    matricula = (matricula or "").strip()
    return matricula.isdigit() and len(matricula) == TAMANHO_MATRICULA


# Converte o valor digitado pelo usuário em decimal com 2 casas
# Devolve None se o texto não for um número válido
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


# Formata no padrão brasileiro
def formatar_moeda(valor):
    texto = f"{valor:,.2f}"                      # '1,250.50'
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"
