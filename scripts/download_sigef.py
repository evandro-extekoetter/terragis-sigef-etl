import json
from pathlib import Path
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "config.json"


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def download_file(url: str, dest: Path):
    dest.parent.mkdir(parents=True, exist_ok=True)
    
    # Verificar se arquivo já existe e comparar tamanho/data
    if dest.exists():
        try:
            resp_head = requests.head(url, timeout=30, verify=False)
            remote_size = int(resp_head.headers.get('content-length', 0))
            local_size = dest.stat().st_size
            
            if remote_size > 0 and remote_size == local_size:
                print(f"[SKIP] {url} (arquivo já existe e tamanho coincide)")
                return
        except Exception as e:
            print(f"[AVISO] Não foi possível verificar mudanças: {e}. Baixando novamente...")
    
    print(f"[DOWNLOAD] {url} -> {dest}")
    resp = requests.get(url, stream=True, timeout=120, verify=False)
    resp.raise_for_status()
    with open(dest, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)


def main():
    cfg = load_config()
    download_dir = Path(cfg["paths"]["download_dir"])

    for ds in cfg["datasets"]:
        name = ds["name"]
        url_template = ds["url_template"]
        print(f"=== Dataset: {name} ===")

        for uf in cfg["ufs"]:
            url = url_template.format(uf=uf)
            dest = download_dir / name / f"{name}_{uf}.zip"

            try:
                # Se o arquivo já existe, pode-se optar por pular download.
                # Aqui sobrescrevemos sempre para simplificar.
                download_file(url, dest)
            except Exception as e:
                print(f"[ERRO] Falha ao baixar {name} {uf}: {e}")


if __name__ == "__main__":
    main()
