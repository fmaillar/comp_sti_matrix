import pandas as pd
from collections import defaultdict
from typing import Tuple, Dict
from comp_sti_matrix.core.sti_loader import STILoader


def compare_matrix_entries(loader: STILoader, matrix_name: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Compare les entrées (IDs) entre deux projets pour une matrice donnée.

    :param loader: STILoader contenant config et données
    :param matrix_name: Nom de la matrice (LocPas, PMR, etc.)
    :return: (df_common, df_unique_A, df_unique_B)
    """
    project_A, project_B = loader.project_labels
    df_A = loader.load_matrix(project_A, matrix_name)
    df_B = loader.load_matrix(project_B, matrix_name)

    id_col = loader.id_column
    set_A = set(df_A[id_col].dropna().astype(str))
    set_B = set(df_B[id_col].dropna().astype(str))

    common_ids = sorted(set_A & set_B)
    unique_A = sorted(set_A - set_B)
    unique_B = sorted(set_B - set_A)

    df_common = pd.concat([
        df_A[df_A[id_col].astype(str).isin(common_ids)].assign(_project=project_A),
        df_B[df_B[id_col].astype(str).isin(common_ids)].assign(_project=project_B)
    ])

    df_unique_A = df_A[df_A[id_col].astype(str).isin(unique_A)]
    df_unique_B = df_B[df_B[id_col].astype(str).isin(unique_B)]

    return df_common, df_unique_A, df_unique_B


def summarize_differences(df_common: pd.DataFrame, fields: list, id_col: str = "Reference") -> pd.DataFrame:
    """
    Compare champ à champ pour chaque ID commun.

    :param df_common: DataFrame concaténé contenant _project
    :param fields: Champs à comparer
    :param id_col: Clé d'identifiant
    :return: DataFrame des divergences
    """
    grouped = df_common.groupby(id_col)
    diffs = []

    for req_id, group in grouped:
        if len(group) != 2:
            continue
        row_A, row_B = group.iloc[0], group.iloc[1]
        entry = {id_col: req_id}

        for field in fields:
            val_A = str(row_A.get(field, "")).strip()
            val_B = str(row_B.get(field, "")).strip()
            if val_A != val_B:
                entry[f"{field} ({row_A['_project']})"] = val_A
                entry[f"{field} ({row_B['_project']})"] = val_B

        if len(entry) > 1:
            diffs.append(entry)

    return pd.DataFrame(diffs)


def compare_all_matrices(loader: STILoader) -> Dict[str, dict]:
    """
    Applique la comparaison à toutes les matrices.

    :param loader: Instance de STILoader
    :return: Dictionnaire des résultats par matrice
    """
    results = {}
    fields = loader.fields_to_compare
    id_col = loader.id_column

    for matrix_name in loader.list_sti_names():
        df_common, df_unique_A, df_unique_B = compare_matrix_entries(loader, matrix_name)
        df_diff = summarize_differences(df_common, fields, id_col=id_col)

        results[matrix_name] = {
            "common": df_common,
            "unique_A": df_unique_A,
            "unique_B": df_unique_B,
            "differences": df_diff
        }

    return results

