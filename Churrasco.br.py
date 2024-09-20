import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from PIL import Image, ImageTk
import crud  # módulo crud


class TelaPrincipal:
    def __init__(self, win):
        self.win = win
        self.win.title('Tela Principal')
        self.win.geometry("720x600+10+10")

        # Adicionando imagem central
        self.imagem = Image.open("imagem_central.jpg")  # Altere para o caminho da sua imagem
        self.imagem = self.imagem.resize((300, 300), Image.LANCZOS)
        self.img = ImageTk.PhotoImage(self.imagem)

        self.labelImagem = tk.Label(win, image=self.img)
        self.labelImagem.pack(pady=20)

        self.label = tk.Label(self.win, text='Churrasco.br', font=("Arial", 15))
        self.label.pack(pady=10)

        # Botões
        self.btnPDV = tk.Button(win, text='PDV', command=self.abrirPDV)
        self.btnEstoque = tk.Button(win, text='Cadastrar Produto', command=self.gerenciarEstoque)
        self.btnRelatorio = tk.Button(win, text='Relatório de Vendas', command=self.abrirRelatorio)

        # Posicionamento dos botões
        self.btnPDV.pack(pady=10)
        self.btnEstoque.pack(pady=10)
        self.btnRelatorio.pack(pady=10)

    def abrirPDV(self):
        self.pdv = PDV(self)  # Passa a referência da tela principal
        self.win.withdraw()  # Oculta a tela principal

    def gerenciarEstoque(self):
        self.estoque = CadastrarProduto(self)  # Passa a referência da tela principal
        self.win.withdraw()  # Oculta a tela principal

    def abrirRelatorio(self):
        self.relatorio = RelatorioVendas(self)  # Passa a referência da tela principal
        self.win.withdraw()  # Oculta a tela principal

    def voltar(self):
        self.win.deiconify()  # Mostra a tela principal novamente


class PDV:
    def __init__(self, tela_principal):
        self.tela_principal = tela_principal  # Armazena a referência da tela principal
        self.conn = 'produtos.db'
        self.objBD = crud.Crud(self.conn)  # Altere conforme sua implementação

        self.carrinho = []
        self.total = 0.0

        self.win = tk.Toplevel(self.tela_principal.win)
        self.win.title('PDV')
        self.win.geometry("720x600+10+10")

        self.label = tk.Label(self.win, text='Sistema de PDV', font=("Arial", 20))
        self.label.pack(pady=20)

        # Campos de entrada
        self.lbCodigo = tk.Label(self.win, text='Código do Produto:')
        self.txtCodigo = tk.Entry(self.win)
        self.btnBuscar = tk.Button(self.win, text='Buscar', command=self.buscarProduto)
        self.btnAdicionar = tk.Button(self.win, text='Adicionar ao Carrinho', command=self.adicionarProdutoAoCarrinho)
        self.btnLimpar = tk.Button(self.win, text='Limpar Carrinho', command=self.limparCarrinho)

        self.lbCodigo.pack(pady=5)
        self.txtCodigo.pack(pady=5)
        self.btnBuscar.pack(pady=10)
        self.btnAdicionar.pack(pady=10)
        self.btnLimpar.pack(pady=10)

        self.resultado = tk.Label(self.win, text='', font=("Arial", 16))
        self.resultado.pack(pady=20)

        self.btnFinalizar = tk.Button(self.win, text='Finalizar Venda', command=self.finalizarVenda)
        self.btnFinalizar.pack(pady=10)

        self.lbCarrinho = tk.Label(self.win, text='Carrinho de Compras:', font=("Arial", 16))
        self.lbCarrinho.pack(pady=10)

        self.treeCarrinho = ttk.Treeview(self.win, columns=("Código", "Nome", "Preço", "Quantidade"), show='headings')
        self.treeCarrinho.heading("Código", text="Código")
        self.treeCarrinho.heading("Nome", text="Nome")
        self.treeCarrinho.heading("Preço", text="Preço")
        self.treeCarrinho.heading("Quantidade", text="Quantidade")

        self.treeCarrinho.pack(padx=10, pady=10)

        self.lbTotal = tk.Label(self.win, text='Total: R$0.00', font=("Arial", 16))
        self.lbTotal.pack(pady=20)

        # Comportamento de fechamento
        self.win.protocol("WM_DELETE_WINDOW", self.fechar)

    def fechar(self):
        self.win.destroy()  # Fecha a janela do PDV
        self.tela_principal.voltar()  # Retorna ao menu principal

    def buscarProduto(self):
        codigo = self.txtCodigo.get()
        produto = self.objBD.selecionarDadosPorCodigo(codigo)
        if produto:
            nome = produto[1]
            preco = produto[2]
            self.resultado.config(text=f'Produto: {nome}, Preço: R${preco:.2f}')
        else:
            self.resultado.config(text='Produto não encontrado!')

    def adicionarProdutoAoCarrinho(self):
        codigo = self.txtCodigo.get()
        produto = self.objBD.selecionarDadosPorCodigo(codigo)

        if produto:
            nome = produto[1]
            preco = produto[2]

            # Pergunta a quantidade ao usuário
            quantidade = simpledialog.askinteger("Quantidade", "Quantas unidades deseja adicionar?", minvalue=1)
            if quantidade is None:
                return  # O usuário cancelou a operação

            # Verifica se o produto já está no carrinho
            for i, item in enumerate(self.carrinho):
                if item[0] == codigo:  # Se o código já está no carrinho
                    item_list = list(item)  # Converte a tupla em lista
                    item_list[3] += quantidade  # Atualiza a quantidade (índice 3)
                    self.carrinho[i] = tuple(item_list)  # Converte de volta para tupla
                    self.total += preco * quantidade  # Atualiza o total
                    self.lbTotal.config(text=f'Total: R${self.total:.2f}')
                    self.resultado.config(text=f'Quantidade de {nome} aumentada para {item_list[3]}.')
                    self.atualizarCarrinho()
                    return

            # Se o produto não está no carrinho, adiciona-o
            self.carrinho.append((codigo, nome, preco, quantidade))  # Armazena código, nome, preço e quantidade
            self.total += preco * quantidade
            self.lbTotal.config(text=f'Total: R${self.total:.2f}')
            self.resultado.config(text=f'Produto {nome} adicionado ao carrinho.')
            self.atualizarCarrinho()

    def limparCarrinho(self):
        # Limpa o carrinho de compras
        self.carrinho.clear()
        self.total = 0.0
        self.lbTotal.config(text='Total: R$0.00')
        self.resultado.config(text='Carrinho limpo com sucesso!')
        self.atualizarCarrinho()

    def atualizarCarrinho(self):
        # Limpa o Treeview antes de atualizar
        self.treeCarrinho.delete(*self.treeCarrinho.get_children())

        for item in self.carrinho:
            codigo, nome, preco, quantidade = item  # Desempacota a tupla
            self.treeCarrinho.insert('', 'end', values=(codigo, nome, preco, quantidade))

    def finalizarVenda(self):
        if not self.carrinho:
            self.resultado.config(text="Carrinho vazio! Adicione produtos antes de finalizar a venda.")
            return

        confirmacao = messagebox.askyesno("Confirmação", "Deseja finalizar a venda?")
        if not confirmacao:
            return

        # Apresenta os detalhes da venda
        detalhes_venda = "\n".join([f'Código: {item[0]}, Nome: {item[1]}, Preço: R${item[2]:.2f}, Quantidade: {item[3]}' for item in self.carrinho])
        total_venda = sum(item[2] * item[3] for item in self.carrinho)
        messagebox.showinfo("Venda Finalizada", f"Venda finalizada!\n\n{detalhes_venda}\n\nTotal: R${total_venda:.2f}")

        # Armazena a venda no banco de dados
        self.objBD.inserirVenda(detalhes_venda, total_venda)
        self.resetCarrinho()

    def resetCarrinho(self):
        self.carrinho.clear()
        self.treeCarrinho.delete(*self.treeCarrinho.get_children())
        self.total = 0.0
        self.lbTotal.config(text='Total: R$0.00')
        self.resultado.config(text='Venda finalizada com sucesso!')

class CadastrarProduto:
    def __init__(self, tela_principal):
        self.tela_principal = tela_principal  # Armazena a referência da tela principal
        self.conn = 'produtos.db'
        self.objBD = crud.Crud(self.conn)

        self.win = tk.Toplevel(self.tela_principal.win)
        self.win.title('Cadastrar Produto')
        self.win.geometry("720x600+10+10")

        self.label = tk.Label(self.win, text='Cadastrar Produto', font=("Arial", 20))
        self.label.pack(pady=20)

        # Componentes de entrada
        self.lbCodigo = tk.Label(self.win, text='Código do Produto:')
        self.txtCodigo = tk.Entry(self.win)
        self.lbNome = tk.Label(self.win, text='Nome do Produto:')
        self.txtNome = tk.Entry(self.win)
        self.lbPreco = tk.Label(self.win, text='Preço:')
        self.txtPreco = tk.Entry(self.win)

        self.btnCadastrar = tk.Button(self.win, text='Cadastrar', command=self.cadastrarProduto)
        self.btnAtualizar = tk.Button(self.win, text='Atualizar', command=self.atualizarProduto)
        self.btnExcluir = tk.Button(self.win, text='Excluir', command=self.excluirProduto)



        # Posicionamento
        self.lbCodigo.pack(pady=5)
        self.txtCodigo.pack(pady=5)
        self.lbNome.pack(pady=5)
        self.txtNome.pack(pady=5)
        self.lbPreco.pack(pady=5)
        self.txtPreco.pack(pady=5)
        self.btnCadastrar.pack(pady=10)
        self.btnAtualizar.pack(padx=10)
        self.btnExcluir.pack(pady=10)

        self.lbSpace = tk.Label(self.win, justify='center', text='-----')
        self.lbSpace.pack(pady=5)


        # Treeview para visualizar produtos cadastrados
        self.treeProdutos = ttk.Treeview(self.win, columns=("Código", "Nome", "Preço"), show='headings')
        self.treeProdutos.heading("Código", text="Código")
        self.treeProdutos.heading("Nome", text="Nome")
        self.treeProdutos.heading("Preço", text="Preço")
        self.treeProdutos.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Carrega os produtos cadastrados
        self.carregarProdutos()

        # Evento de seleção no Treeview
        self.treeProdutos.bind("<<TreeviewSelect>>", self.on_item_selected)

        # Comportamento de fechamento
        self.win.protocol("WM_DELETE_WINDOW", self.fechar)

    def fechar(self):
        self.win.destroy()  # Fecha a janela de gerenciamento de estoque
        self.tela_principal.voltar()  # Retorna ao menu principal

    def carregarProdutos(self):
        # Limpa a Treeview antes de carregar os produtos
        self.treeProdutos.delete(*self.treeProdutos.get_children())
        produtos = self.objBD.selecionarTodosDados()  # Método que deve retornar todos os produtos
        for produto in produtos:
            self.treeProdutos.insert('', 'end', values=produto)

    def cadastrarProduto(self):
        try:
            codigo = int(self.txtCodigo.get())
            nome = self.txtNome.get()
            preco = float(self.txtPreco.get())
            self.objBD.inserirDados(codigo, nome, preco)
            messagebox.showinfo("Sucesso", f'Produto {nome} cadastrado com sucesso!')
            self.carregarProdutos()  # Atualiza a lista de produtos
        except ValueError:
            messagebox.showerror("Erro", "Dados inválidos! Verifique o código e o preço.")

    def atualizarProduto(self):
        try:
            codigo = int(self.txtCodigo.get())
            nome = self.txtNome.get()
            preco = float(self.txtPreco.get())
            self.objBD.atualizarDados(codigo, nome, preco)
            messagebox.showinfo("Sucesso", f'Produto {codigo} atualizado com sucesso!')
            self.carregarProdutos()  # Atualiza a lista de produtos
        except ValueError:
            messagebox.showerror("Erro", "Dados inválidos! Verifique o código e o preço.")

    def on_item_selected(self, event):
        # Obtém o item selecionado
        selected_item = self.treeProdutos.focus()
        item_values = self.treeProdutos.item(selected_item, 'values')

        if item_values:
            # Preenche as entradas com os dados do item selecionado
            self.txtCodigo.delete(0, tk.END)  # Limpa a Entry antes de preencher
            self.txtCodigo.insert(0, item_values[0])  # Código
            self.txtNome.delete(0, tk.END)
            self.txtNome.insert(0, item_values[1])  # Nome
            self.txtPreco.delete(0, tk.END)
            self.txtPreco.insert(0, item_values[2])  # Preço

    def excluirProduto(self):
        try:
            codigo = int(self.txtCodigo.get())
            self.objBD.excluirDados(codigo)
            messagebox.showinfo("Sucesso", f'Produto {codigo} excluído com sucesso!')
            self.carregarProdutos()  # Atualiza a lista de produtos
        except ValueError:
            messagebox.showerror("Erro", "Código inválido!")
class RelatorioVendas:
    def __init__(self, tela_principal):
        self.tela_principal = tela_principal  # Armazena a referência da tela principal
        self.conn = 'produtos.db'
        self.objBD = crud.Crud(self.conn)

        self.win = tk.Toplevel(self.tela_principal.win)
        self.win.title('Relatório de Vendas')
        self.win.geometry("720x600+10+10")

        self.label = tk.Label(self.win, text='Relatório de Vendas', font=("Arial", 20))
        self.label.pack(pady=20)

        # Exibição de dados
        self.dadosColunas = ("Código", "Detalhes", "Total", "Data")

        self.treeRelatorio = ttk.Treeview(self.win, columns=self.dadosColunas, selectmode='browse')
        for coluna in self.dadosColunas:
            self.treeRelatorio.heading(coluna, text=coluna)
            self.treeRelatorio.column(coluna, anchor='center')

        self.treeRelatorio.pack(padx=10, pady=10)

        # Label para informações adicionais
        self.label_info = tk.Label(self.win, text='Dados das Vendas:', font=("Arial", 12))
        self.label_info.pack(pady=10)

        # Labels para exibir detalhes do item selecionado
        self.label_codigo = tk.Label(self.win, text='Código: ')
        self.label_codigo.pack(pady=5)

        self.label_detalhes = tk.Label(self.win, text='Detalhes: ')
        self.label_detalhes.pack(pady=5)

        self.label_total = tk.Label(self.win, text='Total: ')
        self.label_total.pack(pady=5)

        self.label_data = tk.Label(self.win, text='Data: ')
        self.label_data.pack(pady=5)

        # Bind para selecionar item
        self.treeRelatorio.bind('<<TreeviewSelect>>', self.on_item_selected)

        # Comportamento de fechamento
        self.win.protocol("WM_DELETE_WINDOW", self.fechar)

        self.carregarRelatorio()

    def fechar(self):
        self.win.destroy()  # Fecha a janela do relatório de vendas
        self.tela_principal.voltar()  # Retorna ao menu principal

    def carregarRelatorio(self):
        registros = self.objBD.selecionarVendas()
        for item in registros:
            self.treeRelatorio.insert('', 'end', values=item)

    def on_item_selected(self, event):
        # Obtém o item selecionado
        selected_item = self.treeRelatorio.focus()
        item_values = self.treeRelatorio.item(selected_item, 'values')

        if item_values:
            # Atualiza os labels com os dados do item selecionado
            codigo = item_values[0]
            detalhes = item_values[1]

            self.label_codigo.config(text=f'Código: {codigo}')
            self.label_detalhes.config(text=f'{detalhes.format(',','\n')}')
            self.label_total.config(text=f'Total: R${float(item_values[2]):.2f}')
            self.label_data.config(text=f'Data: {item_values[3]}')

            # Imprime os detalhes
            print(f'Detalhes: {detalhes}')


# Programa Principal
if __name__ == "__main__":
    janela = tk.Tk()
    tela_principal = TelaPrincipal(janela)
    janela.mainloop()