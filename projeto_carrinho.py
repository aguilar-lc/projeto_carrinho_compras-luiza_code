
from fastapi import FastAPI
from typing import List
from pydantic import BaseModel

app = FastAPI()
FALHA = "FALHA"
OK = "OK"
db_usuarios = {}
db_endereco = {}
db_produtos = {}   
db_carrinhos = {}

# Classe de dados do usuário:
class Usuario(BaseModel):
    id: int
    nome: str
    email: str
    senha: str
    
# Classe de dados do endereço do cliente
class Endereco(BaseModel):
    id_endereco: int
    rua: str
    cep: str
    cidade: str
    estado: str

# Classe da lista de endereços de um cliente
class ListaDeEnderecosDoUsuario(BaseModel):
    usuario: Usuario
    enderecos: List[Endereco] = []

class Produto(BaseModel):
    id: int
    nome: str
    descricao: str
    preco: float

class CarrinhoDeCompras(BaseModel):
    id_usuario: int
    id_produtos: List[Produto] = []
    preco_total: float
    quantidade_de_produtos: int

# Ter na página raiz uma saudação de boas vindas:
@app.get("/")
def rota_raiz():
    site = "Seja bem vinda"
    return site.replace('\n', '')

# Cadastrar um usuário com um nome e um e-mail. Um usuário irá ter um código identificador único no sistema:
@app.post("/usuario/")
def cadastrar_usuario(novo_usuario: Usuario):
    if novo_usuario.id in db_usuarios:
        return "Falha: Usuário já cadastrado"
    db_usuarios[novo_usuario.id] = novo_usuario
    return novo_usuario

# Consultar um usuário pelo seu código identificador:
@app.get("/usuario-por-id/{id}")
def consultar_usuario_pelo_id(id: int):
    if id in db_usuarios:
        return db_usuarios[id]
    return "Falha: Usuário inexistente"

# Consultar um usuário pelo nome dele:
@app.get("/usuario-por-nome/{nome}")
def consultar_usuario_pelo_nome(nome: str):
    for id in db_usuarios.keys():
        if db_usuarios[id].nome == nome:
            return db_usuarios[id]
    return "Falha: Usuário inexistente"

# Remover usuario pelo código dele
@app.delete("/usuario-delete-por-id/{id}")
def deletar_usuario_pelo_id(id: int):
    if id not in db_usuarios:
        return "Falha: Usuário inexistente"
    elif id in db_usuarios:
        del db_usuarios[id]   
    return "Usuário removido"

# Cadastrar o(s) endereço(s) do usuário: 
@app.post("/endereco/{id}/")
def cadastrar_endereco(endereco: Endereco, id: int):
    if id not in db_usuarios:
         return "Falha: Usuário inexistente, cadastrar usuário"
    else:
        if id not in db_endereco:
            db_endereco[id] = ListaDeEnderecosDoUsuario(**{"usuario": db_usuarios[id],"enderecos": [endereco],})
        else:
            db_endereco[id].enderecos.append(endereco)      
    return db_endereco

# Pesquisar pelo endereço de um usuario pelo id:
@app.get("/usuario-por-endereco/{id_endereco}")
def pesquisar_usuario_pelo_endereco(id_endereco: int):
    for id in db_endereco:
        for endereco in db_endereco[id].enderecos:
            if endereco.id_endereco == id_endereco:
                return endereco
    return "Falha: Endereço não cadastrado"
    
# Remover um endereço do usuário pelo seu código identificador:
@app.delete("/usuario-delete-por-endereco/{id_endereco}")
def deletar_usuario_pelo_endereco(id_endereco: int):
    for id in db_endereco:
        for endereco in db_endereco[id].enderecos:
            if endereco.id_endereco == id_endereco:
                del db_usuarios[id] 
                return "Endereço Removido"
    return "Id não existe"

#Cadastrar um produto, que possua nome, descrição, preço, e código identificador:
@app.post("/produto/")
def cadastrar_produto(novo_produto: Produto):
    if novo_produto.id in db_produtos:
        return "Falha: Produto já cadastrado"
    db_produtos[novo_produto.id] = novo_produto
    return novo_produto

# Remover um produto pelo código:
@app.delete("/produto-delete-pelo-id/{id_produto}")
def deletar_produto_pelo_id(id_produto: int):
    if id_produto not in db_produtos:
        return "Falha: Produto não cadastrado"
    elif id_produto in db_produtos:
        del db_produtos[id_produto]   
    return "Produto removido"

# Criar carrinho de compras associado ao usuário:
# Adicionar produtos ao carrinho de compras:
def criar_novo_carrinho(id_usuario,produtos,carrinho: CarrinhoDeCompras = CarrinhoDeCompras(**{
            "id_usuario":0,
            "id_produtos":[],
            "preco_total":0,
            "quantidade_de_produtos": 1
        })):
    carrinho.id_usuario = id_usuario
    carrinho.id_produtos.append(produtos)
    carrinho.preco_total = produtos.preco
    return carrinho

@app.post("/carrinho/{id_usuario}/{id_produto}/")
def adicionar_carrinho(id_usuario: int, id_produto: int):
    if id_usuario not in db_usuarios or id_produto not in db_produtos:
        return FALHA
    produto = db_produtos[id_produto]
    if id_usuario not in db_carrinhos:
        db_carrinhos[id_usuario] = criar_novo_carrinho(id_usuario, produto)
    else:
        db_carrinhos[id_usuario].id_produtos.append(produto)
        db_carrinhos[id_usuario].preco_total += db_produtos[id_produto].preco
        db_carrinhos[id_usuario].quantidade_de_produtos += 1
    return "Produto adicionado no carrinho"

# Retornar carrinho de compras
@app.get("/carrinho/{id_usuario}/")
def retornar_carrinho(id_usuario: int):
    if id_usuario not in db_carrinhos:
        return FALHA
    return db_carrinhos[id_usuario]

# Cálcular valor total do carrinho de compras
@app.get("/carrinho/{id_usuario}/")
def retornar_total_carrinho(id_usuario: int):
    numero_de_itens, valor_tot = 0
    return numero_de_itens, valor_tot

# Remover carrinho de compras
@app.delete("/carrinho/{id_usuario}/")
def deletar_carrinho(id_usuario: int):
    if id_usuario not in db_usuarios:
        return FALHA
    db_carrinhos.pop(id_usuario)
    return "Carrinho removido"

