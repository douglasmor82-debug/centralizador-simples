# 🗂️ Centralizador de Projetos

![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-yellow)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Cloud-red)

Vitrine dos meus projetos do GitHub, feita em Streamlit. Basta colar a URL de um repositório e o app busca automaticamente a descrição, os tópicos, o link do website, os colaboradores e o README.

## ✨ Funcionalidades

- **Detalhes:** o botão *Detalhes* abre uma caixa de diálogo com o README renderizado, os links e os colaboradores.
- **Colaboradores:** nomes e avatares vêm direto do GitHub, com o número de commits de cada um.
- **Modo galeria:** navegue projeto a projeto com os botões *Anterior* e *Próximo* ou pela lista de seleção, com README e preview do site em abas.
- **Busca** por nome, tópico ou descrição.
- **Adicionar e remover projetos** pela barra lateral, com opção de salvar a lista no próprio GitHub.
- **Cache de 1 hora** nas consultas à API, com botão para atualizar sob demanda.

## 🧩 Como os dados são obtidos

Tudo vem da API pública do GitHub, a partir da URL do repositório:

| Informação | Origem |
|---|---|
| Descrição, tópicos, linguagem, estrelas | `GET /repos/{owner}/{repo}` |
| Website | campo **Website** nas configurações do repositório |
| README | `GET /repos/{owner}/{repo}/readme` |
| Colaboradores | `GET /repos/{owner}/{repo}/contributors` |

> 💡 Para o card abrir o site do projeto, preencha o campo **Website** em *Edit repository details* no GitHub.

## 📁 Estrutura

```
.
├── app.py             # aplicação Streamlit
├── projects.json      # lista de URLs dos projetos
├── requirements.txt   # dependências
└── README.md
```

## 🚀 Executando localmente

```bash
git clone https://github.com/emersonaparecidosilva/centralizador-projetos.git
cd centralizador-projetos

python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

## ☁️ Publicando no Streamlit Cloud

1. Suba este repositório para o GitHub.
2. Acesse [share.streamlit.io](https://share.streamlit.io) e crie um novo app apontando para `app.py`.
3. (Opcional, mas recomendado) configure os *Secrets* conforme a próxima seção.

## 🔐 Configuração do token (opcional)

Sem token, a API do GitHub permite apenas **60 consultas por hora** e não enxerga repositórios privados. Com ele, o limite aumenta e o app também pode salvar a lista de projetos no repositório.

1. No GitHub, vá em **Settings → Developer settings → Personal access tokens → Fine-grained tokens**.
2. Gere um token com acesso ao repositório do catálogo e as permissões:
   - **Contents:** *Read and write* (somente se quiser que o app grave o `projects.json`)
   - **Metadata:** *Read-only*
3. No Streamlit Cloud, em **Settings → Secrets**, adicione:

```toml
GITHUB_TOKEN = "github_pat_xxxxxxxx"
CATALOG_REPO = "emersonaparecidosilva/centralizador-projetos"
```

Para testar localmente, crie o arquivo `.streamlit/secrets.toml` com o mesmo conteúdo e **não o envie ao Git** (adicione `.streamlit/secrets.toml` ao `.gitignore`).

## ➕ Adicionando projetos

Há duas formas:

- **Pela interface:** na barra lateral, cole a URL em *Adicionar projeto*. Com os secrets configurados, a lista é gravada no `projects.json` do repositório. Esse commit faz o app recarregar.
- **Pelo arquivo:** edite o `projects.json` e faça o commit:

```json
{
  "projects": [
    "https://github.com/emersonaparecidosilva/agentreact",
    "https://github.com/usuario/outro-projeto"
  ]
}
```

> O disco do Streamlit Cloud é efêmero. Sem `CATALOG_REPO` e `GITHUB_TOKEN`, os projetos adicionados pela interface se perdem quando o app reinicia. Use o botão *Baixar projects.json* em *Gerenciar* para não perder a lista.

## ⚠️ Limitações conhecidas

- O preview do site na galeria usa iframe, e alguns sites bloqueiam esse tipo de exibição.
- Imagens do README com caminho relativo são corrigidas, mas alguns recursos mais complexos de Markdown/HTML podem renderizar diferente do GitHub.
- Os dados ficam em cache por 1 hora; use *Atualizar dados do GitHub* para forçar a atualização.

## 🛣️ Ideias para o futuro

- Filtro por tópico e ordenação por estrelas ou data de atualização
- Status do projeto lido a partir dos badges do README
- Captura de tela do website como capa do card

## 🛠️ Tecnologias

[Python](https://www.python.org/) · [Streamlit](https://streamlit.io/) · [Requests](https://requests.readthedocs.io/) · [GitHub REST API](https://docs.github.com/rest)
