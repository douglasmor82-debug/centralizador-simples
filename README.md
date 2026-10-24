# 🗂️ Centralizador de Projetos (Versão Simples)

![Status](https://img.shields.io/badge/Status-Concluído-green)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Nativo-red)

Vitrine minimalista dos meus projetos, construída de forma leve utilizando os componentes nativos do Streamlit. Sem necessidade de banco de dados, integrações com APIs ou gestão de tokens.

## ✨ Funcionalidades

- **Cards Nativos:** Visual limpo em formato de quadros utilizando `st.container(border=True)`.
- **Informações Diretas:** Exibição focada no que importa: logo/imagem, título, integrantes e links rápidos para o repositório e deploy.
- **Carregamento Instantâneo:** Dados lidos diretamente da memória, sem tempo de espera de requisições web.

## 📁 Estrutura

```text
.
├── app.py             # Aplicação Streamlit contendo também a lista de projetos
├── requirements.txt   # Dependências (apenas streamlit)
└── README.md
```

## 🚀 Executando localmente

```bash
git clone https://github.com/emersonaparecidosilva/centralizador-simples.git
cd centralizador-simples

python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

## ➕ Adicionando novos projetos

Toda a gestão é feita diretamente no código. Para adicionar, remover ou editar um projeto, basta alterar a lista `projetos` dentro do arquivo `app.py`:

```python
{
    "nome": "Novo Projeto",
    "integrantes": ["Emerson Silva"],
    "repo": "https://github.com/emersonaparecidosilva/novo-projeto",
    "link_externo": "https://link-do-deploy.app",
    "imagem": "https://raw.githubusercontent.com/..." # ou caminho local como "assets/logo.png"
}
```

## 🛠️ Tecnologias

[Python](https://www.python.org/) · [Streamlit](https://streamlit.io/)