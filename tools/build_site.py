#!/usr/bin/env python3
"""Construit le site statique du dossier QNX à partir des sources Markdown.

Une seule implémentation : ce script sert en local et dans la CI. La page
« Fonctionnalités » est extraite des tableaux d'exigences des quatre cahiers,
donc elle ne peut pas diverger du texte.

Usage : python3 tools/build_site.py [repertoire_de_sortie]
"""
from __future__ import annotations

import html
import pathlib
import re
import sys

try:
    import markdown
except ImportError:
    sys.exit("python-markdown absent. Installer : pip install markdown")

RACINE = pathlib.Path(__file__).resolve().parent.parent
EXTENSIONS = ["tables", "fenced_code", "toc", "sane_lists"]

NAV = [
    ("index", "Accueil"),
    ("features", "Fonctionnalités"),
    ("tamis", "Tamis"),
    ("glane", "Glane"),
    ("eclat", "Éclat"),
    ("veille", "Veille"),
    ("codelab-veille", "Codelab Veille"),
    ("classement", "Classement"),
    ("inventaire", "Inventaire QNX"),
    ("idees", "100 idées"),
]
PAGES = [
    ("index.md", "index"),
    ("src/TAMIS-cahier-des-charges.md", "tamis"),
    ("src/GLANE-cahier-des-charges.md", "glane"),
    ("src/ECLAT-cahier-des-charges.md", "eclat"),
    ("src/VEILLE-cahier-des-charges.md", "veille"),
    ("src/qnx-classement-final.md", "classement"),
    ("src/qnx-inventaire-officiel.md", "inventaire"),
    ("src/qnx-100-idees-5sem.md", "idees"),
]
PROJETS = [
    ("tamis", "Tamis", "Developer Tooling & Host Tools",
     "Analyse statique et preuve des politiques de sécurité secpol, avant déploiement."),
    ("glane", "Glane", "Low-level Software",
     "Couche capteurs, publication de périphériques, simulateur et banc de latence."),
    ("eclat", "Éclat", "Open-Source Contribution & Ports",
     "Portage de WAMR (WebAssembly) et courtier de capacités à refus par défaut."),
    ("veille", "Veille", "Robotics & Medical",
     "Moniteur patient QNX dont la latence capteur→alarme est bornée et prouvée par "
     "exploration exhaustive des états de défaillance (IEC 62304 / IEC 60601-1-8)."),
]
SRC = {"tamis": "TAMIS-cahier-des-charges.md", "glane": "GLANE-cahier-des-charges.md",
       "eclat": "ECLAT-cahier-des-charges.md", "veille": "VEILLE-cahier-des-charges.md"}
# Pages composées de plusieurs Markdown concaténés (slug → sources, dans l'ordre).
COMPOSITIONS = {"codelab-veille": [
    "src/veille-codelab/README.md",
    "src/veille-codelab/01-pourquoi-une-borne-prouvee.md",
    "src/veille-codelab/02-construire-la-chaine.md",
    "src/veille-codelab/03-prouver-par-exploration.md",
    "src/veille-codelab/04-porter-sur-qnx.md",
]}
# Projets hébergés dans un autre dépôt : bandeau avec lien en tête de leur page.
DEPOTS = {"veille": ("https://github.com/BaptisteFaisy/veille",
                     "https://baptistefaisy.github.io/veille/")}
RE_EX = re.compile(r"^\|\s*([A-Z]{3}-\d{2})\s*\|\s*([SCX])\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|$")
# Format 3 colonnes du cahier Veille : | S1 | exigence | S | (texte sans « | »).
RE_EX3 = re.compile(r"^\|\s*([SCX]\d+)\s*\|\s*([^|]+?)\s*\|\s*([SCX])\s*\|$")
RE_ESSAI = re.compile(r"^\|\s*(E\d)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|$")
# Essais à 3 colonnes du cahier Veille : | E1 | question | bloquant |.
RE_ESSAI3 = re.compile(r"^\|\s*(E\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|$")
RE_LOT = re.compile(r"^\|\s*(L\d+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|$")
CSS = pathlib.Path(__file__).with_name("style.css").read_text(encoding="utf-8")


def gabarit(titre: str, corps: str, actif: str) -> str:
    liens = []
    for slug, libelle in NAV:
        classe = ' class="actif"' if slug == actif else ''
        liens.append('<a href="%s.html"%s>%s</a>' % (slug, classe, libelle))
    return ("<!DOCTYPE html>\n<html lang=\"fr\">\n<head>\n<meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\n"
            f"<title>{titre} — Dossier QNX</title>\n<style>{CSS}</style>\n</head>\n<body>\n"
            "<header>\n<h1>Dossier QNX — Global Hackathon 2026</h1>\n"
            "<p>Inventaire documenté des manques de QNX SDP 8.0, classement de 140 idées, "
            "quatre cahiers des charges.</p>\n</header>\n<nav>\n" + "\n".join(liens) +
            f"\n</nav>\n<main>\n{corps}\n</main>\n"
            "<footer>Généré depuis les sources Markdown du dépôt. Licence MIT.</footer>\n"
            "</body>\n</html>\n")


def convertir(src: pathlib.Path) -> str:
    return markdown.markdown(src.read_text(encoding="utf-8"), extensions=EXTENSIONS,
                             output_format="html5")


def bandeau(slug: str) -> str:
    """Liens en tête de page vers le dépôt (et le site) propres d'un projet."""
    entree = DEPOTS.get(slug)
    if not entree:
        return ""
    depot, site = entree
    texte = f'<a href="{depot}">{depot}</a>'
    if site:
        texte += (f', et tout le projet se visite en ligne (chiffres calculés, '
                  f'preuves réelles) : <a href="{site}">{site}</a>')
    return ('<p class="bandeau">Ce projet vit dans son propre dépôt — code, tests '
            f'et preuve d\'exploration : {texte}.</p>')


def premier_titre(chemin: pathlib.Path) -> str:
    for ligne in chemin.read_text(encoding="utf-8").splitlines():
        if ligne.startswith("# "):
            return ligne[2:].strip()
    return chemin.stem


def page_composee(sources: list[str]) -> str:
    """Sommaire local + chapitres Markdown concaténés, séparés par <hr>."""
    liens, chapitres = [], []
    for i, rel in enumerate(sources):
        src = RACINE / rel
        titre = premier_titre(src)
        liens.append(f'<li><a href="#partie-{i + 1}">{html.escape(titre)}</a></li>')
        chapitres.append(f'<section id="partie-{i + 1}">{convertir(src)}</section>')
    sommaire = ('<nav class="sommaire"><h2>Sommaire</h2><ol>'
                + "".join(liens) + "</ol></nav>")
    return sommaire + "\n<hr>\n".join(chapitres)


def extraire(chemin: pathlib.Path) -> dict:
    """Lit un cahier et en tire exigences, essais de faisabilité et lots.

    Deux formats de tableaux sont reconnus : 4 colonnes (Tamis/Glane/Éclat,
    avec vérification) et 3 colonnes (Veille, niveau en dernière colonne).
    Les exigences sont normalisées en (ident, niveau, texte, vérification).
    """
    ex, essais, lots = [], [], []
    for ligne in chemin.read_text(encoding="utf-8").splitlines():
        m = RE_EX.match(ligne)
        if m:
            ex.append(m.groups())
            continue
        m = RE_EX3.match(ligne)
        if m:
            ident, texte, niv = m.groups()
            ex.append((ident, niv, texte, ""))
            continue
        m = RE_ESSAI.match(ligne) or RE_ESSAI3.match(ligne)
        if m:
            essais.append(m.groups())
            continue
        m = RE_LOT.match(ligne)
        if m:
            lots.append(m.groups())
    return {"exigences": ex, "essais": essais, "lots": lots}


def carte_exigence(projet: str, ident: str, niv: str, texte: str, verif: str) -> str:
    e = html.escape
    pied = f'<footer><em>Vérification :</em> {e(verif)}</footer>' if verif else ""
    return (f'<article class="ex" data-projet="{projet}" data-niveau="{niv}">'
            f'<header><b>{e(ident)}</b><span class="niv niv-{niv}">{niv}</span>'
            f'<span class="proj">{e(projet)}</span></header>'
            f'<p>{e(texte)}</p>{pied}</article>')


def bloc_projet(slug: str, nom: str, cat: str, desc: str, d: dict) -> str:
    e = html.escape
    comp = {n: sum(1 for x in d["exigences"] if x[1] == n) for n in "SCX"}
    return (f'<section class="projet" id="{slug}"><h2>{e(nom)} '
            f'<small>{e(cat)}</small></h2><p class="desc">{e(desc)}</p>'
            f'<p class="chiffres">{len(d["exigences"])} exigences '
            f'(<b>S</b> {comp["S"]} · <b>C</b> {comp["C"]} · <b>X</b> {comp["X"]}) · '
            f'{len(d["essais"])} essais de faisabilité · {len(d["lots"])} lots délégables</p>'
            + "".join(carte_exigence(nom.lower(), *x) for x in d["exigences"])
            + "</section>")


def filtres() -> str:
    boutons = ['<button class="f actif" data-f="tous">Tout</button>']
    for slug, nom, _c, _d in PROJETS:
        boutons.append(f'<button class="f" data-f="{slug}">{nom}</button>')
    for niv, lib in (("S", "S — socle"), ("C", "C — complet"), ("X", "X — extrême")):
        boutons.append(f'<button class="f niv-{niv}" data-n="{niv}">{lib}</button>')
    return '<div class="filtres">' + "".join(boutons) + '<span id="compte"></span></div>'


def script_filtres() -> str:
    return """<script>
(function(){
  var projet='tous', niveau=null;
  var cartes=[].slice.call(document.querySelectorAll('.ex'));
  var compte=document.getElementById('compte');
  function appliquer(){
    var n=0;
    cartes.forEach(function(c){
      var okP=(projet==='tous')||c.dataset.projet===projet;
      var okN=(niveau===null)||c.dataset.niveau===niveau;
      var vis=okP&&okN; c.style.display=vis?'':'none'; if(vis)n++;
    });
    compte.textContent=n+' fonctionnalité(s) affichée(s)';
    document.querySelectorAll('.projet').forEach(function(s){
      var v=s.querySelectorAll('.ex').length? [].some.call(s.querySelectorAll('.ex'),
        function(c){return c.style.display!=='none';}) : false;
      s.style.display=v?'':'none';
    });
  }
  document.querySelectorAll('.f').forEach(function(b){
    b.addEventListener('click',function(){
      if(b.dataset.f){ projet=b.dataset.f; niveau=null; }
      else { niveau=(niveau===b.dataset.n)?null:b.dataset.n; projet='tous'; }
      document.querySelectorAll('.f').forEach(function(x){x.classList.remove('actif');});
      b.classList.add('actif'); appliquer();
    });
  });
  appliquer();
})();
</script>"""


def page_features() -> str:
    blocs, total = [], 0
    for slug, nom, cat, desc in PROJETS:
        d = extraire(RACINE / "src" / SRC[slug])
        total += len(d["exigences"])
        blocs.append(bloc_projet(slug, nom, cat, desc, d))
    entete = ("<h1>Fonctionnalités des quatre projets</h1>"
              "<p>Page générée automatiquement depuis les tableaux d'exigences des cahiers "
              "des charges : elle ne peut pas diverger du texte source. Les niveaux "
              "<b>S</b> (socle, indispensable à une soumission), <b>C</b> (complet, la "
              "version visée) et <b>X</b> (extrême) viennent des cahiers.</p>"
              f"<p class=\"chiffres\"><b>{total}</b> fonctionnalités au total.</p>")
    return entete + filtres() + "".join(blocs) + script_filtres()


def ecrire(sortie: pathlib.Path, slug: str, corps: str) -> None:
    (sortie / f"{slug}.html").write_text(
        gabarit(dict(NAV)[slug], corps, slug), encoding="utf-8")
    print(f"  {slug}.html")


def construire(sortie: pathlib.Path) -> int:
    if sortie.exists():
        for ancien in sortie.glob("*.html"):
            ancien.unlink()
    sortie.mkdir(parents=True, exist_ok=True)
    (sortie / "styles.css").write_text(CSS, encoding="utf-8")
    for rel, slug in PAGES:
        src = RACINE / rel
        if not src.exists():
            print(f"source absente : {rel}", file=sys.stderr)
            return 1
        ecrire(sortie, slug, bandeau(slug) + convertir(src))
    for slug, sources in COMPOSITIONS.items():
        absentes = [s for s in sources if not (RACINE / s).exists()]
        if absentes:
            print(f"sources absentes : {absentes}", file=sys.stderr)
            return 1
        ecrire(sortie, slug, page_composee(sources))
    (sortie / "features.html").write_text(
        gabarit("Fonctionnalités", page_features(), "features"), encoding="utf-8")
    print("  features.html")
    return 0


if __name__ == "__main__":
    cible = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else RACINE / "site"
    sys.exit(construire(cible))
