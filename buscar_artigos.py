import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import PGVector

# 1. Carrega a chave da API
load_dotenv()

# Coloque OS MESMOS dados que você usou no povoar_vetores.py
DB_USER = "postgres"
DB_PASS = "1234"
DB_HOST = "172.22.224.1"
DB_PORT = "5437"
DB_NAME = "BD_PESQUISADOR"

CONNECTION_STRING = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def main():
    print("Conectando ao cérebro vetorial do PostgreSQL...")
    
    # 2. Inicializa o mesmo modelo de Embeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # 3. Conecta na coleção que criamos no passo anterior
    db_vetorial = PGVector(
        connection_string=CONNECTION_STRING,
        embedding_function=embeddings,
        collection_name="artigos_simcc"
    )
    
    # 4. A Mágica: Vamos fazer uma busca semântica!
    # Mude esta frase para testar assuntos que você sabe que existem nos artigos do seu professor
    pergunta = "Pesquisas sobre doenças no sangue ou HIV"
    print(f"\nBuscando por: '{pergunta}'\n")
    
    # O banco vai trazer os 3 resultados que mais se parecem com o significado da pergunta
    resultados = db_vetorial.similarity_search(pergunta, k=3)
    
    print("--- RESULTADOS ENCONTRADOS ---")
    for i, doc in enumerate(resultados, 1):
        # Acessamos o texto do artigo e o ID original que salvamos nos metadados
        titulo = doc.page_content
        id_banco = doc.metadata.get('producoes_id', 'Sem ID')
        print(f"{i}. [ID: {id_banco}] {titulo}")

if __name__ == "__main__":
    main()