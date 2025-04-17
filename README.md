# Chatbot ANAC - Análise de Reclamações Aéreas

## 📌 Objetivo
Automatizar a análise de reclamações do canal "Fale com a ANAC" usando RAG.

## 🛠 Tecnologias
- **LLM**: OpenAI `gpt-3.5-turbo`
- **Embeddings**: OpenAI `text-embedding-3-small`
- **Vectorstore**: FAISS
- **Framework**: LangChain

## 🚀 Como Executar
1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure sua chave OpenAI no arquivo `info.env`
3. Execute:
   ```bash
   streamlit run app.py
   ```

## 📊 Resultados Esperados
- Redução de 60% no tempo de análise manual
- Identificação automática de padrões de reclamações
