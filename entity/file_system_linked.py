from typing import Dict
from entity.lista import ListaEncadeada

import random

BLOCK_SIZE = 8
TOTAL_BLOCKS = 10

class SistemaArquivos:
    def __init__(self):
        self.nos: Dict[str, ListaEncadeada] = {}
        self.root = ListaEncadeada("/", True)
        self.nos[self.root.id] = self.root
        self.diretorio_atual = self.root
        self.caminho_atual = "/"
        self.disco = [{'data': '', 'next': None} for _ in range(TOTAL_BLOCKS)]
        self.blocos_livres = list(range(TOTAL_BLOCKS))

    def criar_arquivo(self, nome: str):
        if nome in self.diretorio_atual.entries:
            print(f"Erro: '{nome}' já existe neste diretório.")
            return
        no = ListaEncadeada(nome, False)
        self.nos[no.id] = no
        self.diretorio_atual.entries[nome] = no.id
        print(f"Arquivo '{nome}' criado com sucesso.")

    def criar_diretorio(self, nome: str):
        if nome in self.diretorio_atual.entries:
            print(f"Erro: '{nome}' já existe neste diretório.")
            return
        no = ListaEncadeada(nome, True)
        self.nos[no.id] = no
        self.diretorio_atual.entries[nome] = no.id
        print(f"Diretório '{nome}' criado com sucesso.")

    def listar(self):
        if not self.diretorio_atual.entries:
            print("Diretório vazio.")
            return
        for nome in self.diretorio_atual.entries:
            no = self.nos[self.diretorio_atual.entries[nome]]
            tipo = "dir" if no.is_dir else "file"
            print(f"{tipo}\t{nome}")

    def mudar_diretorio(self, caminho: str):
        if caminho == ".":
            return
        if caminho == "..":
            for no in self.nos.values():
                if no.is_dir and self.diretorio_atual.id in no.entries.values():
                    self.diretorio_atual = no
                    self._atualizar_caminho()
                    return
            if self.diretorio_atual.id == self.root.id:
                print("Já está na raiz.")
            return
        if caminho not in self.diretorio_atual.entries:
            print(f"Erro: Diretório '{caminho}' não encontrado.")
            return
        no_id = self.diretorio_atual.entries[caminho]
        no = self.nos[no_id]
        if not no.is_dir:
            print(f"Erro: '{caminho}' não é um diretório.")
            return
        self.diretorio_atual = no
        self._atualizar_caminho()

    def _atualizar_caminho(self):
        if self.diretorio_atual.id == self.root.id:
            self.caminho_atual = "/"
            return
        caminho = []
        atual = self.diretorio_atual
        while atual.id != self.root.id:
            for no in self.nos.values():
                if no.is_dir and atual.id in no.entries.values():
                    for nome, id in no.entries.items():
                        if id == atual.id:
                            caminho.append(nome)
                            atual = no
                            break
            if atual.id == self.root.id:
                caminho.append("")
                break
        self.caminho_atual = "/".join(reversed(caminho)) or "/"

    def mover(self, nome_arquivo: str, destino: str):
        if nome_arquivo not in self.diretorio_atual.entries:
            print(f"Erro: Arquivo '{nome_arquivo}' não encontrado no diretório atual.")
            return
        no_id = self.diretorio_atual.entries[nome_arquivo]
        no = self.nos[no_id]
        if no.is_dir:
            print(f"Erro: '{nome_arquivo}' é um diretório. Apenas arquivos podem ser movidos.")
            return
        destino_dir = self.root if destino == "/" else self.nos[self.diretorio_atual.entries.get(destino)]
        if not destino_dir or not destino_dir.is_dir:
            print(f"Erro: Diretório de destino '{destino}' inválido.")
            return
        if nome_arquivo in destino_dir.entries:
            print(f"Erro: Já existe '{nome_arquivo}' em '{destino}'.")
            return
        del self.diretorio_atual.entries[nome_arquivo]
        destino_dir.entries[nome_arquivo] = no_id
        print(f"Arquivo '{nome_arquivo}' movido para '{destino}' com sucesso.")

    def escrever_arquivo(self, nome: str, dados: str):
        if nome not in self.diretorio_atual.entries:
            self.criar_arquivo(nome)

        no_id = self.diretorio_atual.entries[nome]
        no = self.nos[no_id]

        atual = no.first_block
        while atual is not None:
            prox = self.disco[atual]['next']
            self.disco[atual] = {'data': '', 'next': None}
            self.blocos_livres.append(atual)
            atual = prox
        no.first_block = None

        num_blocos = (len(dados) + BLOCK_SIZE - 1) // BLOCK_SIZE
        if len(self.blocos_livres) < num_blocos:
            print("Erro: Espaço insuficiente em disco.")
            return

        import random
        random.shuffle(self.blocos_livres)

        blocos = [self.blocos_livres.pop(0) for _ in range(num_blocos)]
        for i, bloco in enumerate(blocos):
            inicio = i * BLOCK_SIZE
            fim = inicio + BLOCK_SIZE
            self.disco[bloco]['data'] = dados[inicio:fim]
            self.disco[bloco]['next'] = blocos[i + 1] if i + 1 < num_blocos else None

        no.size = len(dados)
        no.first_block = blocos[0]
        print(f"Dados escritos em '{nome}' ({no.size} bytes) nos blocos {blocos}")


    def ler_arquivo(self, nome: str):
        if nome not in self.diretorio_atual.entries:
            print(f"Erro: Arquivo '{nome}' não encontrado.")
            return
        no_id = self.diretorio_atual.entries[nome]
        no = self.nos[no_id]
        if no.is_dir:
            print(f"Erro: '{nome}' é um diretório.")
            return
        conteudo = ''
        atual = no.first_block
        while atual is not None:
            conteudo += self.disco[atual]['data']
            atual = self.disco[atual]['next']
        print(f"Conteúdo de '{nome}' ({no.size} bytes):")
        print(conteudo[:no.size])

    def deletar(self, nome: str):
        if nome not in self.diretorio_atual.entries:
            print(f"Erro: '{nome}' não existe no diretório atual.")
            return
        no_id = self.diretorio_atual.entries[nome]
        no = self.nos[no_id]
        if no.is_dir:
            if no.entries:
                print(f"Erro: Diretório '{nome}' não está vazio.")
                return
            del self.nos[no_id]
            del self.diretorio_atual.entries[nome]
            print(f"Diretório '{nome}' excluído com sucesso.")
        else:
            atual = no.first_block
            while atual is not None:
                prox = self.disco[atual]['next']
                self.disco[atual] = {'data': '', 'next': None}
                self.blocos_livres.append(atual)
                atual = prox
            del self.nos[no_id]
            del self.diretorio_atual.entries[nome]
            print(f"Arquivo '{nome}' excluído com sucesso.")
