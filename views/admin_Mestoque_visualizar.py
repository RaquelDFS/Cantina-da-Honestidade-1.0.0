import streamlit as st
from database.inicializar import conectar
from datetime import date, timedelta


def tela_admin_estoque_visualizar():

    st.title("Histórico de Movimentações de Estoque")

    usuario = st.session_state.usuario

    if usuario is None or usuario["perfil"] not in ["administrador", "gerente"]:
        st.error("Acesso não autorizado.")
        return

    st.subheader("Filtros")

    col_data, col_motivo = st.columns(2)

    with col_data:
        periodo = st.date_input(
            "Período",
            value=(date.today() - timedelta(days=30), date.today()),
            format="DD/MM/YYYY",
        )

    motivos_opcoes = {
        "reposicao": "Entrada",
        "venda": "Venda",
        "avaria": "Avaria",
        "ajuste": "Ajuste",
    }

    with col_motivo:
        motivos = st.multiselect(
            "Motivos da movimentação",
            options=list(motivos_opcoes.keys()),
            default=list(motivos_opcoes.keys()),
            format_func=lambda motivo: motivos_opcoes[motivo],
        )

    st.divider()

    if len(periodo) != 2:
        st.warning("Selecione uma data inicial e uma data final.")
        return

    data_inicio, data_fim = periodo

    if data_inicio > data_fim:
        st.warning("A data inicial não pode ser posterior à data final.")
        return

    if not motivos:
        st.info("Selecione pelo menos um motivo para visualizar as movimentações.")
        return

    conexao = conectar()

    if not conexao:
        st.error("Não foi possível conectar ao banco de dados.")
        return

    cursor = conexao.cursor(dictionary=True)

    try:

        placeholders = ", ".join(["%s"] * len(motivos))

        consulta = f"""
            SELECT
                m.id_movimentacao,
                p.nome AS produto,
                u.nome AS responsavel,
                m.tipo,
                m.motivo,
                m.quantidade,
                m.valor_compra_unitario_registrado,
                m.custo_total,
                m.fornecedor,
                m.data_hora,
                m.descricao

            FROM movimentacoes_estoque m

            INNER JOIN produtos p
                ON m.id_produto = p.id_produto

            INNER JOIN usuarios u
                ON m.id_usuario_responsavel = u.id_usuario

            WHERE
                m.data_hora >= %s
                AND m.data_hora < %s
                AND m.motivo IN ({placeholders})

            ORDER BY m.data_hora DESC
        """

        parametros = [data_inicio, data_fim + timedelta(days=1)] + motivos

        cursor.execute(consulta, parametros)

        movimentacoes = cursor.fetchall()

    except Exception as erro:
        st.error(f"Erro ao consultar movimentações: {erro}")
        return

    finally:
        cursor.close()
        conexao.close()

    st.subheader("Movimentações registradas")

    if not movimentacoes:
        st.info("Nenhuma movimentação encontrada para os filtros selecionados.")
        return

    st.write(f"Total de movimentações: **{len(movimentacoes)}**")

    dados_exibicao = []

    for movimentacao in movimentacoes:

        dados_exibicao.append(
            {
                "ID": movimentacao["id_movimentacao"],
                "Produto": movimentacao["produto"],
                "Responsável": movimentacao["responsavel"],
                "Tipo": movimentacao["tipo"].capitalize(),
                "Motivo": motivos_opcoes[movimentacao["motivo"]],
                "Quantidade": movimentacao["quantidade"],
                "Valor unitário": (
                    f"R$ {movimentacao['valor_compra_unitario_registrado']:.2f}"
                    if movimentacao["valor_compra_unitario_registrado"] is not None
                    else "-"
                ),
                "Custo total": (
                    f"R$ {movimentacao['custo_total']:.2f}"
                    if movimentacao["custo_total"] is not None
                    else "-"
                ),
                "Fornecedor": movimentacao["fornecedor"] or "-",
                "Data e hora": movimentacao["data_hora"].strftime("%d/%m/%Y %H:%M"),
                "Descrição": movimentacao["descricao"] or "-",
            }
        )

    st.dataframe(dados_exibicao, width="stretch", hide_index=True)
