"""Génère la documentation PDF du projet à partir des sources versionnées.

Produit :
  - docs/diagrammes/*.pdf          : un PDF par schéma (A4 paysage, vectoriel)
  - docs/L1_dossier_architecture.pdf : livrable L1 (dossier + schémas + annexes)

Sources :
  - docs/dossier_architecture.md     : texte du dossier (marqueurs @@SCHEMA:<nom>@@)
  - docs/diagrammes/sources/*.html   : schémas (HTML/CSS/SVG)
  - docs/adr/*.md, docs/profilage_donnees.md, docs/dictionnaire_donnees.md : annexes

Usage :
  python scripts/generer_documentation.py
  Variable d'environnement CHROME : chemin vers Chrome / Chromium (défaut : "chromium").
  Dépendance Python : markdown (pip install markdown).
"""
import os
import re
import subprocess
import tempfile
from pathlib import Path

import markdown

RACINE = Path(__file__).resolve().parent.parent
DOCS = RACINE / "docs"
SCHEMAS_SRC = DOCS / "diagrammes" / "sources"
SCHEMAS_PDF = DOCS / "diagrammes"
SORTIE_L1 = DOCS / "L1_dossier_architecture.pdf"
CHROME = os.environ.get("CHROME", "chromium")

TITRES_SCHEMAS = {
    "01_architecture_logique": "Architecture logique",
    "02_architecture_physique": "Architecture physique (Docker Compose)",
    "03_flux_de_donnees": "Flux de données",
    "04_schema_etoile": "Schéma en étoile des ventes (zone Gold)",
}

CSS = """
@page { size: A4; margin: 18mm 16mm; }
@page paysage { size: A4 landscape; margin: 10mm; }
body { font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 10pt; color: #1d2433; line-height: 1.45; }
h1 { font-size: 20pt; color: #0f3d68; border-bottom: 2px solid #0f3d68; padding-bottom: 4px; break-before: page; }
h2 { font-size: 14pt; color: #0f3d68; margin-top: 22px; border-bottom: 1px solid #c9d6e3; padding-bottom: 3px; }
h3 { font-size: 11.5pt; color: #24507a; margin-top: 16px; }
table { border-collapse: collapse; width: 100%; margin: 8px 0 12px; font-size: 8.4pt; }
tr { break-inside: avoid; }
th { background: #0f3d68; color: #fff; text-align: left; padding: 4px 6px; }
td { border-bottom: 1px solid #dde4ec; padding: 3px 6px; vertical-align: top; }
tr:nth-child(even) td { background: #f5f8fb; }
code { font-family: 'DejaVu Sans Mono', Consolas, monospace; font-size: 8.2pt; background: #eef2f6; padding: 0 3px; border-radius: 3px; }
pre { background: #f3f6f9; border-left: 3px solid #0f3d68; padding: 8px 10px; font-size: 8.2pt; white-space: pre-wrap; break-inside: avoid; }
pre code { background: none; padding: 0; }
blockquote { border-left: 3px solid #e0a020; background: #fff8e8; margin: 8px 0; padding: 6px 10px; }
hr { display: none; }
.page-schema { page: paysage; break-before: page; break-after: page; }
.page-schema .legende-figure { font-size: 11pt; font-weight: 700; color: #0f3d68; border-bottom: 2px solid #0f3d68; padding-bottom: 4px; margin-bottom: 12px; }
.page-schema .zoom { zoom: .76; }
.page-schema h1, .page-schema h2 { break-before: avoid; font-size: 16pt; margin: 0 0 6px; }
.page-schema > p { margin: 0 0 6px; }
.garde { height: 250mm; display: flex; flex-direction: column; justify-content: center; text-align: center; }
.garde h1 { border: none; break-before: avoid; font-size: 26pt; }
.garde .sous-titre { font-size: 14pt; color: #24507a; margin: 6px 0 40px; }
.garde .infos { font-size: 11pt; color: #444; line-height: 1.8; }
.garde .logo { border: 1px dashed #999; color: #999; padding: 18px; width: 60mm; margin: 0 auto 40px; }
.sommaire h1 { break-before: page; }
.sommaire ol { font-size: 11pt; line-height: 1.9; }
"""


def imprimer_pdf(source_html: Path, sortie_pdf: Path) -> None:
    """Imprime un fichier HTML en PDF avec Chrome en mode sans interface."""
    subprocess.run(
        [CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
         f"--print-to-pdf={sortie_pdf.resolve()}", source_html.resolve().as_uri()],
        check=True, capture_output=True,
    )


def generer_schemas() -> None:
    for nom in TITRES_SCHEMAS:
        imprimer_pdf(SCHEMAS_SRC / f"{nom}.html", SCHEMAS_PDF / f"{nom}.pdf")
        print(f"Schéma généré : docs/diagrammes/{nom}.pdf")


def extraire_schema(nom: str) -> tuple[str, str]:
    """Renvoie (styles, contenu) d'un schéma, délimités dans le fichier source."""
    html = (SCHEMAS_SRC / f"{nom}.html").read_text(encoding="utf-8")
    style = re.search(r'<style id="schema-style">(.*?)</style>', html, re.S).group(1)
    corps = re.search(r"<!-- debut-schema -->(.*?)<!-- fin-schema -->", html, re.S).group(1)
    return style, corps


def retirer_liens_md(texte: str) -> str:
    """Les liens vers d'autres fichiers .md n'ont pas de sens dans le PDF : on garde le texte."""
    return re.sub(r"\[([^\]]+)\]\((?!http)[^)]+\.md\)", r"\1", texte)


def md_vers_html(texte: str) -> str:
    return markdown.markdown(texte, extensions=["tables", "fenced_code", "sane_lists"])


def annexe(fichier: Path, niveau_titre: str = "##") -> str:
    """Convertit un document en annexe : son titre principal devient un titre de niveau 2."""
    texte = retirer_liens_md(fichier.read_text(encoding="utf-8"))
    texte = re.sub(r"^## ", "### ", texte, flags=re.M)
    texte = re.sub(r"^# ", f"{niveau_titre} ", texte, count=1, flags=re.M)
    return md_vers_html(texte)


def construire_l1() -> str:
    dossier = retirer_liens_md((DOCS / "dossier_architecture.md").read_text(encoding="utf-8"))
    dossier = re.sub(r"^# .*\n", "", dossier, count=1)            # titre porté par la page de garde
    dossier = re.sub(r"^\*Schéma : .*\*$\n", "", dossier, flags=re.M)  # le chemin figure dans la légende
    dossier = re.sub(r"^## ", "# ", dossier, flags=re.M)          # sections = chapitres
    dossier = re.sub(r"^### ", "## ", dossier, flags=re.M)
    chapitres = re.findall(r"^# (.+)$", dossier, flags=re.M)

    corps = md_vers_html(dossier)
    styles = []
    for i, (nom, titre) in enumerate(TITRES_SCHEMAS.items(), 1):
        style, contenu = extraire_schema(nom)
        styles.append(style)
        page = (f'<div class="page-schema"><div class="legende-figure">Figure {i} — {titre}'
                f'<span style="float:right;font-weight:400;font-size:9pt">docs/diagrammes/{nom}.pdf</span></div>'
                f'<div class="zoom">{contenu}</div></div>')
        corps = corps.replace(f"<p>@@SCHEMA:{nom}@@</p>", page)
    # Un chapitre qui commence par un schéma partage sa page paysage avec lui
    corps = re.sub(r'(<h[12]>[^<]*</h[12]>)\s*((?:<p>(?:(?!</p>).)*</p>\s*)?)<div class="page-schema">',
                   r'<div class="page-schema">\1\2', corps, flags=re.S)
    restants = re.findall(r"@@SCHEMA:[^@]+@@", corps)
    if restants:
        raise ValueError(f"Schémas introuvables : {restants}")

    annexes = [
        ("Annexe A — Décisions d'architecture (ADR)",
         "".join(annexe(f) for f in sorted((DOCS / "adr").glob("*.md")))),
        ("Annexe B — Profilage des données", annexe(DOCS / "profilage_donnees.md", "##")),
        ("Annexe C — Dictionnaire de données des sources", annexe(DOCS / "dictionnaire_donnees.md", "##")),
    ]

    sommaire = "".join(f"<li>{c}</li>" for c in chapitres)
    sommaire += "".join(f"<li>{titre}</li>" for titre, _ in annexes)
    figures = "".join(f"<li>Figure {i} — {t}</li>" for i, t in enumerate(TITRES_SCHEMAS.values(), 1))

    garde = """
    <div class="garde">
      <div class="logo">[Logo établissement]</div>
      <h1>Dossier d'architecture</h1>
      <div class="sous-titre">Plateforme Data Omnicanale « NeoRetail »</div>
      <div class="infos">
        Mise en situation professionnelle — M2 Data Engineer<br>
        Livrable L1 — version du jalon S0<br>
        Équipe : [noms des membres]<br>
        Dépôt Git : [lien]<br>
        Octobre 2026
      </div>
    </div>"""
    html = garde
    html += f'<div class="sommaire"><h1>Sommaire</h1><ol>{sommaire}</ol>'
    html += f'<h2>Liste des figures</h2><ul>{figures}</ul></div>'
    html += corps
    for titre, contenu in annexes:
        html += f"<h1>{titre}</h1>{contenu}"

    return (f'<!doctype html><html lang="fr"><head><meta charset="utf-8">'
            f"<title>Dossier d'architecture NeoRetail</title>"
            f"<style>{CSS}{''.join(styles)}</style></head><body>{html}</body></html>")


def generer_l1() -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".html", dir=DOCS, delete=False,
                                     encoding="utf-8") as f:
        f.write(construire_l1())
        temporaire = Path(f.name)
    try:
        imprimer_pdf(temporaire, SORTIE_L1)
    finally:
        temporaire.unlink()
    print(f"Livrable généré : docs/{SORTIE_L1.name}")


if __name__ == "__main__":
    generer_schemas()
    generer_l1()
