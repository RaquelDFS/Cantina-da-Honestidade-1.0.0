
from datetime import date
from decimal import Decimal

import pandas as pd
import streamlit as st

from database.inicializar import conectar
from controllers.financeiro_controller import (
    consultar_resumo_financeiro,
    consultar_relatorio_financeiro,
    consultar_relatorio_financeiro_diario,
)
from controllers.financeiro_exportacao import (
    gerar_relatorio_financeiro_excel,
    gerar_relatorio_financeiro_diario_excel,
)
from views.admin_Mestoque_visualizar import tela_admin_estoque_visualizar


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

TIPO_ARQUIVO_EXCEL = (
    "application/vnd.openxmlformats-officedocument."
    "spreadsheetml.sheet"
)


def formatar_moeda(valor):
    if valor is None:
        return "Não definido"

    valor = Decimal(str(valor))

    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "X")
    texto = texto.replace(".", ",")
    texto = texto.replace("X", ".")

    return f"R$ {texto}"


def exibir_indicadores_financeiros(conexao, mes, ano):
    sucesso, mensagem, dados = consultar_resumo_financeiro(
        conexao,
        mes,
        ano,
    )

    if not sucesso:
        st.error(mensagem)
        return

    st.caption(
        f"Período: "
        f"{dados['periodo_inicial']:%d/%m/%Y} a "
        f"{dados['periodo_final']:%d/%m/%Y}"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Orçamento mensal",
            formatar_moeda(dados["valor_orcamento"]),
        )

    with col2:
        st.metric(
            "Gastos com reposições",
            formatar_moeda(dados["total_gastos"]),
        )

    with col3:
        st.metric(
            "Vendas realizadas",
            formatar_moeda(dados["total_vendas"]),
        )

    st.divider()

    col4, col5 = st.columns(2)

    with col4:
        st.metric(
            "Saldo orçamentário",
            formatar_moeda(dados["saldo_orcamentario"]),
        )

    with col5:
        st.metric(
            "Resultado financeiro",
            formatar_moeda(dados["resultado_financeiro"]),
        )

    if dados["valor_orcamento"] is None:
        st.info(
            "Não existe orçamento cadastrado "
            "para o período selecionado."
        )

    else:
        percentual = dados["percentual_utilizado"]

        st.write(
            f"**Orçamento utilizado:** {percentual:.2f}%"
        )

        st.progress(
            min(
                max(float(percentual / Decimal("100")), 0.0),
                1.0,
            )
        )

        if percentual > 100:
            st.warning(
                "Os gastos com reposições ultrapassaram "
                "o orçamento previsto para o mês."
            )

    st.caption(
        f"Reposições registradas: "
        f"{dados['quantidade_reposicoes']} | "
        f"Vendas registradas: "
        f"{dados['quantidade_vendas']}"
    )

    st.caption(
        "Os gastos consideram entradas de estoque por "
        "reposição. O resultado financeiro corresponde "
        "ao valor das vendas menos esses gastos."
    )


def exibir_relatorio_mensal(conexao):
    hoje = date.today()

    st.write(
        "Consulte os resultados financeiros consolidados "
        "por mês e exporte os dados para Excel."
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        mes_inicial = st.selectbox(
            "Mês inicial",
            options=list(MESES.keys()),
            index=0,
            format_func=lambda numero: MESES[numero],
            key="relatorio_mes_inicial",
        )

    with col2:
        ano_inicial = st.number_input(
            "Ano inicial",
            min_value=2000,
            max_value=9998,
            value=hoje.year,
            step=1,
            key="relatorio_ano_inicial",
        )

    with col3:
        mes_final = st.selectbox(
            "Mês final",
            options=list(MESES.keys()),
            index=hoje.month - 1,
            format_func=lambda numero: MESES[numero],
            key="relatorio_mes_final",
        )

    with col4:
        ano_final = st.number_input(
            "Ano final",
            min_value=2000,
            max_value=9998,
            value=hoje.year,
            step=1,
            key="relatorio_ano_final",
        )

    sucesso, mensagem, relatorio = consultar_relatorio_financeiro(
        conexao,
        mes_inicial,
        ano_inicial,
        mes_final,
        ano_final,
    )

    if not sucesso:
        st.warning(mensagem)
        return

    linhas = []

    for dados in relatorio:
        linhas.append(
            {
                "Mês/Ano": f"{dados['mes']:02d}/{dados['ano']}",
                "Orçamento": formatar_moeda(
                    dados["valor_orcamento"]
                ),
                "Vendas": formatar_moeda(
                    dados["total_vendas"]
                ),
                "Gastos": formatar_moeda(
                    dados["total_gastos"]
                ),
                "Saldo orçamentário": formatar_moeda(
                    dados["saldo_orcamentario"]
                ),
                "Resultado financeiro": formatar_moeda(
                    dados["resultado_financeiro"]
                ),
            }
        )

    tabela = pd.DataFrame(linhas)

    st.dataframe(
        tabela,
        use_container_width=True,
        hide_index=True,
    )

    try:
        arquivo_excel = gerar_relatorio_financeiro_excel(
            relatorio
        )

        nome_arquivo = (
            f"relatorio_financeiro_mensal_"
            f"{ano_inicial}_{mes_inicial:02d}_"
            f"{ano_final}_{mes_final:02d}.xlsx"
        )

        st.download_button(
            "Baixar relatório mensal Excel (.xlsx)",
            data=arquivo_excel.getvalue(),
            file_name=nome_arquivo,
            mime=TIPO_ARQUIVO_EXCEL,
            use_container_width=True,
        )

    except Exception as erro:
        st.error(
            f"Não foi possível gerar o relatório Excel: {erro}"
        )


def exibir_relatorio_diario(conexao):
    hoje = date.today()

    st.write(
        "Consulte vendas e gastos por dia, incluindo "
        "os dias sem movimentação."
    )

    col1, col2 = st.columns(2)

    with col1:
        data_inicial = st.date_input(
            "Data inicial",
            value=hoje.replace(day=1),
            min_value=date(2000, 1, 1),
            max_value=date(9998, 12, 31),
            format="DD/MM/YYYY",
            key="relatorio_diario_data_inicial",
        )

    with col2:
        data_final = st.date_input(
            "Data final",
            value=hoje,
            min_value=date(2000, 1, 1),
            max_value=date(9998, 12, 31),
            format="DD/MM/YYYY",
            key="relatorio_diario_data_final",
        )

    sucesso, mensagem, relatorio = (
        consultar_relatorio_financeiro_diario(
            conexao,
            data_inicial,
            data_final,
        )
    )

    if not sucesso:
        st.warning(mensagem)
        return

    linhas = []

    for dados in relatorio:
        linhas.append(
            {
                "Data": dados["data"].strftime("%d/%m/%Y"),
                "Vendas": formatar_moeda(
                    dados["total_vendas"]
                ),
                "Gastos": formatar_moeda(
                    dados["total_gastos"]
                ),
                "Resultado financeiro": formatar_moeda(
                    dados["resultado_financeiro"]
                ),
                "Reposições": dados["quantidade_reposicoes"],
                "Vendas realizadas": dados["quantidade_vendas"],
            }
        )

    tabela = pd.DataFrame(linhas)

    st.dataframe(
        tabela,
        use_container_width=True,
        hide_index=True,
    )

    total_vendas = sum(
        (
            dados["total_vendas"]
            for dados in relatorio
        ),
        Decimal("0.00"),
    )

    total_gastos = sum(
        (
            dados["total_gastos"]
            for dados in relatorio
        ),
        Decimal("0.00"),
    )

    resultado_financeiro = total_vendas - total_gastos

    st.write("**Totais do período**")

    col_vendas, col_gastos, col_resultado = st.columns(3)

    with col_vendas:
        st.metric(
            "Total de vendas",
            formatar_moeda(total_vendas),
        )

    with col_gastos:
        st.metric(
            "Total de gastos",
            formatar_moeda(total_gastos),
        )

    with col_resultado:
        st.metric(
            "Resultado financeiro",
            formatar_moeda(resultado_financeiro),
        )

    st.caption(
        f"Período consultado: {len(relatorio)} dia(s). "
        "Os gastos correspondem às reposições de estoque."
    )

    try:
        arquivo_excel = (
            gerar_relatorio_financeiro_diario_excel(
                relatorio
            )
        )

        nome_arquivo = (
            f"relatorio_financeiro_diario_"
            f"{data_inicial:%Y%m%d}_"
            f"{data_final:%Y%m%d}.xlsx"
        )

        st.download_button(
            "Baixar relatório diário Excel (.xlsx)",
            data=arquivo_excel.getvalue(),
            file_name=nome_arquivo,
            mime=TIPO_ARQUIVO_EXCEL,
            use_container_width=True,
        )

    except Exception as erro:
        st.error(
            f"Não foi possível gerar o relatório Excel: {erro}"
        )


def exibir_relatorio_financeiro(conexao):
    with st.expander("Relatórios financeiros"):
        modalidade = st.radio(
            "Tipo de relatório",
            options=["Mensal", "Diário"],
            horizontal=True,
            key="relatorio_financeiro_modalidade",
        )

        if modalidade == "Mensal":
            exibir_relatorio_mensal(conexao)

        else:
            exibir_relatorio_diario(conexao)


def tela_admin_inicio():
    usuario = st.session_state.get("usuario")

    if not usuario or usuario.get("perfil") != "administrador":
        st.error("Acesso não autorizado.")
        st.session_state.pagina = "login"
        st.rerun()
        return

    st.title("Painel Administrativo")
    st.write(f"Bem-vindo(a), {usuario['nome']}!")
    st.caption("Visão geral da Cantina da Honestidade")

    st.divider()
    st.subheader("Financeiro")

    hoje = date.today()

    col_mes, col_ano = st.columns(2)

    with col_mes:
        mes = st.selectbox(
            "Mês de referência",
            options=list(MESES.keys()),
            index=hoje.month - 1,
            format_func=lambda numero: MESES[numero],
            key="dashboard_financeiro_mes",
        )

    with col_ano:
        ano = st.number_input(
            "Ano de referência",
            min_value=2000,
            max_value=9998,
            value=hoje.year,
            step=1,
            key="dashboard_financeiro_ano",
        )

    conexao = conectar()

    if not conexao:
        st.error("Não foi possível conectar ao banco de dados.")

    else:
        try:
            exibir_indicadores_financeiros(
                conexao,
                mes,
                ano,
            )

            st.divider()

            exibir_relatorio_financeiro(conexao)

        finally:
            conexao.close()

    st.divider()

    tela_admin_estoque_visualizar()
