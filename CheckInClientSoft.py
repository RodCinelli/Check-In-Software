import sqlite3

class HotelSoftLife:
    def __init__(self):
        self.conn = sqlite3.connect('hotel_soft_life.db')
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS hospedes (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            email TEXT NOT NULL,
            telefone TEXT NOT NULL,
            quarto INTEGER
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS quartos (
            numero INTEGER PRIMARY KEY,
            ocupado BOOLEAN NOT NULL,
            hospede_id INTEGER,
            FOREIGN KEY (hospede_id) REFERENCES hospedes (id)
        )
        """)

        self.conn.commit()

    def cadastrar_hospede(self, id_hospede, nome, email, telefone):
        cursor = self.conn.cursor()

        # Verifica se já existe um hóspede com o mesmo ID
        cursor.execute("SELECT id FROM hospedes WHERE id = ?", (id_hospede,))
        hospede_existente = cursor.fetchone()

        if not hospede_existente:
            cursor.execute("""
            INSERT INTO hospedes (id, nome, email, telefone) VALUES (?, ?, ?, ?)
            """, (id_hospede, nome, email, telefone))
            self.conn.commit()
        else:
            print(f"Já existe um hóspede cadastrado com o ID {id_hospede}. Tente novamente com um ID diferente.")

    def listar_hospedes(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM hospedes")
        hospedes = cursor.fetchall()

        for hospede in hospedes:
            print(f'ID: {hospede[0]}, Nome: {hospede[1]}, Email: {hospede[2]}, Telefone: {hospede[3]}')

    def adicionar_quarto(self, numero_quarto):
        cursor = self.conn.cursor()
        cursor.execute("SELECT numero FROM quartos WHERE numero = ?", (numero_quarto,))
        quarto = cursor.fetchone()

        if not quarto:
            cursor.execute("""
            INSERT INTO quartos (numero, ocupado) VALUES (?, ?)
            """, (numero_quarto, False))
            self.conn.commit()
        else:
            print(f'O quarto {numero_quarto} já existe no banco de dados.')

    def check_in(self, id_hospede, numero_quarto):
        cursor = self.conn.cursor()
        cursor.execute("SELECT ocupado FROM quartos WHERE numero = ?", (numero_quarto,))
        quarto = cursor.fetchone()

        if quarto and not quarto[0]:
            cursor.execute("""
            UPDATE quartos SET ocupado = ?, hospede_id = ? WHERE numero = ?
            """, (True, id_hospede, numero_quarto))

            cursor.execute("""
            UPDATE hospedes SET quarto = ? WHERE id = ?
            """, (numero_quarto, id_hospede))
            self.conn.commit()
            print(f'Hóspede {id_hospede} fez check-in no quarto {numero_quarto}.')
        else:
            print('Quarto já está ocupado.')

    def check_out(self, id_hospede):
        cursor = self.conn.cursor()
        cursor.execute("SELECT quarto FROM hospedes WHERE id = ?", (id_hospede,))
        quarto = cursor.fetchone()

        if quarto:
            cursor.execute("""
            UPDATE quartos SET ocupado = ?, hospede_id = ? WHERE numero = ?
            """, (False, None, quarto[0]))

            cursor.execute("""
            UPDATE hospedes SET quarto = ? WHERE id = ?
            """, (None, id_hospede))
            self.conn.commit()
            print(f'Hóspede {id_hospede} fez check-out do quarto {quarto[0]}.')
        else:
            print('Hóspede não encontrado.')

    def excluir_hospede(self, id_hospede):
        cursor = self.conn.cursor()

        cursor.execute("SELECT id FROM hospedes WHERE id = ?", (id_hospede,))
        hospede_existente = cursor.fetchone()

        if hospede_existente:
            cursor.execute("DELETE FROM hospedes WHERE id = ?", (id_hospede,))
            cursor.execute("UPDATE quartos SET ocupado = 0, hospede_id = NULL WHERE hospede_id = ?", (id_hospede,))
            self.conn.commit()
            print(f"Hóspede com ID {id_hospede} excluído com sucesso!")
        else:
            print(f"Hóspede com ID {id_hospede} não encontrado.")


    def close(self):
        self.conn.close()

if __name__ == '__main__':
    hotel = HotelSoftLife()

    # Verifica se a tabela quartos está vazia
    cursor = hotel.conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM quartos")
    quartos_count = cursor.fetchone()[0]

    # Adiciona quartos somente se a tabela estiver vazia
    if quartos_count == 0:
        for i in range(1, 6):
            hotel.adicionar_quarto(i)

    while True:
        print("\nMenu:")
        print("1. Cadastrar hóspede")
        print("2. Listar hóspedes")
        print("3. Realizar check-in")
        print("4. Realizar check-out")
        print("5. Excluir hóspede")
        print("6. Sair")

        opcao = int(input("Escolha uma opção: "))

        if opcao == 1:
            id_hospede = int(input("Digite o ID do hóspede: "))
            nome = input("Digite o nome do hóspede: ")
            email = input("Digite o email do hóspede: ")
            telefone = input("Digite o telefone do hóspede: ")
            hotel.cadastrar_hospede(id_hospede, nome, email, telefone)
            print("Hóspede cadastrado com sucesso!")
        elif opcao == 2:
            hotel.listar_hospedes()
        elif opcao == 3:
            id_hospede = int(input("Digite o ID do hóspede: "))
            numero_quarto = int(input("Digite o número do quarto: "))
            hotel.check_in(id_hospede, numero_quarto)
        elif opcao == 4:
            id_hospede = int(input("Digite o ID do hóspede: "))
            hotel.check_out(id_hospede)
        elif opcao == 5:
            id_hospede = int(input("Digite o ID do hóspede que deseja excluir: "))
            hotel.excluir_hospede(id_hospede)
        elif opcao == 6:
            break
        else:
            print("Opção inválida. Tente novamente.")

    # Fechando a conexão com o banco de dados
    hotel.close()

