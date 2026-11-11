from database.conexao import conectar
from models.fornecedor import Fornecedor


class FornecedorRepository:

    def cadastrar(self, fornecedor):
        conexao = conectar()
        cursor = conexao.cursor()

        sql = """
            INSERT INTO fornecedores
            (nome, contato)
            VALUES (%s, %s)
        """

        valores = (
            fornecedor.nome,
            fornecedor.contato
        )

        cursor.execute(sql, valores)
        fornecedor.id = cursor.lastrowid
        conexao.commit()

        cursor.close()
        conexao.close()

    def buscar_por_id(self, id_fornecedor):
        conexao = conectar()
        cursor = conexao.cursor()

        cursor.execute(
            "SELECT id, nome, contato FROM fornecedores WHERE id = %s",
            (id_fornecedor,)
        )
        linha = cursor.fetchone()

        cursor.close()
        conexao.close()

        if linha is None:
            return None

        return Fornecedor(
            id=linha[0],
            nome=linha[1],
            contato=linha[2]
        )

    def listar(self):
        conexao = conectar()
        cursor = conexao.cursor()

        try:
            cursor.execute(
                "SELECT id, nome, contato FROM fornecedores"
            )
            linhas = cursor.fetchall()

            fornecedores = []

            for linha in linhas:
                fornecedor = Fornecedor(
                    id=linha[0],
                    nome=linha[1],
                    contato=linha[2]
                )
                fornecedores.append(fornecedor)

            return fornecedores

        finally:
            cursor.close()
            conexao.close()

    def editar(self, fornecedor):
        conexao = conectar()
        cursor = conexao.cursor()

        sql = """
            UPDATE fornecedores
            SET nome = %s, contato = %s
            WHERE id = %s
        """

        valores = (
            fornecedor.nome,
            fornecedor.contato,
            fornecedor.id
        )

        cursor.execute(sql, valores)
        conexao.commit()

        cursor.close()
        conexao.close()

    def excluir(self, id_fornecedor):
        conexao = conectar()
        cursor = conexao.cursor()

        try:
            cursor.execute(
                "DELETE FROM fornecedores WHERE id = %s",
                (id_fornecedor,)
            )
            conexao.commit()
        finally:
            cursor.close()
            conexao.close()
