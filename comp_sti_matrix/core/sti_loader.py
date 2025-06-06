import os
import pandas as pd
import yaml
from typing import Any


class STILoader:
    """Classe de chargement des configurations STI à partir d'un fichier YAML."""

    def __init__(self, config_path: str):
        """Initialise le chargeur en important toutes les données de configuration."""
        self.config_path = config_path
        self.dataset_root = os.path.dirname(config_path)

        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config: dict[str, Any] = yaml.safe_load(f)

        # Chargement des attributs globaux
        self.project = self.config.get("project")
        self.version = self.config.get("version")
        self.date_modification = self.config.get("date_modification")
        self.auteur = self.config.get("auteur")
        self.id_column = self.config.get("id_column", "Reference")
        self.fields_to_compare = self.config.get("fields_to_compare", [])
        self.matrix_prefixes = self.config.get("matrix_prefixes", [])
        self.project_name = self.config.get("project_name")

        # Construction
        self.project_labels = self.config.get("project_name", "").split("_")
        

        # Chemins de base
        self.root_dir = os.path.abspath(
            self.config.get("root_dir", os.path.dirname(config_path))
        )
        self.ppd_csv_path = os.path.join(self.root_dir, self.config.get("ppd_csv_path"))
        self.excel_dir = os.path.join(self.root_dir, self.config.get("excel_dir", ""))
        self.output_dir = os.path.join(self.root_dir, self.config.get("output_dir", ""))

        os.makedirs(self.output_dir, exist_ok=True)

        # Données projets structurées
        self.projects = self._load_projects()

        self.validate_config()

    def _load_projects(self) -> dict[str, dict[str, dict[str, Any]]]:
        """Retourne un dictionnaire structuré des projets et matrices associées."""
        result = {}
        raw_projects = self.config.get("projects", {})
        for prefix in self.matrix_prefixes:
            proj_data = raw_projects.get(prefix, {})
            result[prefix] = proj_data
        return result

    def get_matrix_config(self, prefix: str, sti: str) -> dict[str, Any]:
        """Retourne la configuration d'une matrice STI spécifique pour un projet donné."""
        return self.projects.get(prefix, {}).get(sti, {})

    def list_sti_names(self) -> list[str]:
        """Retourne la liste des noms STI communs aux projets définis dans matrix_prefixes."""
        if len(self.matrix_prefixes) < 2:
            return list(self.projects.get(self.matrix_prefixes[0], {}).keys())

        common = set(self.projects.get(self.matrix_prefixes[0], {}).keys())
        for prefix in self.matrix_prefixes[1:]:
            common &= set(self.projects.get(prefix, {}).keys())
        return list(common)

    def get_excel_path(self, file_name: str) -> str:
        return os.path.join(self.excel_dir, file_name)

    def get_output_path(self, file_name: str) -> str:
        return os.path.join(self.output_dir, file_name)

    def relpath_from_root(self, file_path: str) -> str:
        """Renvoie un chemin relatif au dossier racine projet."""
        return os.path.relpath(file_path, self.root_dir)

    def validate_config(self):
        required_keys = ["id_column", "fields_to_compare", "matrix_prefixes"]
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Clé obligatoire manquante dans le fichier de config : {key}")

    def load_matrix(self, project_name: str, sti_name: str) -> pd.DataFrame:
        matrix_info = self.projects[project_name][sti_name]
        filename = matrix_info["file"]
        sheet_name = matrix_info["sti_sheet"]
        header_row = matrix_info["sheets"][sheet_name]["header_row"]
        file_path = os.path.join(self.excel_dir, project_name, filename)
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Fichier non trouvé : {file_path}")

        df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)
        column_mapping = matrix_info["column_mapping"]
        df.rename(columns=column_mapping, inplace=True) 

        return df
   
