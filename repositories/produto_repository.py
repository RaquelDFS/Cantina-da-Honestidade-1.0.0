from database.conexao import conectar
from models.produto import Produto
# COLOQUE AS FUNÇÕES AQUI!
#CADASTRAR
#LISTAR
#EDITAR
#EXCLUIR

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

    def listar(self):
        conexao = conectar()
        cursor = conexao.cursor()

        sql = """
            SELECT id, nome, preco, quantidade_estoque, ativo
            FROM produtos
            WHERE ativo = 1
            ORDER BY nome
        """

        cursor.execute(sql)
        linhas = cursor.fetchall()

        produtos = []
        for linha in linhas:
            produto = Produto(linha[1], linha[2], linha[3], linha[4])
            produto.id = linha[0]
            produtos.append(produto)

        cursor.close()
        conexao.close()

        return produtos