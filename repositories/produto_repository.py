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
