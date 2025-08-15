import os
import shutil
from pathlib import Path
from flask import Flask, render_template

# Importa o app real com rotas definidas
try:
    from server import app as flask_app
except Exception as import_error:
    raise SystemExit(f"Falha ao importar 'app' de server.py: {import_error}")

ROOT_DIR = Path(__file__).parent.resolve()
TEMPLATES_DIR = ROOT_DIR / "templates"
STATIC_DIR = ROOT_DIR / "static"
SUSPECTS_DIR = ROOT_DIR / "suspeitos"
DIST_DIR = ROOT_DIR / "dist"

# Limite de tamanho para arquivos copiados (MB) para evitar estouro de limites no deploy
DEFAULT_MAX_FILE_MB = 501
MAX_FILE_MB = int(os.getenv("MAX_FILE_MB", str(DEFAULT_MAX_FILE_MB)))
MAX_FILE_BYTES = MAX_FILE_MB * 1024 * 1024

# Garantir que o app do Flask aponte para os diretórios corretos
flask_app.template_folder = str(TEMPLATES_DIR)
flask_app.static_folder = str(STATIC_DIR)


def clean_dist() -> None:
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True, exist_ok=True)


def copy_static() -> None:
    target_static = DIST_DIR / "static"
    shutil.copytree(STATIC_DIR, target_static)


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def render_page(template_name: str, out_path: Path, **context) -> None:
    ensure_dir(out_path.parent)
    # Renderiza no contexto do app real para que url_for funcione
    with flask_app.test_request_context("/"):
        html = render_template(template_name, **context)
    out_path.write_text(html, encoding="utf-8")


def build_pages() -> None:
    # Páginas básicas
    render_page("home.html", DIST_DIR / "index.html")
    render_page("contato.html", DIST_DIR / "contato" / "index.html")
    render_page("casos.html", DIST_DIR / "casos" / "index.html")
    render_page("ocaso.html", DIST_DIR / "casos" / "hack_x" / "index.html")
    # 404 na raiz para Netlify
    render_page("404.html", DIST_DIR / "404.html")

    # Páginas de suspeitos e cópia de arquivos
    if SUSPECTS_DIR.exists():
        for suspect_dir in sorted(SUSPECTS_DIR.iterdir()):
            if not suspect_dir.is_dir():
                continue
            suspect_id = suspect_dir.name
            output_dir = DIST_DIR / "casos" / "hack_x" / suspect_id
            ensure_dir(output_dir)

            files_to_list = []
            for entry in sorted(suspect_dir.iterdir()):
                if not entry.is_file():
                    continue
                size_bytes = entry.stat().st_size
                if size_bytes <= MAX_FILE_BYTES:
                    shutil.copy2(entry, output_dir / entry.name)
                    files_to_list.append(entry.name)
                else:
                    print(f"Ignorando arquivo grande (> {MAX_FILE_MB}MB): {entry}")

            render_page("suspect.html", output_dir / "index.html", id=suspect_id, name="", files=files_to_list)


def main() -> None:
    clean_dist()
    copy_static()
    build_pages()
    print(f"Static site generated at: {DIST_DIR}")


if __name__ == "__main__":
    main()