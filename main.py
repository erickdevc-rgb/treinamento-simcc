from fastapi import FastAPI, HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI(title="API Observatório SIMCC")

# ==============================================================================
# CONEXÃO COM O BANCO DE DADOS
# ==============================================================================
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host="172.22.224.1",         # O IP do Windows que você achou antes
            port="5437",                 # A porta correta descoberta na imagem!
            database="BD_PESQUISADOR",   # Atenção: Começa com B
            user="postgres",
            password="1234" # (Provavelmente '1234')
        )
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco: {e}")
        return None

# ==============================================================================
# ROTA EXIGIDA: Listar produções de um determinado pesquisador
# ==============================================================================
@app.get("/pesquisadores/{pesquisador_id}/producoes")
def listar_producoes_por_pesquisador(pesquisador_id: str):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Erro de conexão com o banco de dados.")
    
    # RealDictCursor converte as linhas do banco em dicionários Python (formato JSON)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Consulta SQL filtrando pelo ID recebido na URL da API
    query = "SELECT * FROM producoes WHERE pesquisadores_id = %s"
    cursor.execute(query, (pesquisador_id,))
    producoes = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    # Se o banco não retornar nada, devolvemos o erro padrão HTTP 404
    if not producoes:
        raise HTTPException(status_code=404, detail="Nenhuma produção encontrada para este pesquisador.")
        
    return producoes

# ==============================================================================
# ROTA ADICIONAL: Listar todos os pesquisadores (CRUD - Read)
# ==============================================================================
@app.get("/pesquisadores")
def listar_todos_pesquisadores():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Erro de conexão com o banco de dados.")
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM pesquisadores LIMIT 50")
    pesquisadores = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return pesquisadores