import base64
import html
import json
import re
from pathlib import Path

import requests
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Projetos", page_icon="🗂️", layout="wide")

API = "https://api.github.com"
DATA_FILE = Path(__file__).parent / "projects.json"

st.markdown(
    """
<style>
a.card{display:block;text-decoration:none!important;color:inherit!important;
  border:1px solid rgba(128,128,128,.3);border-radius:14px;padding:16px;height:215px;
  overflow:hidden;background:rgba(128,128,128,.06);transition:.15s;margin-bottom:6px}
a.card:hover{transform:translateY(-3px);border-color:#ff4b4b;box-shadow:0 6px 18px rgba(0,0,0,.25)}
a.card h4{margin:0 0 6px 0;font-size:1.1rem}
a.card p{font-size:.88rem;opacity:.8;margin:0 0 10px 0;display:-webkit-box;
  -webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.chip{display:inline-block;font-size:.72rem;padding:2px 9px;margin:0 4px 4px 0;
  border-radius:20px;background:rgba(88,166,255,.18);color:#58a6ff}
.av{width:26px;height:26px;border-radius:50%;margin-right:4px;vertical-align:middle}
.who{display:inline-flex;align-items:center;gap:6px;margin:0 14px 8px 0;font-size:.9rem}
.who img{width:28px;height:28px;border-radius:50%}
</style>
""",
    unsafe_allow_html=True,
)


# ---------- utilidades ----------
def secret(name, default=None):
    try:
        return st.secrets[name]
    except Exception:
        return default


def gh_headers(raw=False):
    h = {
        "Accept": "application/vnd.github.raw+json" if raw else "application/vnd.github+json"
    }
    token = secret("GITHUB_TOKEN")
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def parse_repo(url: str):
    m = re.search(r"github\.com/([\w.-]+)/([\w.-]+)", url.strip())
    if not m:
        return None
    repo = m.group(2)
    if repo.endswith(".git"):
        repo = repo[:-4]
    return m.group(1), repo


def esc(x):
    return html.escape(str(x or ""), quote=True)


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_project(owner: str, repo: str) -> dict:
    r = requests.get(f"{API}/repos/{owner}/{repo}", headers=gh_headers(), timeout=15)
    r.raise_for_status()
    d = r.json()

    contributors = []
    rc = requests.get(
        f"{API}/repos/{owner}/{repo}/contributors",
        headers=gh_headers(),
        params={"per_page": 20},
        timeout=15,
    )
    if rc.status_code == 200:
        for c in rc.json():
            if c.get("type") != "Bot":
                contributors.append(
                    {
                        "login": c["login"],
                        "url": c["html_url"],
                        "avatar": c["avatar_url"],
                        "n": c.get("contributions", 0),
                    }
                )

    homepage = (d.get("homepage") or "").strip()
    if homepage and not homepage.startswith(("http://", "https://")):
        homepage = "https://" + homepage

    return {
        "owner": owner,
        "repo": repo,
        "name": d["name"],
        "description": d.get("description") or "Sem descrição.",
        "homepage": homepage,
        "html_url": d["html_url"],
        "topics": d.get("topics", []),
        "language": d.get("language"),
        "stars": d.get("stargazers_count", 0),
        "branch": d.get("default_branch", "main"),
        "contributors": contributors,
    }


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_readme(owner: str, repo: str, branch: str) -> str:
    r = requests.get(
        f"{API}/repos/{owner}/{repo}/readme", headers=gh_headers(raw=True), timeout=15
    )
    if r.status_code != 200:
        return ""
    md = r.text
    base = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/"

    def fix(url):
        if url.startswith(("http://", "https://", "#", "mailto:", "data:")):
            return url
        return base + re.sub(r"^\./", "", url).lstrip("/")

    md = re.sub(
        r"(!\[[^\]]*\]\()([^)\s]+)", lambda m: m.group(1) + fix(m.group(2)), md
    )
    md = re.sub(
        r'(<img[^>]+src=")([^"]+)', lambda m: m.group(1) + fix(m.group(2)), md
    )
    return md


# ---------- persistência ----------
def load_urls():
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8")).get("projects", [])
        except Exception:
            return []
    return []


def dump_json(urls):
    return json.dumps({"projects": urls}, indent=2, ensure_ascii=False)


def persist(urls):
    """Salva localmente e, se houver token, commita projects.json no GitHub."""
    try:
        DATA_FILE.write_text(dump_json(urls), encoding="utf-8")
    except Exception:
        pass
    token, repo = secret("GITHUB_TOKEN"), secret("CATALOG_REPO")
    if not (token and repo):
        return False
    url = f"{API}/repos/{repo}/contents/projects.json"
    cur = requests.get(url, headers=gh_headers(), timeout=15)
    body = {
        "message": "Atualiza lista de projetos",
        "content": base64.b64encode(dump_json(urls).encode()).decode(),
    }
    if cur.ok:
        body["sha"] = cur.json().get("sha")
    return requests.put(url, headers=gh_headers(), json=body, timeout=15).ok


if "urls" not in st.session_state:
    st.session_state.urls = load_urls()


# ---------- componentes ----------
def target_link(p):
    return p["homepage"] or p["html_url"]


def card_html(p):
    chips = "".join(f'<span class="chip">{esc(t)}</span>' for t in p["topics"][:4])
    avatars = "".join(
        f'<img class="av" src="{esc(c["avatar"])}" title="{esc(c["login"])}">'
        for c in p["contributors"][:6]
    )
    return (
        f'<a class="card" href="{esc(target_link(p))}" target="_blank" rel="noopener">'
        f'<h4>{esc(p["name"])}</h4><p>{esc(p["description"])}</p>'
        f"<div>{chips}</div><div>{avatars}</div></a>"
    )


def contributors_html(p):
    if not p["contributors"]:
        return "<i>Colaboradores indisponíveis.</i>"
    return "".join(
        f'<a class="who" href="{esc(c["url"])}" target="_blank">'
        f'<img src="{esc(c["avatar"])}"> {esc(c["login"])} ({c["n"]})</a>'
        for c in p["contributors"]
    )


@st.dialog("Detalhes do projeto", width="large")
def show_details(p):
    st.subheader(p["name"])
    st.write(p["description"])
    b1, b2, _ = st.columns([1, 1, 3])
    b1.link_button("📦 Repositório", p["html_url"])
    if p["homepage"]:
        b2.link_button("🌐 Website", p["homepage"])
    st.markdown("**Colaboradores**")
    st.markdown(contributors_html(p), unsafe_allow_html=True)
    st.divider()
    readme = fetch_readme(p["owner"], p["repo"], p["branch"])
    if readme:
        st.markdown(readme, unsafe_allow_html=True)
    else:
        st.info("Este repositório não tem README.")


def embed_url(url):
    if "streamlit.app" in url and "embed=true" not in url:
        return url + ("&" if "?" in url else "?") + "embed=true"
    return url


def view_boards(items, ncols):
    for start in range(0, len(items), ncols):
        cols = st.columns(ncols)
        for col, (i, p) in zip(cols, list(enumerate(items))[start : start + ncols]):
            with col:
                st.markdown(card_html(p), unsafe_allow_html=True)
                if st.button("📖 Detalhes", key=f"det_{i}", use_container_width=True):
                    show_details(p)


def view_gallery(items):
    names = [p["name"] for p in items]
    if st.session_state.get("gal_pick") not in names:
        st.session_state.gal_pick = names[0]

    def move(step):
        cur = names.index(st.session_state.gal_pick)
        st.session_state.gal_pick = names[(cur + step) % len(names)]

    c1, c2, c3 = st.columns([1, 6, 1])
    c1.button("◀ Anterior", on_click=move, args=(-1,), use_container_width=True)
    c2.selectbox("Projeto", names, key="gal_pick", label_visibility="collapsed")
    c3.button("Próximo ▶", on_click=move, args=(1,), use_container_width=True)

    idx = names.index(st.session_state.gal_pick)
    p = items[idx]
    st.caption(f"{idx + 1} de {len(items)}")

    left, right = st.columns([2, 3], gap="large")
    with left:
        st.header(p["name"])
        st.write(p["description"])
        st.markdown(
            "".join(f'<span class="chip">{esc(t)}</span>' for t in p["topics"]),
            unsafe_allow_html=True,
        )
        meta = []
        if p["language"]:
            meta.append(f"💻 {p['language']}")
        meta.append(f"⭐ {p['stars']}")
        st.caption(" · ".join(meta))
        st.markdown("**Colaboradores**")
        st.markdown(contributors_html(p), unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        b1.link_button("📦 Repositório", p["html_url"], use_container_width=True)
        if p["homepage"]:
            b2.link_button("🌐 Abrir website", p["homepage"], use_container_width=True)

    with right:
        tab_readme, tab_preview = st.tabs(["📖 README", "🌐 Preview do site"])
        with tab_readme:
            readme = fetch_readme(p["owner"], p["repo"], p["branch"])
            with st.container(height=560):
                if readme:
                    st.markdown(readme, unsafe_allow_html=True)
                else:
                    st.info("Este repositório não tem README.")
        with tab_preview:
            if p["homepage"]:
                if st.toggle("Carregar preview", key=f"prev_{p['name']}"):
                    components.iframe(embed_url(p["homepage"]), height=560, scrolling=True)
                    st.caption("Alguns sites bloqueiam exibição dentro de outra página.")
            else:
                st.info("Este projeto não tem website configurado no GitHub.")


# ---------- barra lateral ----------
with st.sidebar:
    st.title("🗂️ Meus Projetos")
    view = st.radio("Visualização", ["Galeria"], horizontal=True)
    ncols = st.slider("Colunas", 2, 4, 3) if view == "Quadros" else 3
    query = st.text_input("🔍 Buscar", placeholder="nome, tópico ou descrição")

    st.divider()
    st.subheader("➕ Adicionar projeto")
    new_url = st.text_input("URL do GitHub", placeholder="https://github.com/usuario/repo")
    if st.button("Adicionar", use_container_width=True):
        parsed = parse_repo(new_url)
        if not parsed:
            st.error("URL inválida. Use o formato github.com/usuario/repo")
        elif new_url.strip() in st.session_state.urls:
            st.warning("Esse projeto já está na lista.")
        else:
            try:
                fetch_project(*parsed)
                st.session_state.urls.append(new_url.strip())
                saved = persist(st.session_state.urls)
                st.success("Adicionado!" + (" Salvo no GitHub." if saved else ""))
                st.rerun()
            except requests.HTTPError as e:
                st.error(f"Não consegui acessar o repositório ({e.response.status_code}).")

    with st.expander("🛠️ Gerenciar"):
        if st.session_state.urls:
            to_remove = st.selectbox("Remover", st.session_state.urls)
            if st.button("Remover projeto"):
                st.session_state.urls.remove(to_remove)
                persist(st.session_state.urls)
                st.rerun()
        st.download_button(
            "⬇️ Baixar projects.json",
            dump_json(st.session_state.urls),
            file_name="projects.json",
            mime="application/json",
        )
        if st.button("🔄 Atualizar dados do GitHub"):
            st.cache_data.clear()
            st.rerun()

    if not secret("GITHUB_TOKEN"):
        st.caption("Sem GITHUB_TOKEN: limite de 60 consultas/hora na API do GitHub.")


# ---------- corpo ----------
projects, errors = [], []
for u in st.session_state.urls:
    parsed = parse_repo(u)
    if not parsed:
        errors.append(f"{u}: URL inválida")
        continue
    try:
        projects.append(fetch_project(*parsed))
    except requests.HTTPError as e:
        errors.append(f"{u}: erro {e.response.status_code}")
    except requests.RequestException:
        errors.append(f"{u}: falha de conexão")

for err in errors:
    st.warning(err)

if query:
    q = query.lower()
    projects = [
        p
        for p in projects
        if q in p["name"].lower()
        or q in p["description"].lower()
        or any(q in t.lower() for t in p["topics"])
    ]

if not projects:
    st.info("Nenhum projeto para mostrar. Adicione uma URL do GitHub na barra lateral.")
elif view == "Quadros":
    st.title("Meus Projetos")
    view_boards(projects, ncols)
else:
    view_gallery(projects)
