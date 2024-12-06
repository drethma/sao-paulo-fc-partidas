import sqlite3

def criar_banco():
    conexao = sqlite3.connect("sao_paulo_fc.db")
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jogos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data DATE,
            dia_semana TEXT,
            cidade TEXT,
            competicao TEXT CHECK(competicao IN (
                'Campeonato Paulista', 
                'Copa do Brasil', 
                'Campeonato Brasileiro', 
                'Copa Sulamericana', 
                'Copa Libertadores')),
            time_casa TEXT,
            gols_time_casa INTEGER,
            gols_time_visitante INTEGER,
            time_visitante TEXT,
            resultado TEXT,
            renda REAL,
            publico INTEGER,
            gols TEXT
        )
    """)

    conexao.commit()
    conexao.close()

if __name__ == "__main__":
    criar_banco()
