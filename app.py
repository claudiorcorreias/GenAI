import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI

# Configuração da página
st.set_page_config(page_title="Chatbot ANAC - RAG", page_icon="✈️")

# Sidebar (upload de PDF)
with st.sidebar:
    st.header("Configurações")
    pdf_file = st.file_uploader("Carregue o PDF da ANAC", type="pdf")
    openai_key = st.text_input("Insira sua API Key da OpenAI", type="password")

# Funções RAG (iguais ao seu código)
def load_pdf(file):
    reader = PdfReader(file)
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
st.write("**Como usar**: Carregue o PDF da ANAC e faça perguntas sobre direitos do passageiro.")

if pdf_file and openai_key:
    text = load_pdf(pdf_file)
    chunks = process_text(text)
    vector_store = create_vector_store(chunks, openai_key)
    
    query = st.text_input("Digite sua pergunta (ex: 'Quais os direitos em caso de cancelamento?')")
    if query:
        answer = get_answer(query, vector_store, openai_key)
        st.write("**Resposta:**", answer)
else:
    st.warning("⚠️ Carregue um PDF e insira a API Key da OpenAI para começar.")
