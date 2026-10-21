# Documentation

| Fichier | Contenu | Format |
|---|---|---|
| `L1_dossier_architecture.pdf` | **Livrable L1** : dossier d'architecture complet (schémas, flux, choix motivés, sécurité / RGPD, annexes) | PDF |
| `diagrammes/01_architecture_logique.pdf` | Architecture logique | PDF |
| `diagrammes/02_architecture_physique.pdf` | Architecture physique (Docker Compose) | PDF |
| `diagrammes/03_flux_de_donnees.pdf` | Flux de données (batch, temps réel, transformation, ML) | PDF |
| `diagrammes/04_schema_etoile.pdf` | Schéma en étoile des ventes (zone Gold) | PDF |
| `adr/` | Décisions d'architecture (une fiche par choix technique) | Markdown, reprises en annexe A du L1 |
| `profilage_donnees.md` | Analyse des données sources et anomalies détectées | Markdown, repris en annexe B du L1 |
| `dictionnaire_donnees.md` | Dictionnaire de données (chaque colonne de chaque source) | Markdown, repris en annexe C du L1 |
| `dossier_architecture.md` | Texte source du L1 | Markdown |
| `diagrammes/sources/` | Sources modifiables des schémas | HTML |

## Mettre à jour le L1

1. Modifier `dossier_architecture.md` (ou un schéma dans `diagrammes/sources/`, une ADR, etc.).
2. Lancer `python scripts/generer_documentation.py` (nécessite Chrome / Chromium et `pip install markdown`).
3. Les PDF des schémas et `L1_dossier_architecture.pdf` sont régénérés.
