import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Função para conectar ao banco de dados
def conectar_banco():
    return sqlite3.connect("partidas.db")

# Função para criar a tabela 'partidas' se não existir
def criar_tabela_partidas():
    conn = conectar_banco()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS partidas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_competicao TEXT NOT NULL,
                data TEXT NOT NULL,
                hora TEXT NOT NULL,
                dia_semana TEXT NOT NULL,
                cidade TEXT NOT NULL,
                estadio TEXT NOT NULL,
                time_casa TEXT NOT NULL,
                gols_time_casa INTEGER NOT NULL,
                time_visitante TEXT NOT NULL,
                gols_time_visitante INTEGER NOT NULL,
                publico INTEGER,
                renda REAL,
                resultado TEXT
            )
        """)
        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Erro ao criar a tabela 'partidas': {e}")
    finally:
        conn.close()

# Função para calcular o resultado com base nos gols
def calcular_resultado(gol_casa, gol_visitante, time_casa, time_visitante):
    if gol_casa > gol_visitante:
        return time_casa  # Retorna o nome do time da casa
    elif gol_casa < gol_visitante:
        return time_visitante  # Retorna o nome do time visitante
    else:
        return "Empate"

# Função para atualizar os resultados das partidas existentes
def atualizar_resultados_existentes():
    conn = conectar_banco()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, gols_time_casa, gols_time_visitante, time_casa, time_visitante FROM partidas")
        partidas = cursor.fetchall()
        for partida in partidas:
            id_partida, gols_casa, gols_visitante, time_casa, time_visitante = partida
            resultado = calcular_resultado(gols_casa, gols_visitante, time_casa, time_visitante)
            cursor.execute("UPDATE partidas SET resultado = ? WHERE id = ?", (resultado, id_partida))
        conn.commit()
        st.success("Resultados atualizados com sucesso!")
    except sqlite3.Error as e:
        st.error(f"Erro ao atualizar resultados: {e}")
    finally:
        conn.close()

# Função para cadastrar uma nova partida
def cadastrar_partida():
    st.title("Cadastrar Partida")
    with st.form("form_cadastro"):
        tipo_competicao = st.selectbox("Tipo de Competição", ["Campeonato Paulista", "Campeonato Brasileiro", "Copa do Brasil", "Copa Sul-Americana", "Copa Libertadores"])
        data = st.date_input("Data da Partida")
        hora = st.time_input("Hora da Partida")
        dia_semana = data.strftime("%A")
        cidade = st.text_input("Cidade")
        estadio = st.text_input("Estádio")
        time_casa = st.text_input("Time da Casa")
        gol_casa = st.number_input("Gols do Time da Casa", min_value=0, step=1)
        time_visitante = st.text_input("Time Visitante")
        gol_visitante = st.number_input("Gols do Time Visitante", min_value=0, step=1)
        publico = st.number_input("Público", min_value=0, step=1)
        renda = st.number_input("Renda", min_value=0.0, step=0.01)

        submit = st.form_submit_button("Cadastrar Partida")

        if submit:
            resultado = calcular_resultado(gol_casa, gol_visitante, time_casa, time_visitante)
            conn = conectar_banco()
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO partidas (tipo_competicao, data, hora, dia_semana, cidade, estadio, time_casa, gols_time_casa, time_visitante, gols_time_visitante, publico, renda, resultado)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (tipo_competicao, str(data), str(hora), dia_semana, cidade, estadio, time_casa, gol_casa, time_visitante, gol_visitante, publico, renda, resultado))
                conn.commit()
                st.success("Partida cadastrada com sucesso!")
            except sqlite3.Error as e:
                st.error(f"Erro ao cadastrar a partida: {e}")
            finally:
                conn.close()

# Função para exibir partidas cadastradas
def exibir_partidas():
    st.title("Partidas Cadastradas")
    conn = conectar_banco()
    query = "SELECT * FROM partidas"
    try:
        df = pd.read_sql_query(query, conn)
        if not df.empty:
            st.dataframe(df)
        else:
            st.warning("Nenhuma partida cadastrada.")
    except pd.io.sql.DatabaseError as e:
        st.error(f"Erro ao acessar o banco de dados: {e}")
    finally:
        conn.close()

# Função principal para o menu lateral
def main():
    st.sidebar.title("Menu")
    opcoes = st.sidebar.radio("Navegação", ["Cadastrar Partida", "Partidas Cadastradas", "Atualizar Resultados"])

    if opcoes == "Cadastrar Partida":
        cadastrar_partida()
    elif opcoes == "Partidas Cadastradas":
        exibir_partidas()
    elif opcoes == "Atualizar Resultados":
        atualizar_resultados_existentes()

# Inicialização do app
if __name__ == "__main__":
    criar_tabela_partidas()
    main()

