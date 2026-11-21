
from io import BytesIO
from datetime import datetime
from decimal import Decimal

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


MESES = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro",
}

FORMATO_MOEDA = '"R$" #,##0.00;[Red]("R$" #,##0.00)'


def gerar_relatorio_financeiro_excel(relatorio):
    """
    Gera um arquivo XLSX com o relatório financeiro mensal.

    Parâmetros:
        relatorio: lista retornada por consultar_relatorio_financeiro().

    Retorna:
        BytesIO contendo o arquivo Excel.
    """

    if not relatorio:
        raise ValueError(
            "Não existem dados para gerar o relatório financeiro."
        )

    arquivo = BytesIO()
    planilha = Workbook()
    aba = planilha.active
    aba.title = "Relatório Financeiro"

    azul_escuro = "17365D"
    azul_claro = "DCEAF7"
    branco = "FFFFFF"
    cinza = "666666"

    aba.merge_cells("A1:H1")
    titulo = aba["A1"]
    titulo.value = "CANTINA DA HONESTIDADE - RELATÓRIO FINANCEIRO"
    titulo.font = Font(
        name="Calibri",
        size=15,
        bold=True,
        color=branco,
    )
    titulo.fill = PatternFill(
        fill_type="solid",
        fgColor=azul_escuro,
    )
    titulo.alignment = Alignment(
        horizontal="center",
        vertical="center",
    )
    aba.row_dimensions[1].height = 32

    aba.merge_cells("A2:H2")
    aba["A2"] = (
        f"Período: "
        f"{MESES[relatorio[0]['mes']]}/{relatorio[0]['ano']} "
        f"a "
        f"{MESES[relatorio[-1]['mes']]}/{relatorio[-1]['ano']}"
    )
    aba["A2"].alignment = Alignment(horizontal="center")
    aba["A2"].font = Font(
        name="Calibri",
        size=11,
        color=cinza,
    )

    aba.merge_cells("A3:H3")
    aba["A3"] = (
        "Gerado em: "
        f"{datetime.now():%d/%m/%Y %H:%M}"
    )
    aba["A3"].alignment = Alignment(horizontal="center")
    aba["A3"].font = Font(
        name="Calibri",
        size=10,
        italic=True,
        color=cinza,
    )

    cabecalhos = [
        "Mês/Ano",
        "Orçamento (R$)",
        "Vendas (R$)",
        "Gastos (R$)",
        "Saldo Orçamentário (R$)",
        "Resultado Financeiro (R$)",
        "Reposições",
        "Vendas Realizadas",
    ]

    for coluna, nome in enumerate(cabecalhos, start=1):
        celula = aba.cell(row=5, column=coluna, value=nome)
        celula.font = Font(
            name="Calibri",
            bold=True,
            color=branco,
        )
        celula.fill = PatternFill(
            fill_type="solid",
            fgColor=azul_escuro,
        )
        celula.alignment = Alignment(
            horizontal="center",
            vertical="center",
            wrap_text=True,
        )

    aba.row_dimensions[5].height = 32

    borda = Border(
        bottom=Side(style="hair", color="DDDDDD")
    )

    for indice, dados in enumerate(relatorio, start=6):
        valores = [
            f"{dados['mes']:02d}/{dados['ano']}",
            dados["valor_orcamento"],
            dados["total_vendas"],
            dados["total_gastos"],
            dados["saldo_orcamentario"],
            dados["resultado_financeiro"],
            dados["quantidade_reposicoes"],
            dados["quantidade_vendas"],
        ]

        for coluna, valor in enumerate(valores, start=1):
            if isinstance(valor, Decimal):
                valor = float(valor)

            celula = aba.cell(
                row=indice,
                column=coluna,
                value=valor,
            )

            celula.font = Font(name="Calibri", size=11)
            celula.border = borda
            celula.alignment = Alignment(vertical="center")

            if indice % 2 == 0:
                celula.fill = PatternFill(
                    fill_type="solid",
                    fgColor=azul_claro,
                )

            if 2 <= coluna <= 6 and valor is not None:
                celula.number_format = FORMATO_MOEDA

        aba.row_dimensions[indice].height = 23

    larguras = {
        "A": 14,
        "B": 22,
        "C": 20,
        "D": 20,
        "E": 29,
        "F": 29,
        "G": 16,
        "H": 20,
    }

    for coluna, largura in larguras.items():
        aba.column_dimensions[coluna].width = largura

    aba.freeze_panes = "B6"
    aba.auto_filter.ref = f"A5:H{5 + len(relatorio)}"

    aba.merge_cells(
        start_row=7 + len(relatorio),
        start_column=1,
        end_row=7 + len(relatorio),
        end_column=8,
    )

    observacao = aba.cell(
        row=7 + len(relatorio),
        column=1,
        value=(
            "Observação: gastos correspondem às entradas por "
            "reposição de estoque. O resultado financeiro é "
            "calculado como vendas menos gastos com reposições. "
            "Meses sem orçamento cadastrado apresentam "
            "as respectivas células em branco."
        ),
    )

    observacao.font = Font(
        name="Calibri",
        size=10,
        italic=True,
        color=cinza,
    )
    observacao.alignment = Alignment(
        wrap_text=True,
        vertical="center",
    )

    aba.row_dimensions[7 + len(relatorio)].height = 45

    planilha.save(arquivo)
    arquivo.seek(0)

    return arquivo

def gerar_relatorio_financeiro_diario_excel(relatorio):
    """
    Gera um arquivo XLSX com o relatório financeiro diário.

    Parâmetros:
        relatorio: lista retornada por
            consultar_relatorio_financeiro_diario().

    Retorna:
        BytesIO contendo o arquivo Excel.
    """

    if not relatorio:
        raise ValueError(
            "Não existem dados para gerar o relatório financeiro diário."
        )

    arquivo = BytesIO()
    planilha = Workbook()
    aba = planilha.active
    aba.title = "Relatório Diário"

    azul_escuro = "17365D"
    azul_claro = "DCEAF7"
    branco = "FFFFFF"
    cinza = "666666"

    # Título do relatório
    aba.merge_cells("A1:F1")

    titulo = aba["A1"]
    titulo.value = (
        "CANTINA DA HONESTIDADE - RELATÓRIO FINANCEIRO DIÁRIO"
    )
    titulo.font = Font(
        name="Calibri",
        size=15,
        bold=True,
        color=branco,
    )
    titulo.fill = PatternFill(
        fill_type="solid",
        fgColor=azul_escuro,
    )
    titulo.alignment = Alignment(
        horizontal="center",
        vertical="center",
    )

    aba.row_dimensions[1].height = 32

    # Período consultado
    aba.merge_cells("A2:F2")

    aba["A2"] = (
        f"Período: {relatorio[0]['data']:%d/%m/%Y} "
        f"a {relatorio[-1]['data']:%d/%m/%Y}"
    )
    aba["A2"].alignment = Alignment(horizontal="center")
    aba["A2"].font = Font(
        name="Calibri",
        size=11,
        color=cinza,
    )

    # Data e hora da exportação
    aba.merge_cells("A3:F3")

    aba["A3"] = (
        f"Gerado em: {datetime.now():%d/%m/%Y %H:%M}"
    )
    aba["A3"].alignment = Alignment(horizontal="center")
    aba["A3"].font = Font(
        name="Calibri",
        size=10,
        italic=True,
        color=cinza,
    )

    # Cabeçalhos
    cabecalhos = [
        "Data",
        "Vendas (R$)",
        "Gastos (R$)",
        "Resultado Financeiro (R$)",
        "Reposições",
        "Vendas Realizadas",
    ]

    for coluna, nome in enumerate(cabecalhos, start=1):
        celula = aba.cell(
            row=5,
            column=coluna,
            value=nome,
        )

        celula.font = Font(
            name="Calibri",
            bold=True,
            color=branco,
        )
        celula.fill = PatternFill(
            fill_type="solid",
            fgColor=azul_escuro,
        )
        celula.alignment = Alignment(
            horizontal="center",
            vertical="center",
            wrap_text=True,
        )

    aba.row_dimensions[5].height = 32

    borda = Border(
        bottom=Side(style="hair", color="DDDDDD")
    )

    # Dados diários
    for indice, dados in enumerate(relatorio, start=6):
        valores = [
            dados["data"],
            dados["total_vendas"],
            dados["total_gastos"],
            dados["resultado_financeiro"],
            dados["quantidade_reposicoes"],
            dados["quantidade_vendas"],
        ]

        for coluna, valor in enumerate(valores, start=1):
            if isinstance(valor, Decimal):
                valor = float(valor)

            celula = aba.cell(
                row=indice,
                column=coluna,
                value=valor,
            )

            celula.font = Font(
                name="Calibri",
                size=11,
            )
            celula.border = borda
            celula.alignment = Alignment(
                vertical="center",
            )

            if indice % 2 == 0:
                celula.fill = PatternFill(
                    fill_type="solid",
                    fgColor=azul_claro,
                )

            if coluna == 1:
                celula.number_format = "DD/MM/YYYY"

            if 2 <= coluna <= 4:
                celula.number_format = FORMATO_MOEDA

        aba.row_dimensions[indice].height = 23

    # Largura das colunas
    larguras = {
        "A": 16,
        "B": 22,
        "C": 22,
        "D": 30,
        "E": 18,
        "F": 22,
    }

    for coluna, largura in larguras.items():
        aba.column_dimensions[coluna].width = largura

    # Congelar cabeçalho e habilitar filtros
    aba.freeze_panes = "B6"
    aba.auto_filter.ref = f"A5:F{5 + len(relatorio)}"

    # Observações
    linha_observacao = 7 + len(relatorio)

    aba.merge_cells(
        start_row=linha_observacao,
        start_column=1,
        end_row=linha_observacao,
        end_column=6,
    )

    observacao = aba.cell(
        row=linha_observacao,
        column=1,
        value=(
            "Observação: gastos correspondem às entradas "
            "por reposição de estoque. O resultado financeiro "
            "é calculado como vendas menos gastos com "
            "reposições. Dias sem movimentação são "
            "apresentados com valores zerados."
        ),
    )

    observacao.font = Font(
        name="Calibri",
        size=10,
        italic=True,
        color=cinza,
    )
    observacao.alignment = Alignment(
        wrap_text=True,
        vertical="center",
    )

    aba.row_dimensions[linha_observacao].height = 45

    # Salvar o arquivo em memória
    planilha.save(arquivo)
    arquivo.seek(0)

    return arquivo
