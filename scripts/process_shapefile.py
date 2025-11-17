import json
import zipfile
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "config.json"


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def unzip_all():
    cfg = load_config()
    download_dir = Path(cfg["paths"]["download_dir"])
    unzip_dir = Path(cfg["paths"]["unzip_dir"])
    unzip_dir.mkdir(parents=True, exist_ok=True)

    for ds in cfg["datasets"]:
        name = ds["name"]
        src_dir = download_dir / name
        if not src_dir.exists():
            print(f"[AVISO] Diretório de download não existe: {src_dir}")
            continue

        print(f"=== Descompactando dataset: {name} ===")
        for zip_path in src_dir.glob("*.zip"):
            target_dir = unzip_dir / name / zip_path.stem
            target_dir.mkdir(parents=True, exist_ok=True)
            print(f"[UNZIP] {zip_path} -> {target_dir}")
            try:
                with zipfile.ZipFile(zip_path, "r") as zf:
                    zf.extractall(target_dir)
            except Exception as e:
                print(f"[ERRO] Falha ao descompactar {zip_path}: {e}")


def main():
    unzip_all()


if __name__ == "__main__":
    main()
