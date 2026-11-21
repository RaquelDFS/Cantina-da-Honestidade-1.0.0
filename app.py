import time
from views.admin_orcamentos import tela_admin_orcamentos
from views.geral_perfil import tela_perfil
from views.gerente_usuarios_visualizar import tela_gerente_usuarios_visualizar
from views.admin_usuarios_gerenciar import tela_admin_usuarios
from views.admin_Mestoque_visualizar import tela_admin_estoque_visualizar
from views.gerente_estoque_movimentar import tela_gerente_estoque_movimentar
from views.admin_produto_editar import tela_admin_produto_editar
from views.cliente_adicionar_credito import tela_cliente_adicionar_credito
from views.gerente_produtos_visualizar import tela_gerente_produtos_visualizar
from views.admin_produtos_visualizar import tela_admin_produtos_visualizar
from views.produto_cadastro import tela_produto_cadastro
from views.gerente_inicio import tela_gerente_inicio
from views.admin_inicio import tela_admin_inicio
from views.cliente_historico_compras import tela_cliente_historico_compras
from views.cliente_finalizar_compra import tela_cliente_finalizar_compra
from views.cliente_loja import tela_cliente_loja
from views.cliente_inicio import tela_cliente_inicio
from views.menu_lateral import menu_lateral
from views.cliente_cadastro import tela_cadastro_cliente
from views.login import tela_login
from database.inicializar import inicializar_banco
from database.inicializar import conectar
from streamlit_cookies_controller import CookieController
import streamlit as st

st.set_page_config(page_title="Cantina da Honestidade", layout="wide")


if "banco_inicializado" not in st.session_state:

    if not inicializar_banco():
        st.error("Não foi possível inicializar o banco.")
        st.stop()

    st.session_state.banco_inicializado = True


if "pagina" not in st.session_state:
    st.session_state.pagina = "login"

if "usuario" not in st.session_state:
    st.session_state.usuario = None


cookies = CookieController(key="cookies")

if "cookies_carregados" not in st.session_state:

    cookies.getAll()
    time.sleep(1)

    st.session_state.cookies_carregados = True


if st.session_state.usuario is None:

    id_usuario = cookies.get("id_usuario")

    if id_usuario:

        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id_usuario, nome, email, perfil, matricula
            FROM usuarios
            WHERE id_usuario = %s
              AND status = 'ativo'
            """,
            (id_usuario,),
        )

        usuario = cursor.fetchone()

        cursor.close()
        conexao.close()

        if usuario:
            st.session_state.usuario = usuario
            st.session_state.pagina = "inicio"


# P04 - Revalidar o usuário que já possui uma sessão aberta
if st.session_state.usuario is not None:

    id_usuario = st.session_state.usuario["id_usuario"]

    conexao = conectar()

    if conexao is None:
        st.error("Não foi possível validar a sessão. Tente novamente.")
        st.stop()

    try:
        cursor = conexao.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT id_usuario, nome, email, perfil, matricula
                FROM usuarios
                WHERE id_usuario = %s
                  AND status = 'ativo'
                """,
                (id_usuario,),
            )

            usuario_atualizado = cursor.fetchone()

        finally:
            cursor.close()

    finally:
        conexao.close()

    if usuario_atualizado is None:

        cookies.remove("id_usuario")

        st.session_state.usuario = None
        st.session_state.pagina = "login"

        st.warning("Sua sessão foi encerrada porque sua conta está inativa.")

        st.stop()

    else:
        st.session_state.usuario = usuario_atualizado


menu_lateral(cookies)


if st.session_state.pagina == "login":
    tela_login(cookies)

elif st.session_state.pagina == "cadastro":
    tela_cadastro_cliente()

elif st.session_state.pagina == "inicio":

    if st.session_state.usuario is None:
        st.session_state.pagina = "login"
        st.rerun()

    else:
        perfil = st.session_state.usuario["perfil"]

        if perfil == "administrador":
            tela_admin_inicio()

        elif perfil == "gerente":
            tela_gerente_inicio()

        elif perfil == "cliente":
            tela_cliente_inicio()

        else:
            st.error("Perfil de usuário inválido.")
            st.session_state.usuario = None
            st.session_state.pagina = "login"
            st.rerun()

elif st.session_state.pagina == "produto_cadastro":

    if (
        st.session_state.usuario is not None
        and st.session_state.usuario["perfil"] == "administrador"
    ):
        tela_produto_cadastro()

elif st.session_state.pagina == "admin_produtos_visualizar":

    if (
        st.session_state.usuario is not None
        and st.session_state.usuario["perfil"] == "administrador"
    ):
        tela_admin_produtos_visualizar()

elif st.session_state.pagina == "gerente_produtos_visualizar":

    if (
        st.session_state.usuario is not None
        and st.session_state.usuario["perfil"] == "gerente"
    ):
        tela_gerente_produtos_visualizar()

elif st.session_state.pagina == "cliente_loja":

    if (
        st.session_state.usuario is not None
        and st.session_state.usuario["perfil"] == "cliente"
    ):
        tela_cliente_loja()
    else:
        st.error("Acesso não autorizado.")

elif st.session_state.pagina == "cliente_finalizar_compra":

    if (
        st.session_state.usuario is not None
        and st.session_state.usuario["perfil"] == "cliente"
    ):
        tela_cliente_finalizar_compra()
    else:
        st.error("Acesso não autorizado.")

elif st.session_state.pagina == "cliente_historico_compras":

    if (
        st.session_state.usuario is not None
        and st.session_state.usuario["perfil"] == "cliente"
    ):
        tela_cliente_historico_compras()
    else:
        st.error("Acesso não autorizado.")

elif st.session_state.pagina == "cliente_adicionar_credito":

    if (
        st.session_state.usuario is not None
        and st.session_state.usuario["perfil"] == "cliente"
    ):
        tela_cliente_adicionar_credito()
    else:
        st.error("Acesso não autorizado.")

elif st.session_state.pagina == "admin_produto_editar":

    if (
        st.session_state.usuario
        and st.session_state.usuario["perfil"] == "administrador"
    ):
        tela_admin_produto_editar()
    else:
        st.error("Acesso não autorizado.")

elif st.session_state.pagina == "gerente_estoque_movimentar":

    if st.session_state.usuario and st.session_state.usuario["perfil"] == "gerente":
        tela_gerente_estoque_movimentar()
    else:
        st.error("Acesso não autorizado.")

elif st.session_state.pagina == "admin_estoque_visualizar":

    if st.session_state.usuario and st.session_state.usuario["perfil"] in [
        "administrador",
        "gerente",
    ]:
        tela_admin_estoque_visualizar()
    else:
        st.error("Acesso não autorizado.")

elif st.session_state.pagina == "admin_usuarios":

    if (
        st.session_state.usuario is not None
        and st.session_state.usuario["perfil"] == "administrador"
    ):
        tela_admin_usuarios()

elif st.session_state.pagina == "perfil":
    tela_perfil()

elif st.session_state.pagina == "gerente_usuarios_visualizar":

    if (
        st.session_state.usuario
        and st.session_state.usuario["perfil"] == "gerente"
    ):
        tela_gerente_usuarios_visualizar()
    else:
        st.error("Acesso não autorizado.")

elif st.session_state.pagina == "admin_orcamentos":

    if (
        st.session_state.usuario is not None
        and st.session_state.usuario["perfil"] == "administrador"
    ):
        tela_admin_orcamentos()
    else:
        st.error("Acesso não autorizado.")
else:
    # evita deixar a tela em branco.
    st.warning("Página não encontrada.")

    if st.button("Voltar ao início"):
        st.session_state.pagina = (
            "inicio" if st.session_state.usuario else "login"
        )
        st.rerun()
