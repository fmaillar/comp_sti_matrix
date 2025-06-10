"""Script principal du projet de comparasion de matrices STI."""

import os
import sys
import logging
from builtins import set, tuple

import pandas as pd

from comp_sti_matrix.core.sti_loader import STILoader
from comp_sti_matrix.core.utils_structural import (
    get_matrix_pairs,
    export_df_excel,
    analyser_couple_matrices,
    enrichir_colonne_difference,
)


class STIAnalyzer:
    """Encapsule le processus d'analyse sous forme orientée objet."""

    def __init__(self, config_path: str) -> None:
        self.config_path = config_path
        self.dataset_path = os.path.dirname(config_path)
        self.output_file = os.path.join(
            self.dataset_path, "output", "analyse_doc_consolidee.xlsx"
        )
        self.labels = os.path.basename(self.dataset_path).split("_")
        self.loader = STILoader(config_path)

    def analyse_sti_matrices(self):
        """Analyse toutes les paires de matrices définies dans la configuration."""
        res_sti = {}
        set1 = set()
        set2 = set()
        for name_x, name_y in get_matrix_pairs(self.loader):
            sti = name_x[3:]  # Strip prefix (e.g. GE_)
            try:
                res, set1_temp, set2_temp = analyser_couple_matrices((name_x, name_y))
                res_sti[sti] = res
                set1 |= set1_temp
                set2 |= set2_temp
            except OSError as e:
                logging.warning(
                    "Échec d’analyse sur la paire (%s, %s) : %s", name_x, name_y, e
                )
        return res_sti, set1, set2

    @staticmethod
    def consolider_dfs(res_sti):
        """Concatène et structure les DataFrames valides."""
        dfs_valides = [
            df.assign(STI=sti)[["STI"] + [col for col in df.columns if col != "STI"]]
            for sti, df in res_sti.items()
            if not df.empty
        ]

        if not dfs_valides:
            logging.info("Aucune divergence documentaire détectée.")
            return None

        df = pd.concat(dfs_valides, ignore_index=True)

        if df["Reference"].apply(type).eq(list).any():
            df = df.explode("Reference")

        df = df.groupby(["STI", "Champ", "État", "Différence"], as_index=False).agg(
            {"Reference": set}
        )

        df["Reference"] = df["Reference"].map(tuple)
        df["nb_references"] = df["Reference"].apply(len)
        df.sort_values(by=["nb_references"], ascending=False, inplace=True)

        return df

    def run(self):
        """Lance l'analyse complète."""
        res_sti, set1, set2 = self.analyse_sti_matrices()
        df_consolidated = self.consolider_dfs(res_sti)
        doc_reference_path = os.path.join(self.dataset_path, "PPD_export_DOORS.csv")
        if df_consolidated is not None and os.path.exists(doc_reference_path):
            df_ref = pd.read_csv(
                doc_reference_path, sep="\t", dtype={"N°": str}, encoding="utf-8-sig"
            )
            df_ref["index"] = df_ref["N°"].astype(str) + "_" + df_ref["Référence ALSTOM"].astype(str)
            df_ref.set_index("index", inplace=True)
            df_consolidated = enrichir_colonne_difference(df_consolidated, df_ref, self.labels)
            logging.info("Colonne 'Différence' enrichie avec les titres et révisions.")
        elif df_consolidated is not None:
            logging.warning(
                "Fichier de référence documentaire introuvable : %s", doc_reference_path
            )

        if df_consolidated is not None:
            os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
            export_df_excel(df_consolidated, self.output_file)
            logging.info("Fichier consolidé exporté : %s", self.output_file)
            logging.info(
                "{%s divergences consolidées sur %s matrices comparées.",
                len(df_consolidated),
                len(res_sti),
            )

        logging.info("\n liste 1 de documents : {%s}", set1)
        logging.info("\n liste 2 de documents : {%s}", set2)


def main(config_path):
    """Fonction principale pour compatibilité CLI."""
    STIAnalyzer(config_path).run()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <config_yaml_path>")
        sys.exit(1)

    main(sys.argv[1])
