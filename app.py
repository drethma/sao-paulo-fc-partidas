import streamlit as st
import sqlite3
from datetime import datetime

# Funções auxiliares
def conectar_banco():
    return sqlite3.connect("sao_paulo_fc.db")

def criar_tabela():
    conexao = conectar_banco()
    cursor = conexao.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jogos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data DATE,
            dia_semana TEXT,
            cidade TEXT,
            estadio TEXT,
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

def atualizar_banco():
    conexao = conectar_banco()
    cursor = conexao.cursor()
    try:
        cursor.execute("ALTER TABLE jogos ADD COLUMN estadio TEXT")
        conexao.commit()
    except sqlite3.OperationalError:
        # O campo já existe
        pass
    finally:
        conexao.close()

def calcular_dia_semana(data):
    dias = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
    return dias[data.weekday()]

def calcular_resultado(gols_casa, gols_visitante, time_casa, time_visitante):
    if gols_casa > gols_visitante:
        return time_casa
    elif gols_casa < gols_visitante:
        return time_visitante
    else:
        return "EMPATE"

# Criar banco de dados, se necessário
criar_tabela()
atualizar_banco()

# Sidebar com menu suspenso
st.sidebar.title("Menu")
pagina = st.sidebar.selectbox("Navegação", ["Cadastro de Jogos", "Editar Partidas", "Visualizar Partidas"])

# Página de cadastro
if pagina == "Cadastro de Jogos":
    st.title("Cadastro de Jogos")
    with st.form("form_cadastro"):
        data = st.date_input("Data")
        dia_semana = calcular_dia_semana(data)
        st.text(f"Dia da Semana: {dia_semana}")
        cidade = st.text_input("Cidade")
        estadio = st.text_input("Estádio")
        competicao = st.selectbox("Competição", [
            "Campeonato Paulista", "Copa do Brasil", 
            "Campeonato Brasileiro", "Copa Sulamericana", 
            "Copa Libertadores"
        ])
        time_casa = st.text_input("Time Casa")
        gols_casa = st.number_input("Gols Time Casa", min_value=0, step=1)
        gols_visitante = st.number_input("Gols Time Visitante", min_value=0, step=1)
        time_visitante = st.text_input("Time Visitante")
        renda = st.number_input("Renda", min_value=0.0, step=0.01, format="%.2f")
        publico = st.number_input("Público", min_value=0, step=1)
        gols = st.text_area("Descrição dos Gols")
        
        if st.form_submit_button("Cadastrar"):
            resultado = calcular_resultado(gols_casa, gols_visitante, time_casa, time_visitante)
            conexao = conectar_banco()
            cursor = conexao.cursor()
            cursor.execute("""
                INSERT INTO jogos (data, dia_semana, cidade, estadio, competicao, time_casa, gols_time_casa, gols_time_visitante, time_visitante, resultado, renda, publico, gols)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (data, dia_semana, cidade, estadio, competicao, time_casa, gols_casa, gols_visitante, time_visitante, resultado, renda, publico, gols))
            conexao.commit()
            conexao.close()
            st.success("Jogo cadastrado com sucesso!")

# Página de edição
elif pagina == "Editar Partidas":
    st.title("Editar Partidas")
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    cursor.execute("""
        SELECT id, data, dia_semana, cidade, estadio, competicao, time_casa, 
               gols_time_casa, gols_time_visitante, time_visitante, 
               resultado, renda, publico, gols 
        FROM jogos
    """)
    partidas = cursor.fetchall()
    conexao.close()

    if partidas:
        partida_selecionada = st.selectbox(
            "Selecione uma partida para editar",
            partidas,
            format_func=lambda x: f"{x[1]} - {x[6]} x {x[9]} ({x[5]})"
        )

        if partida_selecionada:
            partida_id = partida_selecionada[0]
            data = st.date_input("Data", value=datetime.strptime(partida_selecionada[1], "%Y-%m-%d"))
            dia_semana = calcular_dia_semana(data)
            st.text(f"Dia da Semana: {dia_semana}")
            cidade = st.text_input("Cidade", partida_selecionada[3])
            estadio = st.text_input("Estádio", partida_selecionada[4])
            competicao = st.selectbox("Competição", [
                "Campeonato Paulista", "Copa do Brasil", 
                "Campeonato Brasileiro", "Copa Sulamericana", 
                "Copa Libertadores"
            ], index=["Campeonato Paulista", "Copa do Brasil", "Campeonato Brasileiro", 
                      "Copa Sulamericana", "Copa Libertadores"].index(partida_selecionada[5]))
            time_casa = st.text_input("Time Casa", partida_selecionada[6])
            gols_time_casa = st.number_input("Gols Time Casa", min_value=0, step=1, value=partida_selecionada[7])
            gols_time_visitante = st.number_input("Gols Time Visitante", min_value=0, step=1, value=partida_selecionada[8])
            time_visitante = st.text_input("Time Visitante", partida_selecionada[9])
            resultado = calcular_resultado(gols_time_casa, gols_time_visitante, time_casa, time_visitante)
            st.text(f"Resultado: {resultado}")
            renda = st.number_input("Renda", min_value=0.0, step=0.01, format="%.2f", value=partida_selecionada[11])
            publico = st.number_input("Público", min_value=0, step=1, value=partida_selecionada[12])
            gols = st.text_area("Descrição dos Gols", partida_selecionada[13])

            if st.button("Salvar Alterações"):
                conexao = conectar_banco()
                cursor = conexao.cursor()
                cursor.execute("""
                    UPDATE jogos
                    SET data = ?, dia_semana = ?, cidade = ?, estadio = ?, competicao = ?, 
                        time_casa = ?, gols_time_casa = ?, gols_time_visitante = ?, 
                        time_visitante = ?, resultado = ?, renda = ?, publico = ?, gols = ?
                    WHERE id = ?
                """, (data, dia_semana, cidade, estadio, competicao, time_casa, gols_time_casa, 
                      gols_time_visitante, time_visitante, resultado, renda, publico, gols, partida_id))
                conexao.commit()
                conexao.close()
                st.success("Partida atualizada com sucesso!")
    else:
        st.info("Nenhuma partida cadastrada.")

# Página de visualização
elif pagina == "Visualizar Partidas":
    st.title("Visualizar Partidas")
    conexao = conectar_banco()
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT 
            data AS "Data", 
            dia_semana AS "Dia da Semana", 
            cidade AS "Cidade", 
            estadio AS "Estádio",
            competicao AS "Competição", 
            time_casa AS "Time Casa", 
            gols_time_casa AS "Gols Time Casa", 
            gols_time_visitante AS "Gols Time Visitante", 
            time_visitante AS "Time Visitante", 
            resultado AS "Resultado", 
            renda AS "Renda", 
            publico AS "Público", 
            gols AS "Descrição dos Gols"
        FROM jogos
    """)
    partidas = cursor.fetchall()
    colunas = [descricao[0] for descricao in cursor.description]
    conexao.close()
    
    if partidas:
        st.dataframe({colunas[i]: [row[i] for row in partidas] for i in range(len(colunas))})
    else:
        st.info("Nenhuma partida cadastrada.")
