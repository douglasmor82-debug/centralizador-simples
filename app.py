import streamlit as st

# Configuração da página
st.set_page_config(page_title="Meus Projetos", page_icon="🗂️", layout="wide")
st.title("🗂️ Vaar - Fatec 2026")

# Dados simplificados dos projetos (podem vir de um JSON)
projetos = [
    {
        "nome": "Análise Exploratória de Dados",
        "integrantes": ["Emerson Silva", "Lucas Juan"],
        "repo": "https://github.com/emersonaparecidosilva/projeto-r",
        "link_externo": "https://fatec-cotia-analise.streamlit.app",
        "imagem": "https://raw.githubusercontent.com/emersonaparecidosilva/vaar-nacional-oficial/main/assets/logo.png" # URL ou caminho local
    },
    {
        "nome": "AgentReact",
        "integrantes": ["Emerson Silva"],
        "repo": "https://github.com/emersonaparecidosilva/agentreact",
        "link_externo": "https://agentreact.streamlit.app",
        "imagem": "https://via.placeholder.com/400x200.png?text=Logo+AgentReact"
    },
    {
        "nome": "Utilitários PDF",
        "integrantes": ["Emerson Silva"],
        "repo": "https://github.com/emersonaparecidosilva/ultispdf",
        "link_externo": "",
        "imagem": "https://via.placeholder.com/400x200.png?text=Logo+PDF"
    },
    {
            "nome": "Utilitários PDF2",
            "integrantes": ["Emerson Silva"],
            "repo": "https://github.com/emersonaparecidosilva/ultispdf",
            "link_externo": "",
            "imagem": "https://via.placeholder.com/400x200.png?text=Logo+PDF"
        },
]

# Cria uma grade de 3 colunas para distribuir os quadros
colunas = st.columns(3)

# Renderiza cada projeto dentro de um quadro
for i, proj in enumerate(projetos):
    coluna_atual = colunas[i % 3] # Distribui os quadros uniformemente
    
    with coluna_atual:
        # Cria o quadro com borda
        with st.container(border=True):
            
            # 1. Foto / Logo
            if proj.get("imagem"):
                st.image(proj["imagem"], width='stretch')
                
            # 2. Nome do trabalho
            st.subheader(proj["nome"])
            
            # 3. Integrantes
            st.write(f"**Integrantes:** {', '.join(proj['integrantes'])}")
            
            st.divider() # Uma linha separadora sutil
            
            # 4. Botões de Links
            b1, b2 = st.columns(2)
            if proj.get("repo"):
                b1.link_button("📦 GitHub", proj["repo"], width='stretch')
            if proj.get("link_externo"):
                b2.link_button("🌐 Acessar", proj["link_externo"], width='stretch')