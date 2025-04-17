import os
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI

# Carrega variáveis do .env
load_dotenv("info.env")

# Configuração
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Funções auxiliares
def load_pdf(file_path):
    with open(file_path, "rb") as file:
        reader = PdfReader(file)
        return " ".join([page.extract_text() for page in reader.pages])

def process_text(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    return splitter.split_text(text)

def create_vector_store(chunks):
    embeddings = OpenAIEmbeddings()  # Usa embeddings da OpenAI
    return FAISS.from_texts(chunks, embeddings)

# Chatbot com OpenAI
def get_answer(query, vector_store):
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)  # Modelo da OpenAI
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
    )
    return qa_chain.run(query)

# Interface de terminal
def main():
    print("\n--- Chatbot ANAC (OpenAI) ---")
    print("Carregando PDF...")

    try:
        text = load_pdf("Chatbot_SAC.pdf")  # Ajuste o caminho se necessário
        chunks = process_text(text)
        vector_store = create_vector_store(chunks)
        
        print("\nPronto! Faça perguntas sobre reclamações aéreas.")
        print("Exemplo: 'Quais são as reclamações sobre bagagens?'")
        print("Digite 'sair' para encerrar.\n")

        while True:
            query = input("Pergunta: ").strip()
            if query.lower() == "sair":
                break
            if query:
                answer = get_answer(query, vector_store)
                print("\nResposta:", answer, "\n")

    except Exception as e:
        print(f"\nErro: {str(e)}")
        print("Verifique:")
        print("- Se o arquivo .env está correto")
        print("- Se o PDF existe no diretório")

if __name__ == "__main__":
    main()
