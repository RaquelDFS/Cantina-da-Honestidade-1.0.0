class Fornecedor:

    def __init__(
        self,
        nome,
        contato=None,
        id=None
    ):
        self.id = id
        self.nome = nome
        self.contato = contato
