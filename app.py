import streamlit as st
from dotenv import load_dotenv
import os
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI

# Configuração do CSS personalizado
st.markdown("""
<style>
    /* Cores principais */
    :root {
        --primary: #2563EB;
        --secondary: #7C3AED;
        --background: #F8FAFC;
        --text: #1E293B;
        --accent: #10B981;
    }
    
    /* Estilos gerais */
    .stApp {
        background-color: var(--background);
    }
    
    h1 {
        color: var(--primary) !important;
        border-bottom: 2px solid var(--secondary);
        padding-bottom: 10px;
    }
    
    .stButton>button {
        background-color: var(--primary) !important;
        color: white !important;
        border-radius: 8px !important;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background-color: var(--secondary) !important;
    }
    
    .stTextInput>div>div>input {
        border: 2px solid var(--primary) !important;
        border-radius: 8px !important;
    }
    
    /* Container personalizado */
    .custom-container {
        background: linear-gradient(135deg, #E0F2FE 0%, #F0FDF4 100%);
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 30px;
    }
    
    /* Rodapé */
    footer {
        color: var(--text);
        opacity: 0.8;
        font-size: 0.9em;
        text-align: center;
        margin-top: 30px;
    }
</style>
""", unsafe_allow_html=True)

# Carregar variáveis de ambiente
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    st.error("⚠️ Chave da OpenAI não encontrada. Verifique seu arquivo .env ou Secrets.")
    st.stop()

# Inicializar session_state
if 'input_pergunta' not in st.session_state:
    st.session_state.input_pergunta = ""

# Funções RAG (mantidas iguais às anteriores)
@st.cache_resource
def load_data():
    PDF_PATH = "Chatbot_SAC.pdf"
    if not os.path.exists(PDF_PATH):
        st.error(f"⚠️ Arquivo {PDF_PATH} não encontrado.")
        st.stop()
    
    text = load_pdf(PDF_PATH)
    chunks = process_text(text)
    return create_vector_store(chunks, OPENAI_API_KEY)

def load_pdf(file_path):
    reader = PdfReader(file_path)
    return " ".join([page.extract_text() for page in reader.pages])

def process_text(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return splitter.split_text(text)

def create_vector_store(chunks, api_key):
    embeddings = OpenAIEmbeddings(openai_api_key=api_key)
    return FAISS.from_texts(chunks, embeddings)

def get_answer(query, vector_store):
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7, openai_api_key=OPENAI_API_KEY)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
    )
    return qa_chain.run(query)

# Interface principal
st.title("✈️ Chatbot ANAC - Atendimento de Reclamações Aéreas")

# Container com fundo diferenciado
with st.container():
    st.markdown("""
    <div class="custom-container">
        <h3 style='color: #2563EB;'>Como posso ajudar hoje?</h3>
        <p>Explore suas dúvidas sobre direitos do passageiro, reclamações e regulamentações aéreas.</p>
    </div>
    """, unsafe_allow_html=True)

# Perguntas sugeridas
st.subheader("🔍 Perguntas Frequentes")
perguntas_sugeridas = [
    "Qual o principal motivo de reclamação?",
    "Quais as reclamações sobre bagagem?",
    "Quais os objetivos da ANAC com a Resolução 400/2016?",
    "Quais as atividades desempenhadas pela ANAC?",
    "O que diz o atual marco regulatório do setor aéreo?",
    "Como encontrar passagens baratas?",
    "Quais são os direitos do passageiro em voos atrasados?"
]

cols = st.columns(2)
for i, pergunta in enumerate(perguntas_sugeridas):
    with cols[i % 2]:
        if st.button(pergunta, key=f"pergunta_{i}"):
            st.session_state.input_pergunta = pergunta

# Campo de pergunta
query = st.text_input(
    "**Digite sua pergunta:**", 
    value=st.session_state.input_pergunta, 
    key="input_pergunta",
    placeholder="Ex: Quais os direitos em caso de cancelamento?"
)

# Rodapé
st.markdown("""
<footer>
    ✈️ Chatbot oficial para consultas ANAC | Digite 'sair' a qualquer momento
</footer>
""", unsafe_allow_html=True)

# Processamento das perguntas (mantido igual)
vector_store = load_data()

if query:
    if query.lower() == "sair":
        st.success("✅ Chatbot encerrado. Obrigado!")
        st.stop()
    else:
        with st.spinner("🔍 Buscando informações..."):
            answer = get_answer(query, vector_store)
        
        st.markdown(f"**Resposta:**\n\n{answer}")
        st.session_state.input_pergunta = ""
        st.rerun()
