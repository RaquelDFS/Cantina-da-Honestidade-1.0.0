class Produto:

    def __init__(
        self,
        nome,
        preco,
        quantidade_estoque,
        ativo=True,
        id=None,
        id_fornecedor=None
    ):
        self.id = id
        self.nome = nome
        self.preco = preco
        self.quantidade_estoque = quantidade_estoque
        self.ativo = ativo
        self.id_fornecedor = id_fornecedor
