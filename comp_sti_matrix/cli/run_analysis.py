"""Fait l'analyse."""
import argparse
from comp_sti_matrix.core.analysis_driver import main

def parse_args():
    parser = argparse.ArgumentParser(description="Lance l’analyse STI")
    parser.add_argument(
        "--config", "-c",
        required=True,
        help="Chemin du fichier de configuration YAML (ex : data/GE_H2/sti_config.yaml)"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(config_path=args.config)
