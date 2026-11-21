
import calendar
from datetime import date
from decimal import Decimal, InvalidOperation

import mysql.connector

from controllers.admin_usuario_controller import verificar_administrador


def validar_periodo(mes, ano):
    try:
        mes = int(mes)
        ano = int(ano)
    except (ValueError, TypeError):
        return False, "Mês ou ano inválido.", None, None

    if ano < 1 or ano > 9999:
        return False, "Ano inválido.", None, None

    if mes < 1 or mes > 12:
        return False, "Mês inválido.", None, None

    ultimo_dia = calendar.monthrange(ano, mes)[1]

    periodo_inicial = date(ano, mes, 1)
    periodo_final = date(ano, mes, ultimo_dia)

    return True, "", periodo_inicial, periodo_final


def validar_valor(valor):
    try:
        valor = Decimal(str(valor))
    except (InvalidOperation, ValueError, TypeError):
        return False, "Informe um valor válido.", None

    if not valor.is_finite():
        return False, "Informe um valor válido.", None

    if valor <= 0:
        return False, "O orçamento deve ser maior que zero.", None

    if valor > Decimal("9999999999.99"):
        return False, "O valor excede o limite permitido.", None

    if valor.as_tuple().exponent < -2:
        return False, "Informe no máximo duas casas decimais.", None

    return True, "", valor


def cadastrar_orcamento(
    conexao,
    id_administrador,
    mes,
    ano,
    valor,
):
    cursor = conexao.cursor(dictionary=True)

    try:
        if not verificar_administrador(cursor, id_administrador):
            return False, "Acesso não autorizado."

        valido, mensagem, periodo_inicial, periodo_final = validar_periodo(
            mes, ano
        )

        if not valido:
            return False, mensagem

        valido, mensagem, valor = validar_valor(valor)

        if not valido:
            return False, mensagem

        # Verifica se existe qualquer orçamento que
        # coincida com o período informado.
        cursor.execute(
            """
            SELECT id_orcamento
            FROM orcamentos
            WHERE periodo_inicial <= %s
              AND periodo_final >= %s
            LIMIT 1
            """,
            (periodo_final, periodo_inicial),
        )

        if cursor.fetchone():
            return False, "Já existe um orçamento para esse período."

        cursor.execute(
            """
            INSERT INTO orcamentos (
                id_administrador,
                valor_definido,
                periodo_inicial,
                periodo_final
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                id_administrador,
                valor,
                periodo_inicial,
                periodo_final,
            ),
        )

        conexao.commit()

        return True, "Orçamento cadastrado com sucesso!"

    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"Erro ao cadastrar orçamento: {erro}")
        return False, "Erro ao cadastrar orçamento."

    finally:
        cursor.close()


def listar_orcamentos(conexao, id_administrador):
    cursor = conexao.cursor(dictionary=True)

    try:
        if not verificar_administrador(cursor, id_administrador):
            return False, "Acesso não autorizado."

        cursor.execute(
            """
            SELECT
                o.id_orcamento,
                o.id_administrador,
                u.nome AS nome_administrador,
                o.valor_definido,
                o.periodo_inicial,
                o.periodo_final,
                o.data_hora_definicao
            FROM orcamentos o
            INNER JOIN usuarios u
                ON u.id_usuario = o.id_administrador
            ORDER BY
                o.periodo_inicial DESC,
                o.id_orcamento DESC
            """
        )

        orcamentos = cursor.fetchall()

        return True, orcamentos

    except mysql.connector.Error as erro:
        print(f"Erro ao listar orçamentos: {erro}")
        return False, "Erro ao consultar orçamentos."

    finally:
        conexao.rollback()
        cursor.close()


def editar_orcamento(
    conexao,
    id_administrador,
    id_orcamento,
    valor,
):
    cursor = conexao.cursor(dictionary=True)

    try:
        if not verificar_administrador(cursor, id_administrador):
            return False, "Acesso não autorizado."

        valido, mensagem, valor = validar_valor(valor)

        if not valido:
            return False, mensagem

        try:
            id_orcamento = int(id_orcamento)
        except (ValueError, TypeError):
            return False, "Orçamento inválido."

        cursor.execute(
            """
            SELECT
                id_orcamento,
                valor_definido
            FROM orcamentos
            WHERE id_orcamento = %s
            FOR UPDATE
            """,
            (id_orcamento,),
        )

        orcamento = cursor.fetchone()

        if not orcamento:
            return False, "Orçamento não encontrado."

        if orcamento["valor_definido"] == valor:
            return False, "O valor informado já é o valor atual."

        cursor.execute(
            """
            UPDATE orcamentos
            SET valor_definido = %s
            WHERE id_orcamento = %s
            """,
            (valor, id_orcamento),
        )

        conexao.commit()

        return True, "Orçamento atualizado com sucesso!"

    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"Erro ao editar orçamento: {erro}")
        return False, "Erro ao editar orçamento."

    finally:
        cursor.close()
