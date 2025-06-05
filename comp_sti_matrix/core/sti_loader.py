"""Définit la classe pour les STI."""
import os
import logging
import pandas as pd
import yaml


class STILoader:
    """Repreyésente la classe STI."""
    def __init__(self, config_path: str):
        """Initie la classe."""
        self.config_path = config_path
        self.dataset_root = os.path.dirname(config_path)
        self.excel_dir = os.path.join(self.dataset_root, "excel_files")
        self.output_dir = os.path.join(self.dataset_root, "output")
        os.makedirs(self.output_dir, exist_ok=True)

        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        self.matrices = self.config.get("matrices", [])

    def list_available(self) -> list[str]:
        """Liste les matrices."""
        return [entry["name"] for entry in self.matrices]

    def get_matrix(self, name: str) -> pd.DataFrame:
        """Renvoie le DataFrame corerspondant à la matrice."""
        entry = next((m for m in self.matrices if m["name"] == name), None)
        if not entry:
            raise ValueError(f"Matrice '{name}' non trouvée.")

        file_path = os.path.join(self.excel_dir, entry["file"])

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Fichier Excel non trouvé : {file_path}")

        sti_sheet = entry.get("sti_sheet")
        sheet_cfg = entry["sheets"].get(sti_sheet, {})
        header_row = sheet_cfg.get("header_row", 0)

        logging.info(
            "Chargement de %s | Feuille : %s | En-tête ligne %s",
            file_path, sti_sheet, header_row
        )
        return pd.read_excel(file_path, sheet_name=sti_sheet, header=header_row)

    def get_output_path(self, filename: str) -> str:
        """Renvoie le chemin de sortie complet dans output/."""
        os.makedirs(self.output_dir, exist_ok=True)
        return os.path.join(self.output_dir, filename)

    def get_column_mapping(self, name: str) -> dict:
        """Renvoies le dictionnaire de mapping."""
        for matrix in self.matrices:
            if matrix["name"] == name:
                return matrix.get("column_mapping", {})
        return {}

    def get_fields_to_compare(self):
        """Renvoie le champs à comparer."""
        return self.config.get("fields_to_compare", [])

    def get_matrix_roles(self) -> list:
        """Retourne la liste des rôles disponibles (e.g. GE, H2, etc.)."""
        return list({m["name"].split("_", 1)[0] for m in self.matrices})

    def get_matrix_names(self, role: str) -> list:
        """Retourne les noms des matrices pour un rôle donné (e.g. 'GE')."""
        return [m["name"] for m in self.matrices if m["name"].startswith(role + "_")]
