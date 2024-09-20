import sqlite3


class Crud:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS produtos (
                codigo INTEGER PRIMARY KEY,
                nome TEXT NOT NULL,
                preco REAL NOT NULL
            )
        ''')

        # Criar tabela de vendas
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS vendas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                detalhes TEXT NOT NULL,
                total REAL NOT NULL,
                data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def inserirVenda(self, detalhes, total):
        self.cursor.execute('INSERT INTO vendas (detalhes, total) VALUES (?, ?)', (detalhes, total))
        self.conn.commit()

    def selecionarVendas(self):
        self.cursor.execute('SELECT * FROM vendas')
        return self.cursor.fetchall()
    def inserirDados(self, codigo, nome, preco):
        self.cursor.execute('INSERT INTO produtos (codigo, nome, preco) VALUES (?, ?, ?)', (codigo, nome, preco))
        self.conn.commit()

    def atualizarDados(self, codigo, nome, preco):
        self.cursor.execute('UPDATE produtos SET nome = ?, preco = ? WHERE codigo = ?', (nome, preco, codigo))
        self.conn.commit()

    def excluirDados(self, codigo):
        self.cursor.execute('DELETE FROM produtos WHERE codigo = ?', (codigo,))
        self.conn.commit()

    def selecionarDadosPorCodigo(self, codigo):
        self.cursor.execute('SELECT * FROM produtos WHERE codigo = ?', (codigo,))
        return self.cursor.fetchone()

    def selecionarTodosDados(self):
        self.cursor.execute('SELECT * FROM produtos')
        return self.cursor.fetchall()

    def __del__(self):
        self.conn.close()