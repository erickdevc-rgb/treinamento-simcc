from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI(
    title="API Observatório SIMCC",
    description="API robusta para o gerenciamento de pesquisadores e produções científicas.",
    version="1.1.0"
)

# ==============================================================================
# CONFIGURAÇÃO CENTRALIZADA DO BANCO DE DADOS
# ==============================================================================
DB_CONFIG = {
    "host": "172.22.224.1",
    "port": "5437",
    "database": "BD_PESQUISADOR",
    "user": "postgres",
    "password": "1234"
}

def get_db_connection():
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        print(f"Erro crítico de conexão com o banco de dados: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Não foi possível estabelecer conexão com o banco de dados."
        )

# ==============================================================================
# SCHEMAS PYDANTIC (Validação de Dados de Entrada para o Swagger)
# ==============================================================================
class PesquisadorCreate(BaseModel):
    id: str
    nome: str
    instituicao: Optional[str] = None

class PesquisadorUpdate(BaseModel):
    nome: str
    instituicao: Optional[str] = None

class ProducaoCreate(BaseModel):
    producoes_id: str
    pesquisadores_id: str
    nomeartigo: str
    anoartigo: Optional[int] = None
    issn: Optional[str] = None

class ProducaoUpdate(BaseModel):
    nomeartigo: str
    anoartigo: Optional[int] = None
    issn: Optional[str] = None


# ==============================================================================
# ENDPOINTS: PESQUISADORES
# ==============================================================================

@app.get("/pesquisadores", tags=["Pesquisadores"])
def listar_todos_pesquisadores():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("SELECT * FROM pesquisadores LIMIT 50")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


@app.post("/pesquisadores", status_code=status.HTTP_201_CREATED, tags=["Pesquisadores"])
def criar_pesquisador(pesquisador: PesquisadorCreate):
    conn = get_db_connection()
    try:
        with conn: # Efetua COMMIT automaticamente se der certo; ROLLBACK se falhar
            with conn.cursor() as cursor:
                query = "INSERT INTO pesquisadores (id, nome, instituicao) VALUES (%s, %s, %s)"
                cursor.execute(query, (pesquisador.id, pesquisador.nome, pesquisador.instituicao))
        return {"message": "Pesquisador criado com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Erro ao inserir: {e}")
    finally:
        conn.close()


@app.put("/pesquisadores/{pesquisador_id}", tags=["Pesquisadores"])
def atualizar_pesquisador(pesquisador_id: str, pesquisador: PesquisadorUpdate):
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cursor:
                query = "UPDATE pesquisadores SET nome = %s, instituicao = %s WHERE id = %s"
                cursor.execute(query, (pesquisador.nome, pesquisador.instituicao, pesquisador_id))
        return {"message": "Pesquisador atualizado com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Erro ao atualizar: {e}")
    finally:
        conn.close()


@app.delete("/pesquisadores/{pesquisador_id}", tags=["Pesquisadores"])
def deletar_pesquisador(pesquisador_id: str):
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cursor:
                query = "DELETE FROM pesquisadores WHERE id = %s"
                cursor.execute(query, (pesquisador_id,))
        return {"message": "Pesquisador deletado com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Erro ao deletar: {e}")
    finally:
        conn.close()


# ==============================================================================
# ENDPOINTS: PRODUÇÕES Científicas
# ==============================================================================

@app.get("/pesquisadores/{pesquisador_id}/producoes", tags=["Produções"])
def listar_producoes_por_pesquisador(pesquisador_id: str):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        query = "SELECT * FROM producoes WHERE pesquisadores_id = %s"
        cursor.execute(query, (pesquisador_id,))
        producoes = cursor.fetchall()
        
        if not producoes:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhuma produção encontrada para este pesquisador.")
        return producoes
    finally:
        cursor.close()
        conn.close()


@app.post("/producoes", status_code=status.HTTP_201_CREATED, tags=["Produções"])
def criar_producao(producao: ProducaoCreate):
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cursor:
                query = """INSERT INTO producoes (producoes_id, pesquisadores_id, nomeartigo, anoartigo, issn) 
                           VALUES (%s, %s, %s, %s, %s)"""
                cursor.execute(query, (producao.producoes_id, producao.pesquisadores_id, producao.nomeartigo, producao.anoartigo, producao.issn))
        return {"message": "Produção criada com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Erro ao inserir produção: {e}")
    finally:
        conn.close()


@app.put("/producoes/{produco_id}", tags=["Produções"])
def atualizar_producao(produco_id: str, producao: ProducaoUpdate):
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cursor:
                query = """UPDATE producoes SET nomeartigo = %s, anoartigo = %s, issn = %s 
                           WHERE producoes_id = %s"""
                cursor.execute(query, (producao.nomeartigo, producao.anoartigo, producao.issn, produco_id))
        return {"message": "Produção atualizada com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Erro ao atualizar produção: {e}")
    finally:
        conn.close()


@app.delete("/producoes/{produco_id}", tags=["Produções"])
def deletar_producao(produco_id: str):
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cursor:
                query = "DELETE FROM producoes WHERE producoes_id = %s"
                cursor.execute(query, (produco_id,))
        return {"message": "Produção deletada com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Erro ao deletar produção: {e}")
    finally:
        conn.close()