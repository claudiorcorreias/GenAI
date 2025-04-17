import streamlit as st
# Inicialização do estado da sessão (antes de qualquer widget)
# Inicialização segura do session_state
if 'input_pergunta' not in st.session_state:
    st.session_state.input_pergunta = ""
if 'last_query' not in st.session_state:
    st.session_state.last_query = ""
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = None

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


# Funções RAG
@st.cache_resource(show_spinner="Processando PDF...")
def load_and_process_pdf(file_path):
    """Carrega e processa o PDF apenas uma vez"""
    reader = PdfReader(file_path)
    text = " ".join([page.extract_text() for page in reader.pages])
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_text(text)
    
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    vector_store = FAISS.from_texts(chunks, embeddings)
    
    return vector_store

def get_answer(query, vector_store):
    """Obtém resposta usando a cadeia RAG"""
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.7,
        openai_api_key=OPENAI_API_KEY
    )
    
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

# Carregar PDF e criar vetor store (apenas uma vez)
if st.session_state.vector_store is None:
    PDF_PATH = "Chatbot_SAC.pdf"
    if os.path.exists(PDF_PATH):
        try:
            st.session_state.vector_store = load_and_process_pdf(PDF_PATH)
            st.success("✅ Base de conhecimento carregada com sucesso!")
        except Exception as e:
            st.error(f"⚠️ Erro ao processar o PDF: {str(e)}")
            st.stop()
    else:
        st.error(f"⚠️ Arquivo {PDF_PATH} não encontrado.")
        st.stop()

# Widget controlado para input
def submit_query():
    """Callback para envio da pergunta"""
    st.session_state.last_query = st.session_state.input_pergunta
    st.session_state.input_pergunta = ""

# Campo de pergunta com tratamento de estado
st.text_input(
    "Digite sua pergunta:",
    value=st.session_state.input_pergunta,
    key="input_pergunta",
    on_change=submit_query,
    placeholder="Ex: Quais meus direitos em caso de atraso?"
)


# Processamento da consulta
if st.session_state.last_query:
    if st.session_state.last_query.lower() == "sair":
        st.info("Atendimento encerrado. Obrigado!")
        st.stop()
    else:
        with st.spinner("Processando sua pergunta..."):
            try:
                answer = get_answer(
                    st.session_state.last_query,
                    st.session_state.vector_store
                )
                st.write("**Sua pergunta:**", st.session_state.last_query)
                st.write("**Resposta:**", answer)
                
                # Adiciona ao histórico
                if 'history' not in st.session_state:
                    st.session_state.history = []
                st.session_state.history.append(
                    (st.session_state.last_query, answer)
                )
                
            except Exception as e:
                st.error(f"⚠️ Erro ao processar sua pergunta: {str(e)}")

# Exibir histórico se existir
if 'history' in st.session_state and st.session_state.history:
    with st.expander("📜 Histórico de Conversas"):
        for i, (q, a) in enumerate(st.session_state.history, 1):
            st.write(f"**Consulta {i}:** {q}")
            st.write(f"**Resposta {i}:** {a}")
            st.write("---")
