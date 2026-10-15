from database.conexao import conectar
from models.produto import Produto


class ProdutoRepository:

    def cadastrar(self, produto):
        conexao = conectar()
        cursor = conexao.cursor()

        sql = """
            INSERT INTO produtos
            (nome, preco, quantidade_estoque, ativo)
            VALUES (%s, %s, %s, %s)
        """

        valores = (
            produto.nome,
            produto.preco,
            produto.quantidade_estoque,
            produto.ativo
        )

        cursor.execute(sql, valores)
        produto.id = cursor.lastrowid
        conexao.commit()

        cursor.close()
        conexao.close()

    def buscar_por_id(self, id_produto):
        conexao = conectar()
        cursor = conexao.cursor()

        cursor.execute(
            "SELECT id, nome, preco, quantidade_estoque, ativo "
            "FROM produtos WHERE id = %s",
            (id_produto,)
        )
        linha = cursor.fetchone()

        cursor.close()
        conexao.close()

        if linha is None:
            return None

        return Produto(
            id=linha[0],
            nome=linha[1],
            preco=linha[2],
            quantidade_estoque=linha[3],
            ativo=bool(linha[4])
        )

    def editar(self, produto):
        conexao = conectar()
        cursor = conexao.cursor()

        sql = """
            UPDATE produtos
            SET nome = %s, preco = %s, quantidade_estoque = %s, ativo = %s
            WHERE id = %s
        """

        valores = (
            produto.nome,
            produto.preco,
            produto.quantidade_estoque,
            produto.ativo,
            produto.id
        )

        cursor.execute(sql, valores)
        conexao.commit()

        cursor.close()
        conexao.close()

    def listar(self):
        conexao = conectar()
        cursor = conexao.cursor()

        try:
            cursor.execute(
                "SELECT id, nome, preco, quantidade_estoque, ativo "
                "FROM produtos"
            )
            linhas = cursor.fetchall()

            produtos = []

            for linha in linhas:
                produto = Produto(
                    id=linha[0],
                    nome=linha[1],
                    preco=linha[2],
                    quantidade_estoque=linha[3],
                    ativo=bool(linha[4])
                )
                produtos.append(produto)

            return produtos

        finally:
            cursor.close()
            conexao.close()

    def excluir(self, id_produto):
        conexao = conectar()
        cursor = conexao.cursor()

        try:
            cursor.execute(
                "DELETE FROM produtos WHERE id = %s",
                (id_produto,)
            )
            conexao.commit()
        finally:
            cursor.close()
            conexao.close()

    def toggle_ativo(self, id_produto):
        conexao = conectar()
        cursor = conexao.cursor()

        try:
            cursor.execute(
                """
                UPDATE produtos
                SET ativo = CASE
                    WHEN ativo = TRUE THEN FALSE
                    WHEN quantidade_estoque > 0 THEN TRUE
                    ELSE FALSE
                END
                WHERE id = %s
                """,
                (id_produto,)
            )
            conexao.commit()
        finally:
            cursor.close()
            conexao.close()
