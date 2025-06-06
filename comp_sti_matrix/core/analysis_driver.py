"""Script principal du projet de comparaison de matrices STI."""
import os
import sys
import logging
import pandas as pd
from comp_sti_matrix.core.sti_loader import STILoader
from comp_sti_matrix.core.difference_utils import compare_all_matrices, summarize_differences


def consolider_differences(differences_by_sti: dict, loader: STILoader) -> pd.DataFrame | None:
    """Consolide les différences détectées par STI."""
    dfs = []
    for sti, data in differences_by_sti.items():
        df = data["differences"]
        if not df.empty:
            df.insert(0, "STI", sti)
            dfs.append(df)

    if not dfs:
        logging.info("Aucune divergence détectée.")
        return None

    df = pd.concat(dfs, ignore_index=True)

    if df["Reference"].apply(type).eq(list).any():
        df = df.explode("Reference")

    df = df.groupby(["STI"] + [col for col in df.columns if col.startswith("Reference") or col.endswith(")")], as_index=False)\
           .agg({"Reference": set})
    df["Reference"] = df["Reference"].map(tuple)
    df["nb_references"] = df["Reference"].apply(len)
    df.sort_values(by="nb_references", ascending=False, inplace=True)

    return df


def enrichir_différences(df: pd.DataFrame, loader: STILoader) -> pd.DataFrame:
    """Enrichit les différences avec des données issues du PPD."""
    if not os.path.exists(loader.ppd_csv_path):
        logging.warning("Fichier PPD introuvable : %s", loader.ppd_csv_path)
        return df

    df_ref = pd.read_csv(loader.ppd_csv_path, sep="\t", dtype={"N°": str}, encoding="utf-8-sig")
    df_ref["index"] = df_ref["N°"].astype(str) + "_" + df_ref["Référence ALSTOM"].astype(str)
    df_ref.set_index("index", inplace=True)

    def enrich_diff(row):
        enriched = []
        for ref in row["Reference"]:
            ref_str = str(ref)
            if ref_str in df_ref.index:
                title = df_ref.at[ref_str, "Titre"]
                rev = df_ref.at[ref_str, "Révision"]
                enriched.append(f"{ref_str} - {title} (Rev {rev})")
            else:
                enriched.append(ref_str)
        return enriched

    df["Reference enrichie"] = df.apply(enrich_diff, axis=1)
    return df


def main(config_path: str):
    """Point d’entrée principal du script."""
    loader = STILoader(config_path)
    differences = compare_all_matrices(loader)
    df_consolide = consolider_differences(differences, loader)

    if df_consolide is not None:
        df_consolide = enrichir_différences(df_consolide, loader)
        os.makedirs(loader.output_dir, exist_ok=True)
        output_path = os.path.join(loader.output_dir, "analyse_doc_consolidee.xlsx")
        df_consolide.to_excel(output_path, index=False)
        logging.info("Fichier consolidé exporté : %s", output_path)
        logging.info("%d divergences détectées sur %d matrices", len(df_consolide), len(differences))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <config_yaml_path>")
        sys.exit(1)
    main(sys.argv[1])

