
from datetime import date
from decimal import Decimal

import streamlit as st

from controllers.orcamento_controller import (
    cadastrar_orcamento,
    editar_orcamento,
    listar_orcamentos,
)
from database.inicializar import conectar


def formatar_moeda(valor):
    valor = Decimal(str(valor))
    return (
        f"R$ {valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def tela_admin_orcamentos():

    usuario = st.session_state.get("usuario")

    if not usuario or usuario["perfil"] != "administrador":
        st.error("Acesso não autorizado.")
        return

    st.title("Gestão de Orçamentos")
    st.caption("Cadastro e acompanhamento dos orçamentos mensais da cantina.")

    st.divider()

    st.subheader("Cadastrar orçamento mensal")

    hoje = date.today()

    meses = {
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

    with st.form("form_cadastro_orcamento"):

        col1, col2, col3 = st.columns(3)

        with col1:
            mes = st.selectbox(
                "Mês",
                options=list(meses.keys()),
                index=hoje.month - 1,
                format_func=lambda valor: meses[valor],
            )

        with col2:
            ano = st.number_input(
                "Ano",
                min_value=2000,
                max_value=2100,
                value=hoje.year,
                step=1,
            )

        with col3:
            valor = st.number_input(
                "Valor previsto (R$)",
                min_value=0.01,
                max_value=9999999999.99,
                value=100.00,
                step=10.00,
                format="%.2f",
            )

        salvar = st.form_submit_button(
            "Cadastrar orçamento",
            use_container_width=True,
        )

    if salvar:

        conexao = conectar()

        if conexao is None:
            st.error("Não foi possível conectar ao banco de dados.")
        else:
            try:
                sucesso, mensagem = cadastrar_orcamento(
                    conexao,
                    usuario["id_usuario"],
                    mes,
                    ano,
                    Decimal(str(valor)),
                )

                if sucesso:
                    st.success(mensagem)
                    st.rerun()
                else:
                    st.warning(mensagem)

            finally:
                conexao.close()

    st.divider()

    st.subheader("Orçamentos cadastrados")

    conexao = conectar()

    if conexao is None:
        st.error("Não foi possível consultar os orçamentos.")
        return

    try:
        sucesso, resultado = listar_orcamentos(
            conexao,
            usuario["id_usuario"],
        )

    finally:
        conexao.close()

    if not sucesso:
        st.error(resultado)
        return

    if not resultado:
        st.info("Nenhum orçamento cadastrado até o momento.")
        return

    tabela = []

    for orcamento in resultado:
        tabela.append(
            {
                "ID": orcamento["id_orcamento"],
                "Mês/Ano": orcamento["periodo_inicial"].strftime("%m/%Y"),
                "Valor previsto": formatar_moeda(
                    orcamento["valor_definido"]
                ),
                "Administrador": orcamento["nome_administrador"],
                "Data do cadastro": orcamento[
                    "data_hora_definicao"
                ].strftime("%d/%m/%Y %H:%M"),
            }
        )

    st.dataframe(
        tabela,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    st.subheader("Editar orçamento")

    opcoes = {
        item["id_orcamento"]: item
        for item in resultado
    }

    id_selecionado = st.selectbox(
        "Selecione o orçamento",
        options=list(opcoes.keys()),
        format_func=lambda identificador: (
            opcoes[identificador]["periodo_inicial"].strftime("%m/%Y")
            + " — "
            + formatar_moeda(
                opcoes[identificador]["valor_definido"]
            )
        ),
    )

    orcamento_selecionado = opcoes[id_selecionado]

    with st.form("form_edicao_orcamento"):

        st.caption(
            "Período: "
            + orcamento_selecionado["periodo_inicial"].strftime("%d/%m/%Y")
            + " até "
            + orcamento_selecionado["periodo_final"].strftime("%d/%m/%Y")
        )

        novo_valor = st.number_input(
            "Novo valor previsto (R$)",
            min_value=0.01,
            max_value=9999999999.99,
            value=float(orcamento_selecionado["valor_definido"]),
            step=10.00,
            format="%.2f",
            key=f"editar_valor_{id_selecionado}",
        )

        atualizar = st.form_submit_button(
            "Salvar alteração",
            use_container_width=True,
        )

    if atualizar:

        conexao = conectar()

        if conexao is None:
            st.error("Não foi possível conectar ao banco de dados.")
        else:
            try:
                sucesso, mensagem = editar_orcamento(
                    conexao,
                    usuario["id_usuario"],
                    id_selecionado,
                    Decimal(str(novo_valor)),
                )

                if sucesso:
                    st.success(mensagem)
                    st.rerun()
                else:
                    st.warning(mensagem)

            finally:
                conexao.close()
