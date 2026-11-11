#!/usr/bin/env python3
"""Construit le site statique du dossier QNX à partir des sources Markdown.

Une seule implémentation : ce script sert en local et dans la CI.
Usage : python3 tools/build_site.py [repertoire_de_sortie]
"""
from __future__ import annotations

import pathlib
import sys

try:
    import markdown
except ImportError:
    sys.exit("python-markdown absent. Installer : pip install markdown")

RACINE = pathlib.Path(__file__).resolve().parent.parent
EXTENSIONS = ["tables", "fenced_code", "toc", "sane_lists"]
PAGES = [
    ("index.md", "index", "Accueil"),
    ("src/TAMIS-cahier-des-charges.md", "tamis", "Tamis — politiques de sécurité"),
    ("src/GLANE-cahier-des-charges.md", "glane", "Glane — capteurs et publication"),
    ("src/ECLAT-cahier-des-charges.md", "eclat", "Éclat — WebAssembly (WAMR)"),
    ("src/qnx-classement-final.md", "classement", "Classement des 140 idées"),
    ("src/qnx-inventaire-officiel.md", "inventaire", "Inventaire : ce que QNX fournit déjà"),
    ("src/qnx-100-idees-5sem.md", "idees", "100 idées détaillées"),
]
CSS = """
:root{--fg:#e6e6e6;--bg:#12141a;--card:#1b1f28;--acc:#7fd1c1;--mut:#9aa3b2;--bd:#2a3040}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
 font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
header{padding:1.4rem 1.2rem;border-bottom:1px solid var(--bd);background:var(--card)}
header h1{margin:0;font-size:1.25rem}
header p{margin:.3rem 0 0;color:var(--mut);font-size:.9rem}
nav{display:flex;flex-wrap:wrap;gap:.4rem;padding:.8rem 1.2rem;border-bottom:1px solid var(--bd)}
nav a{color:var(--mut);text-decoration:none;font-size:.85rem;padding:.3rem .6rem;
 border:1px solid var(--bd);border-radius:999px}
nav a:hover{color:var(--fg)}
nav a.actif{color:#12141a;background:var(--acc);border-color:var(--acc);font-weight:600}
main{padding:1.2rem;max-width:60rem;margin:0 auto}
main h1{font-size:1.6rem;border-bottom:1px solid var(--bd);padding-bottom:.4rem}
main h2{font-size:1.25rem;margin-top:2rem;color:var(--acc)}
main h3{font-size:1.05rem;margin-top:1.6rem}
a{color:var(--acc)}
code{background:#0d0f14;padding:.1rem .35rem;border-radius:4px;font-size:.88em}
pre{background:#0d0f14;padding:.9rem;border-radius:8px;overflow-x:auto;border:1px solid var(--bd)}
pre code{background:none;padding:0}
table{border-collapse:collapse;width:100%;margin:1rem 0;font-size:.9rem;display:block;overflow-x:auto}
th,td{border:1px solid var(--bd);padding:.45rem .6rem;text-align:left;vertical-align:top}
th{background:var(--card);white-space:nowrap}
blockquote{border-left:3px solid var(--acc);margin:1rem 0;padding:.2rem 1rem;color:var(--mut)}
footer{padding:1.2rem;color:var(--mut);font-size:.85rem;border-top:1px solid var(--bd);text-align:center}
"""


def gabarit(titre: str, corps: str, actif: str) -> str:
    liens = []
    for _src, slug, label in PAGES:
        cls = ' class="actif"' if slug == actif else ""
        liens.append(f'<a href="{slug}.html"{cls}>{label}</a>')
    nav = "\n".join(liens)
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{titre} — Dossier QNX</title>
<style>{CSS}</style>
</head>
<body>
<header>
<h1>Dossier QNX — Global Hackathon 2026</h1>
<p>Inventaire documenté des manques de QNX SDP 8.0, classement de 140 idées, trois cahiers des charges.</p>
</header>
<nav>
{nav}
</nav>
<main>
{corps}
</main>
<footer>Généré depuis les sources Markdown du dépôt. Licence MIT.</footer>
</body>
</html>
"""


def convertir(src: pathlib.Path) -> str:
    texte = src.read_text(encoding="utf-8")
    return markdown.markdown(texte, extensions=EXTENSIONS, output_format="html5")


def construire(sortie: pathlib.Path) -> int:
    if sortie.exists():
        for ancien in sortie.glob("*.html"):
            ancien.unlink()
    sortie.mkdir(parents=True, exist_ok=True)
    (sortie / "styles.css").write_text(CSS, encoding="utf-8")
    for rel, slug, label in PAGES:
        src = RACINE / rel
        if not src.exists():
            print(f"source absente : {rel}", file=sys.stderr)
            return 1
        html = gabarit(label, convertir(src), slug)
        (sortie / f"{slug}.html").write_text(html, encoding="utf-8")
        print(f"  {slug}.html  ({len(html)} octets)")
    return 0


if __name__ == "__main__":
    cible = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else RACINE / "site"
    sys.exit(construire(cible))
