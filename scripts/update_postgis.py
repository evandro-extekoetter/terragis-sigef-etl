import json
import os
import subprocess
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "config.json"


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_conn_string(db_cfg: dict) -> str:
    host = os.environ.get(db_cfg["host_env"])
    port = os.environ.get(db_cfg["port_env"], "5432")
    dbname = os.environ.get(db_cfg["name_env"])
    user = os.environ.get(db_cfg["user_env"])
    password = os.environ.get(db_cfg["password_env"])

    if not all([host, dbname, user, password]):
        raise RuntimeError("Variáveis de ambiente do banco não configuradas. "
                           "Verifique PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD.")

    return f"PG:host={host} port={port} dbname={dbname} user={user} password={password}"


def import_shapefile(conn_str: str, schema: str, table: str, shp_path: Path, uf: str, first_import: bool):
    full_table = f"{schema}.{table}"
    print(f"[IMPORT] {shp_path} -> {full_table} (UF={uf}, first_import={first_import})")

    cmd = [
        "ogr2ogr",
        "-f", "PostgreSQL",
        conn_str,
        str(shp_path),
        "-nln", full_table,
        "-nlt", "PROMOTE_TO_MULTI",
        "-lco", "GEOMETRY_NAME=geom",
        "-lco", "FID=id",
        "-lco", "SPATIAL_INDEX=YES"
    ]

    # Primeira UF sobrescreve a tabela, demais fazem append
    if first_import:
        cmd.append("-overwrite")
    else:
        cmd.append("-append")

    # Adicionar coluna UF aos dados
    cmd.extend([
        "-sql",
        f"SELECT *, '{uf}' AS uf FROM OGRGeoJSON"
    ])

    subprocess.check_call(cmd)


def main():
    cfg = load_config()
    unzip_dir = Path(cfg["paths"]["unzip_dir"])
    db_cfg = cfg["db"]
    conn_str = get_conn_string(db_cfg)

    for ds in cfg["datasets"]:
        name = ds["name"]
        target_table = ds["target_table"]
        base_dir = unzip_dir / name

        if not base_dir.exists():
            print(f"[AVISO] Diretório descompactado não existe: {base_dir}")
            continue

        print(f"=== Importando dataset: {name} -> tabela {target_table} ===")

        # Primeiro shapefile sobrescreve, os demais fazem append
        first_import = True

        # Ordena para processar sempre na mesma ordem
        for uf_dir in sorted(base_dir.glob(f"{name}_*")):
            uf = uf_dir.name.split("_")[-1]  # espera padrão name_UF
            shp_files = list(uf_dir.rglob("*.shp"))
            if not shp_files:
                print(f"[AVISO] Nenhum shapefile encontrado em {uf_dir}")
                continue

            shp_path = shp_files[0]
            try:
                import_shapefile(conn_str, db_cfg["schema"], target_table, shp_path, uf, first_import)
                first_import = False
            except subprocess.CalledProcessError as e:
                print(f"[ERRO] Falha ao importar {shp_path}: {e}")


if __name__ == "__main__":
    main()
