"""Script qui exporte le PPD excel vers un tableau importabel dans DOORS."""

import pandas as pd

PATH_TO_PPD_EXCEL = "..."

# 'Nom_DOORS': 'Nom_Excel'
MAPPING_DICT_DOORS_XLS = {
    "Titre": "Titre",
    "Référence ALSTOM": "N°ATSA",
    "Révision": "Indice de révision",
    "Dans PPD Excel": None,
    "Projets": None,
    "Matrices": None,
    "Validé ALSTOM": None,
    "Métier": "Métier",
    "Statut d'échange avec la SNCF": None,
    "Type de document": "Type de document",
    "Référence SNCF": "N°SNCF",
    "Référence FNR": "N°Fournisseur",
    "Nom FNR": "Nom Fournisseur",
    "Numéro de bordereau": "N° Bordereau",
    "Date d'envoi": "Date d'envoi",
    "Date du retour SNCF": "Date du retour SNCF",
    "Statut du retour SNCF": "Statut du retour SNCF",
}
# Étape 1 : Echange
MAPPING_DICT_XLS_DOORS = {
    v: k for k, v in MAPPING_DICT_DOORS_XLS.items() if v is not None
}
colonnes_date = ["Date d'envoi", "Date du retour SNCF"]
ppd_xls = pd.read_excel(PATH_TO_PPD_EXCEL, sheet_name="PPD", header=3, usecols="C:AM")
for col in colonnes_date:
    ppd_xls[col] = ppd_xls[col].dt.strftime("%d/%m/%Y")

# Étape 2 : Vérification des colonnes présentes
colonnes_disponibles = set(MAPPING_DICT_XLS_DOORS.keys())
colonnes_requises = set(ppd_xls.columns)
colonnes_manquantes = colonnes_requises - colonnes_disponibles

# if colonnes_manquantes:
#     print(f" Colonnes manquantes dans DOORS : {colonnes_manquantes}")

# Étape 3 : Sélection et renommage
ppd_doors = ppd_xls[list(colonnes_requises & colonnes_disponibles)].copy()
ppd_doors.rename(columns=MAPPING_DICT_XLS_DOORS, inplace=True)

# Étape 4 : Nettoyage éventuel (trim, NA, etc.)
ppd_doors = ppd_doors.dropna(how="all")  # Suppression des lignes totalement vides
ppd_doors = ppd_doors.fillna("")  # Remplissage vide (optionnel pour DOORS)
# Suppression des lignes où 'Référence ALSTOM' commence par '##'
ppd_doors = ppd_doors[~ppd_doors["Référence ALSTOM"].astype(str).str.startswith("##")]
# Reorganisation des colonnes
ppd_doors = ppd_doors[list(MAPPING_DICT_XLS_DOORS.values())]

# Étape 5 : Export vers CSV compatible DOORS (ex. séparateur tabulation)
ppd_doors.to_csv(
    "data/GE_H2/PPD_export_DOORS.csv", sep="\t", index=False, encoding="utf-8-sig"
)
ppd_doors.to_excel("data/GE_H2/PPD_export_DOORS.xlsx", header=True, index=False)

print("Export terminé avec succès : PPD_export_DOORS.[csv,xlsx]")
