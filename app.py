import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
import os

# Configuração da página
st.set_page_config(page_title="Chatbot ANAC - RAG", page_icon="✈️")

# --- 1. REMOVER INPUTS MANUAIS ---
# Carrega o PDF e a API Key automaticamente (ajuste os caminhos/conforme necessário)
PDF_PATH = "Chatbot_SAC.pdf"  # Coloque o PDF no mesmo diretório do script
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# --- FUNÇÕES RAG (MANTIDAS) ---
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

# --- INTERFACE STREAMLIT ---
st.title("Chatbot ANAC - Atendimento de Reclamações Aéreas")
st.write("""
**Instruções:**  
- Digite sua pergunta sobre direitos do passageiro (ex: _"Quais os direitos em caso de cancelamento?"_).  
- Para encerrar, digite **'sair'**.  
""")

# Inicialização do vetor store (automática)
if os.path.exists(PDF_PATH) and OPENAI_API_KEY:
    text = load_pdf(PDF_PATH)
    chunks = process_text(text)
    vector_store = create_vector_store(chunks, OPENAI_API_KEY)
    st.success("✅ PDF e API Key carregados com sucesso!")
else:
    st.error("⚠️ Arquivo PDF ou API Key não encontrados. Verifique o caminho do PDF ou a chave da OpenAI.")

# --- 2. CAMPO DE PERGUNTA + LIMPEZA APÓS RESPOSTA ---
query = st.text_input("Digite sua pergunta:", key="input_pergunta")

if query:
    if query.lower() == "sair":
        st.stop()  # Encerra o app
    else:
        answer = get_answer(query, vector_store, OPENAI_API_KEY)
        st.write("**Resposta:**", answer)
        
        # --- 3. LIMPAR CAMPO APÓS RESPOSTA ---
        st.session_state["input_pergunta"] = ""  # Reseta o input
        st.rerun()  # Força a atualização da interface
