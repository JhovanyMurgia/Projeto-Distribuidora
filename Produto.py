class Produto:
    def __init__(self, id, nome, preco):
        self.id = id
        self.nome = nome
        self.preco = preco


    def setNome(self, novo_nome):
        self.nome = novo_nome

    def setPreco (self, novo_preco):
        self.preco = novo_preco

    def __str__(self) -> str:
        return f"{self.id} {self.nome} R$ {self.preco}"
    

   