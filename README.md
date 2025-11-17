# terragis-sigef-etl

ETL automático para atualizar a base SIGEF/SNCI usada pelo WebGIS TerraGIS.

## Fluxo básico

1. `scripts/download_sigef.py`  
   - Lê `config/config.json`.
   - Baixa arquivos SIGEF e SNCI por UF (zip), usando os `url_template` configurados.

2. `scripts/process_shapefile.py`  
   - Descompacta os arquivos `.zip` para `data/unzipped/{dataset}/{dataset}_UF/...`.

3. `scripts/update_postgis.py`  
   - Lê os shapefiles descompactados e importa para o banco **PostGIS**.
   - Primeiro shapefile de cada dataset sobrescreve a tabela; os demais fazem append.

Tudo é orquestrado pelo GitHub Actions em `.github/workflows/update-daily.yml`.

## Configuração

1. Ajustar `config/config.json`:
   - Substituir `https://SEU_ENDPOINT_SIGEF/{uf}.zip` e `https://SEU_ENDPOINT_SNCI/{uf}.zip`
     pelos endpoints reais de download por UF.
   - Ajustar nomes de tabelas (`target_table`) se necessário.

2. Definir os **secrets** do banco no repositório GitHub:
   - `PGHOST`
   - `PGPORT`
   - `PGDATABASE`
   - `PGUSER`
   - `PGPASSWORD`

3. Verificar se o GDAL/ogr2ogr atende às necessidades de projeção/SRID.

## Execução

- O workflow `update-daily.yml` roda automaticamente todos os dias às 03:00 UTC.
- Também pode ser disparado manualmente via aba **Actions** no GitHub.

Após a importação, as tabelas no PostGIS ficam prontas para serem consumidas
pelo servidor de mapas/tiles e, em seguida, pelo WebGIS TerraGIS.
