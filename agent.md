# Agents Documentation – comp_sti_matrix

## 1. Agent Name: STIMatrixComparator

### Description
Agent Python dédié à la comparaison automatisée de matrices de conformité STI (Spécifications Techniques d’Interopérabilité ferroviaires).
Il détecte, structure et documente les divergences pour l’ingénierie certification et le reporting réglementaire.

### Capabilities
- Extraction de matrices (Excel, CSV, YAML)
- Alignement automatique des exigences (mapping d’IDs, gestion d’intitulés divergents)
- Détection d’écarts : exigences manquantes, modifiées, divergentes
- Génération de rapports détaillés (Markdown, Excel, console)
- Paramétrage avancé via fichiers YAML
- Gestion de gros volumes

### Usage Instructions

**Installation** :
pip install -r requirements.txt

**Exécution principale** :
python -m comp_sti_matrix.compare --config config.yaml

**Paramètres clés** :
--config : chemin du fichier de configuration YAML
--report : chemin du rapport de sortie (Markdown ou Excel)
--log-level : niveau de log (DEBUG, INFO, WARNING, ERROR)

**Exemple d’utilisation** :
python -m comp_sti_matrix.compare --config ./config/sti_referentiel.yaml --report ./outputs/rapport_2025_06.md --log-level INFO

**Integration Context**
- Utilisable en ligne de commande, CI/CD, ou comme module Python
- Compatible Python 3.9+
- Accès requis aux fichiers de matrices
- Intégrable dans des workflows de validation documentaire
- Example Use Cases
- Comparer deux matrices STI CCS pour identifier les écarts
- Générer un rapport texte sur les exigences non couvertes
- Détecter les modifications entre deux versions d’une matrice
- Utilisable en amont du comparateur principal
- Appelable en CLI ou comme fonction Python
- Gère tous les formats d’entrée supportés par le projet
- Compatible avec l’automatisation documentaire

Example Use Cases
- Extraire toutes les exigences d’un fichier Excel non formaté vers un YAML normalisé
- Nettoyer et homogénéiser une matrice brute téléchargée depuis un portail externe
- Préparer des fichiers pour analyse massive (batch)

### Maintenance et évolutions
Mettre à jour ce fichier à chaque évolution majeure du code ou ajout de module.
Respecter la structuration par agent pour la traçabilité.
