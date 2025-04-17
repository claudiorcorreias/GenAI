# Adicione este CSS personalizado no início do seu app
st.markdown("""
<style>
    /* Cores principais */
    :root {
        --primary: #2563EB;  /* Azul vibrante */
        --secondary: #7C3AED; /* Roxo suave */
        --background: #F8FAFC; /* Fundo claro */
        --text: #1E293B;      /* Texto escuro */
        --accent: #10B981;    /* Verde fresco */
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
        transform: scale(1.02);
    }
    
    .stTextInput>div>div>input {
        border: 2px solid var(--primary) !important;
        border-radius: 8px !important;
    }
    
    /* Cards de perguntas */
    .question-card {
        background: linear-gradient(135deg, #E0F2FE 0%, #F0FDF4 100%);
        border-left: 4px solid var(--accent);
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
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

# Interface principal (substitua a seção atual)
st.title("✈️ Chatbot ANAC - Atendimento de Reclamações Aéreas")

# Container com fundo diferenciado
with st.container():
    st.markdown("""
    <div style='background: linear-gradient(135deg, #2563EB10 0%, #7C3AED10 100%); 
                padding: 20px; 
                border-radius: 12px;
                margin-bottom: 30px;'>
        <h3 style='color: #2563EB;'>Como posso ajudar hoje?</h3>
        <p>Explore suas dúvidas sobre direitos do passageiro, reclamações e regulamentações aéreas.</p>
    </div>
    """, unsafe_allow_html=True)

# Seção de perguntas sugeridas (atualizada)
st.subheader("🔍 Perguntas Frequentes")
cols = st.columns(2)
for i, pergunta in enumerate(perguntas_sugeridas):
    with cols[i % 2]:
        st.markdown(f"""
        <div class='question-card'>
            <p style='font-weight: 500; margin-bottom: 5px;'>{pergunta}</p>
            <button onclick='window._stcore.setQueryInput("{pergunta}")' 
                    style='background: transparent; 
                           border: 1px solid { "#2563EB" if i%2==0 else "#7C3AED" }; 
                           color: { "#2563EB" if i%2==0 else "#7C3AED" };
                           padding: 5px 10px;
                           border-radius: 6px;
                           cursor: pointer;'>
                Usar esta pergunta
            </button>
        </div>
        """, unsafe_allow_html=True)

# Rodapé personalizado
st.markdown("""
<footer>
    ✈️ Chatbot oficial para consultas ANAC | 
    <span style='color: var(--accent)'>Digite 'sair' a qualquer momento</span>
</footer>
""", unsafe_allow_html=True)
