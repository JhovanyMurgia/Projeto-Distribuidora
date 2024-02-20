from datetime import datetime

class Venda:
    def __init__(self, id, produto, quantidade):
        self.id = id
        self.produto = produto
        self.quantidade = quantidade
        self.valor = produto.preco*quantidade


    def __str__(self) -> str:
        return f"{self.produto} {self.quantidade} R${self.valor}"
    
