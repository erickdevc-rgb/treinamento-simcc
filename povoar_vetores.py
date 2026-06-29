import os
import psycopg2
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import PGVector
from langchain_core.documents import Document

# 1. Carregar as variáveis de ambiente (.env)
load_dotenv()

# Configurações da sua base de dados PostgreSQL (ajuste se a senha ou utilizador forem diferentes)
DB_USER = "postgres"
DB_PASS = "1234"
DB_HOST = "172.22.224.1"
DB_PORT = "5437"
DB_NAME = "BD_PESQUISADOR" # Nome da sua base de dados

CONNECTION_STRING = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def obter_artigos_do_banco():
    """Procura os artigos reais guardados na tabela producoes"""
    conexao = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
    )
    cursor = conexao.cursor()
    
    # Vamos procurar o ID do artigo e o título (nomeartigo)
    cursor.execute("SELECT producoes_id, nomeartigo FROM producoes;")
    linhas = cursor.fetchall()
    
    cursor.close()
    conexao.close()
    return linhas

def main():
    print("Iniciando a conversão de artigos em vetores...")
    
    # 2. Inicializar o modelo de Embeddings da OpenAI usando a chave do .env
    # (Se for usar Gemini, mudaria para GoogleGenAIEmbeddings)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # 3. Obter os artigos do banco de dados
    artigos = obter_artigos_do_banco()
    if not artigos:
        print("Nenhum artigo encontrado na tabela 'producoes' para vetorizar.")
        return
        
    print(f"Encontrados {len(artigos)} artigos para processar.")
    
    # 4. Converter as linhas do banco no formato que o LangChain entende (Documents)
    documentos = []
    for uuid, titulo in artigos:
        if titulo:
            # O LangChain precisa do texto principal e pode guardar metadados (como o ID original)
            doc = Document(
                page_content=titulo,
                metadata={"producoes_id": str(uuid)}
            )
            documentos.append(doc)
            
    # 5. Usar o LangChain + pgvector para criar as tabelas vetoriais e guardar os dados
    # O LangChain criará automaticamente tabelas chamadas langchain_pg_collection e langchain_pg_embedding
    print("Enviando dados para a API e guardando os vetores no PostgreSQL (pgvector)...")
    
    db_vetorial = PGVector.from_documents(
        documents=documentos,
        embedding=embeddings,
        connection_string=CONNECTION_STRING,
        collection_name="artigos_simcc" # Nome da coleção de vetores
    )
    
    print("Sucesso! Todos os artigos foram vetorizados e guardados.")

if __name__ == "__main__":
    main()