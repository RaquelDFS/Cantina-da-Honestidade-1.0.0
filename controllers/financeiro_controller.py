
import calendar
from datetime import date
from decimal import Decimal

import mysql.connector


def consultar_resumo_financeiro(conexao, mes, ano):
    """
    Consulta o resumo financeiro de um mês.

    Retorna:
        (True, mensagem, dados) em caso de sucesso.
        (False, mensagem, None) em caso de erro.
    """

    try:
        mes = int(mes)
        ano = int(ano)

        if mes < 1 or mes > 12:
            return False, "Mês inválido.", None

        if ano < 1 or ano > 9999:
            return False, "Ano inválido.", None

        ultimo_dia = calendar.monthrange(ano, mes)[1]

        periodo_inicial = date(ano, mes, 1)
        periodo_final = date(ano, mes, ultimo_dia)

        if mes == 12:
            proximo_periodo = date(ano + 1, 1, 1)
        else:
            proximo_periodo = date(ano, mes + 1, 1)

    except (ValueError, TypeError, OverflowError):
        return False, "Período informado é inválido.", None

    if conexao is None:
        return False, "Conexão com o banco indisponível.", None

    cursor = None

    try:
        cursor = conexao.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                id_orcamento,
                valor_definido
            FROM orcamentos
            WHERE periodo_inicial <= %s
              AND periodo_final >= %s
            ORDER BY id_orcamento DESC
            LIMIT 1
            """,
            (periodo_final, periodo_inicial),
        )

        orcamento = cursor.fetchone()

        cursor.execute(
            """
            SELECT
                COUNT(*) AS quantidade_reposicoes,
                COALESCE(SUM(custo_total), 0) AS total_gastos
            FROM movimentacoes_estoque
            WHERE tipo = 'entrada'
              AND motivo = 'reposicao'
              AND data_hora >= %s
              AND data_hora < %s
            """,
            (periodo_inicial, proximo_periodo),
        )

        gastos = cursor.fetchone()

        cursor.execute(
            """
            SELECT
                COUNT(*) AS quantidade_vendas,
                COALESCE(SUM(valor_total), 0) AS total_vendas
            FROM vendas
            WHERE data_hora >= %s
              AND data_hora < %s
            """,
            (periodo_inicial, proximo_periodo),
        )

        vendas = cursor.fetchone()

        valor_orcamento = (
            Decimal(str(orcamento["valor_definido"]))
            if orcamento
            else None
        )

        total_gastos = Decimal(
            str(gastos["total_gastos"])
        )

        total_vendas = Decimal(
            str(vendas["total_vendas"])
        )

        saldo_orcamentario = None
        percentual_utilizado = None

        if valor_orcamento is not None:
            saldo_orcamentario = valor_orcamento - total_gastos

            percentual_utilizado = (
                total_gastos / valor_orcamento
            ) * Decimal("100")

        resultado_financeiro = total_vendas - total_gastos

        dados = {
            "mes": mes,
            "ano": ano,
            "periodo_inicial": periodo_inicial,
            "periodo_final": periodo_final,
            "id_orcamento": (
                orcamento["id_orcamento"]
                if orcamento
                else None
            ),
            "valor_orcamento": valor_orcamento,
            "quantidade_reposicoes": gastos["quantidade_reposicoes"],
            "total_gastos": total_gastos,
            "quantidade_vendas": vendas["quantidade_vendas"],
            "total_vendas": total_vendas,
            "saldo_orcamentario": saldo_orcamentario,
            "percentual_utilizado": percentual_utilizado,
            "resultado_financeiro": resultado_financeiro,
        }

        return True, "Resumo financeiro consultado com sucesso.", dados

    except mysql.connector.Error as erro:
        return False, f"Erro ao consultar dados financeiros: {erro}", None

    finally:
        if cursor is not None:
            cursor.close()

        if conexao is not None and conexao.is_connected():
            conexao.rollback()

def consultar_relatorio_financeiro(
    conexao,
    mes_inicial,
    ano_inicial,
    mes_final,
    ano_final,
):
    """
    Consulta o relatório financeiro consolidado por mês.

    Retorna:
        (True, mensagem, lista_de_meses) em caso de sucesso.
        (False, mensagem, None) em caso de erro.
    """

    try:
        mes_inicial = int(mes_inicial)
        ano_inicial = int(ano_inicial)
        mes_final = int(mes_final)
        ano_final = int(ano_final)

        if not 1 <= mes_inicial <= 12:
            return False, "Mês inicial inválido.", None

        if not 1 <= mes_final <= 12:
            return False, "Mês final inválido.", None

        if not 1 <= ano_inicial <= 9998:
            return False, "Ano inicial inválido.", None

        if not 1 <= ano_final <= 9998:
            return False, "Ano final inválido.", None

    except (ValueError, TypeError, OverflowError):
        return False, "Período informado é inválido.", None

    indice_inicial = ano_inicial * 12 + mes_inicial
    indice_final = ano_final * 12 + mes_final

    quantidade_meses = indice_final - indice_inicial + 1

    if quantidade_meses <= 0:
        return (
            False,
            "O período inicial não pode ser posterior ao final.",
            None,
        )

    if quantidade_meses > 60:
        return (
            False,
            "Selecione um período de até 60 meses.",
            None,
        )

    if conexao is None:
        return False, "Conexão com o banco indisponível.", None

    relatorio = []

    for indice in range(indice_inicial, indice_final + 1):

        ano = (indice - 1) // 12
        mes = (indice - 1) % 12 + 1

        sucesso, mensagem, dados = consultar_resumo_financeiro(
            conexao,
            mes,
            ano,
        )

        if not sucesso:
            return False, mensagem, None

        relatorio.append(dados)

    return (
        True,
        "Relatório financeiro consultado com sucesso.",
        relatorio,
    )

def consultar_relatorio_financeiro_diario(
    conexao,
    data_inicial,
    data_final,
):
    """
    Consulta vendas e gastos diários de um período.

    Inclui dias sem movimentação.

    Retorna:
        (True, mensagem, lista_de_dias) em caso de sucesso.
        (False, mensagem, None) em caso de erro.
    """

    from datetime import datetime, timedelta

    try:
        if isinstance(data_inicial, str):
            data_inicial = date.fromisoformat(data_inicial)

        if isinstance(data_final, str):
            data_final = date.fromisoformat(data_final)

        if isinstance(data_inicial, datetime):
            data_inicial = data_inicial.date()

        if isinstance(data_final, datetime):
            data_final = data_final.date()

        if not isinstance(data_inicial, date):
            return False, "Data inicial inválida.", None

        if not isinstance(data_final, date):
            return False, "Data final inválida.", None

    except (ValueError, TypeError):
        return False, "Período informado é inválido.", None

    if data_inicial > data_final:
        return (
            False,
            "A data inicial não pode ser posterior à data final.",
            None,
        )

    quantidade_dias = (data_final - data_inicial).days + 1

    if quantidade_dias > 366:
        return (
            False,
            "Selecione um período de até 366 dias.",
            None,
        )

    if conexao is None:
        return False, "Conexão com o banco indisponível.", None

    cursor = None

    try:
        cursor = conexao.cursor(dictionary=True)

        # Limite exclusivo: inclui todos os horários do último dia.
        data_limite = data_final + timedelta(days=1)

        cursor.execute(
            """
            SELECT
                DATE(data_hora) AS data_movimentacao,
                COUNT(*) AS quantidade_reposicoes,
                COALESCE(SUM(custo_total), 0) AS total_gastos
            FROM movimentacoes_estoque
            WHERE tipo = 'entrada'
              AND motivo = 'reposicao'
              AND data_hora >= %s
              AND data_hora < %s
            GROUP BY DATE(data_hora)
            """,
            (data_inicial, data_limite),
        )

        gastos_por_dia = {
            linha["data_movimentacao"]: linha
            for linha in cursor.fetchall()
        }

        cursor.execute(
            """
            SELECT
                DATE(data_hora) AS data_venda,
                COUNT(*) AS quantidade_vendas,
                COALESCE(SUM(valor_total), 0) AS total_vendas
            FROM vendas
            WHERE data_hora >= %s
              AND data_hora < %s
            GROUP BY DATE(data_hora)
            """,
            (data_inicial, data_limite),
        )

        vendas_por_dia = {
            linha["data_venda"]: linha
            for linha in cursor.fetchall()
        }

        relatorio = []

        for deslocamento in range(quantidade_dias):
            dia = data_inicial + timedelta(days=deslocamento)

            gastos = gastos_por_dia.get(dia, {})
            vendas = vendas_por_dia.get(dia, {})

            total_gastos = Decimal(
                str(gastos.get("total_gastos", 0))
            )

            total_vendas = Decimal(
                str(vendas.get("total_vendas", 0))
            )

            relatorio.append(
                {
                    "data": dia,
                    "quantidade_reposicoes": gastos.get(
                        "quantidade_reposicoes", 0
                    ),
                    "total_gastos": total_gastos,
                    "quantidade_vendas": vendas.get(
                        "quantidade_vendas", 0
                    ),
                    "total_vendas": total_vendas,
                    "resultado_financeiro": (
                        total_vendas - total_gastos
                    ),
                }
            )

        return (
            True,
            "Relatório financeiro diário consultado com sucesso.",
            relatorio,
        )

    except mysql.connector.Error as erro:
        return (
            False,
            f"Erro ao consultar relatório diário: {erro}",
            None,
        )

    except OverflowError:
        return False, "Período informado é inválido.", None

    finally:
        if cursor is not None:
            cursor.close()

        if conexao is not None and conexao.is_connected():
            conexao.rollback()
