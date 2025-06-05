"""Script principal du projet de comparasion de matrices sti."""
import os
import sys
from builtins import set,tuple
import logging
import pandas as pd
from comp_sti_matrix.core.sti_loader import STILoader
from comp_sti_matrix.core.utils_structural import (
    get_matrix_pairs,
    export_df_excel,
    analyser_couple_matrices,
)
# import pdb


def analyse_sti_matrices(loader):
    """Analyse toutes les paires de matrices définies dans la configuration."""
    res_sti = {}
    for name_x, name_y in get_matrix_pairs(loader):
        sti = name_x[3:]  # Strip prefix (e.g. GE_)
        try:
            res_sti[sti] = analyser_couple_matrices((name_x, name_y))
        except OSError as e:
            logging.warning(
                "Échec d’analyse sur la paire (%s, %s) : %s", name_x, name_y, e
            )
    return res_sti


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


def main(config_path):
    """Fonction principale du script."""
    dataset_path = os.path.dirname(config_path)
    output_file = f"{dataset_path}/output/analyse_doc_consolidee.xlsx"

    # pdb.set_trace()
    loader = STILoader(config_path)
    res_sti = analyse_sti_matrices(loader)
    df_consolidated = consolider_dfs(res_sti)

    if df_consolidated is not None:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        export_df_excel(df_consolidated, output_file)
        logging.info("Fichier consolidé exporté : %s", output_file)
        logging.info(
            "{%s divergences consolidées sur %s matrices comparées.",
            len(df_consolidated),
            len(res_sti),
        )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <config_yaml_path>")
        sys.exit(1)

    main(sys.argv[1])
