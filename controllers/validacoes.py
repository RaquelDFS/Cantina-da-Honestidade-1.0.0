# Validações e formatações usadas pelos formulários (P10).
#
# Nada aqui desenha na tela: são só funções que conferem e formatam dados.
# Os limites batem com as colunas do banco (database/schema.sql), para o
# usuário receber uma mensagem clara antes de o MySQL recusar o dado.

import re
from decimal import Decimal, InvalidOperation


# Limites iguais aos do schema.sql
TAMANHO_NOME_USUARIO = 100      # usuarios.nome VARCHAR(100)
TAMANHO_EMAIL = 150             # usuarios.email VARCHAR(150)
TAMANHO_MATRICULA = 7           # usuarios.matricula: 7 dígitos
SENHA_MINIMO = 10
SENHA_MAXIMO = 20
TAMANHO_NOME_PRODUTO = 50       # CHECK chk_produto_nome
TAMANHO_FORNECEDOR = 150        # produtos.fornecedor_atual VARCHAR(150)
TAMANHO_DESCRICAO_CURTA = 255   # descricao VARCHAR(255) das movimentações

# Formato simples de e-mail: algo@algo.algo, sem espaços.
_PADRAO_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# True se o texto tem cara de e-mail (ex.: nome@senai.br).
def email_valido(email):
    return bool(email) and bool(_PADRAO_EMAIL.match(email.strip()))


# True se a matrícula tem exatamente 7 números.
def matricula_valida(matricula):
    matricula = (matricula or "").strip()
    return matricula.isdigit() and len(matricula) == TAMANHO_MATRICULA


# Converte o valor digitado pelo usuário em Decimal com 2 casas.
#
# Aceita os jeitos mais comuns de digitar dinheiro:
#     "50"        -> 50.00
#     "50,5"      -> 50.50
#     "50.00"     -> 50.00   (ponto como decimal)
#     "1.250,50"  -> 1250.50 (ponto de milhar + vírgula decimal)
#     "R$ 10,00"  -> 10.00
#
# Devolve None se o texto não for um número válido.
def converter_valor(texto):
    if texto is None:
        return None

    texto = str(texto).strip().replace("R$", "").replace(" ", "")

    if not texto:
        return None

    if "," in texto:
        # Formato brasileiro: os pontos são separadores de milhar.
        texto = texto.replace(".", "").replace(",", ".")

    elif texto.count(".") > 1 or re.search(r"\.\d{3}$", texto):
        # "1.250" ou "1.250.000": pontos de milhar, sem centavos.
        texto = texto.replace(".", "")

    try:
        valor = Decimal(texto)
    except InvalidOperation:
        return None

    if not valor.is_finite():
        return None

    return valor.quantize(Decimal("0.01"))


# Formata no padrão brasileiro: 1250.5 -> 'R$ 1.250,50'.
def formatar_moeda(valor):
    texto = f"{valor:,.2f}"                      # '1,250.50'
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"
