import streamlit as st
from dotenv import load_dotenv
import os
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI

# Configuração da página
st.set_page_config(page_title="Chatbot ANAC - RAG", page_icon="✈️")

# Carregar variáveis de ambiente
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    st.error("⚠️ Chave da OpenAI não encontrada. Verifique seu arquivo .env ou Secrets.")
    st.stop()

# Inicializar session_state
if 'input_pergunta' not in st.session_state:
    st.session_state.input_pergunta = ""

# Funções RAG
def load_pdf(file_path):
    reader = PdfReader(file_path)
    return " ".join([page.extract_text() for page in reader.pages])

def process_text(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return splitter.split_text(text)

def create_vector_store(chunks, api_key):
    embeddings = OpenAIEmbeddings(openai_api_key=api_key)
    return FAISS.from_texts(chunks, embeddings)

def get_answer(query, vector_store, api_key):
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7, openai_api_key=api_key)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
    )
    return qa_chain.run(query)

# Interface principal
st.title("Chatbot ANAC - Atendimento de Reclamações Aéreas")
st.write("""
**Instruções:**  
- Digite sua pergunta sobre direitos do passageiro (ex: "Quais os direitos em caso de cancelamento?").  
- Para encerrar, digite **'sair'**.  
""")

# Carregar PDF e criar vetor store
PDF_PATH = "Chatbot_SAC.pdf"
if os.path.exists(PDF_PATH):
    text = load_pdf(PDF_PATH)
    chunks = process_text(text)
    vector_store = create_vector_store(chunks, OPENAI_API_KEY)
    st.success("✅ PDF carregado com sucesso!")
else:
    st.error(f"⚠️ Arquivo {PDF_PATH} não encontrado.")
    st.stop()

# Campo de pergunta com tratamento de estado
query = st.text_input("Digite sua pergunta:", value=st.session_state.input_pergunta, key="input_pergunta")

if query:
    if query.lower() == "sair":
        st.stop()
    else:
        answer = get_answer(query, vector_store, OPENAI_API_KEY)
        st.write("**Resposta:**", answer)
        
        # Limpar campo após resposta
        st.session_state.input_pergunta = ""
        st.experimental_rerun()
