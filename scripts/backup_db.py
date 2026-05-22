import os
import sys
import subprocess
import logging
from datetime import datetime
import boto3
from botocore.client import Config
from decouple import config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- CONFIGURAÇÕES ---
S3_BUCKET = config('AWS_STORAGE_BUCKET_NAME', default=None) or config('S3_BUCKET_NAME', default=None)
S3_ACCESS_KEY = config('AWS_ACCESS_KEY_ID', default=None) or config('S3_ACCESS_KEY_ID', default=None)
S3_SECRET_KEY = config('AWS_SECRET_ACCESS_KEY', default=None) or config('S3_SECRET_ACCESS_KEY', default=None)
S3_REGION = config('AWS_S3_REGION_NAME', default=None) or config('S3_REGION', default='us-east-1')
S3_ENDPOINT = config('AWS_S3_ENDPOINT_URL', default=None) or config('S3_ENDPOINT', default=None)

DATABASE_URL = config('DATABASE_URL', default=None)

# Caminho Temporário (usa a pasta temporária do sistema na Railway)
BACKUP_DIR = "/tmp/backups"
os.makedirs(BACKUP_DIR, exist_ok=True)

DATE_STR = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
FILE_NAME = f"backup_railway_{DATE_STR}.sql.gz"
FILE_PATH = os.path.join(BACKUP_DIR, FILE_NAME)

def run_backup():
    if not DATABASE_URL:
        logger.error("DATABASE_URL não encontrada no ambiente")
        sys.exit(1)
        
    if not all([S3_BUCKET, S3_ACCESS_KEY, S3_SECRET_KEY]):
        logger.error("Credenciais do Bucket S3 incompletas")
        sys.exit(1)

    logger.info("Iniciando backup...")

    try:
        # Tenta usar pg_dump direto (Railway/Linux) com formato Custom (-Fc)
        logger.info("Executando pg_dump (formato Custom)...")
        try:
            # -Fc: Binário e Compactado / --no-acl --no-owner: Evita erros de permissão
            dump_cmd = ["pg_dump", "-Fc", "--no-acl", "--no-owner", DATABASE_URL, "-f", FILE_PATH]
            subprocess.run(dump_cmd, capture_output=True, text=True, timeout=600, check=True)
        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            if isinstance(e, subprocess.CalledProcessError):
                logger.error(f"pg_dump direto falhou com status {e.returncode}. Stderr: {e.stderr}")
            else:
                logger.info("pg_dump direto não encontrado no path.")
            
            # Se falhar ou não achar pg_dump, tenta via Docker (Mac Local) usando postgres:18
            logger.info("Tentando via Docker com postgres:18...")
            dump_cmd = ["docker", "run", "--rm", "postgres:18", "pg_dump", "-Fc", "--no-acl", "--no-owner", DATABASE_URL]
            try:
                with open(FILE_PATH, "wb") as f:
                    subprocess.check_call(dump_cmd, stdout=f, timeout=600)
            except Exception as docker_err:
                raise Exception(f"Erro tanto no pg_dump nativo quanto via Docker. Detalhes Docker: {docker_err}")
        except subprocess.TimeoutExpired:
            raise Exception("O backup demorou demais (mais de 10 min) e foi cancelado automaticamente.")

        # Verifica se o arquivo tem conteúdo
        file_size = os.path.getsize(FILE_PATH)
        if file_size < 100: # Um backup real compactado deve ter mais que 100 bytes
            raise Exception(f"O arquivo de backup gerado está muito pequeno ({file_size} bytes). Algo deu errado no dump.")

        logger.info(f"Dump concluído ({file_size} bytes). Enviando para S3 ({S3_BUCKET})...")

        s3 = boto3.client(
            's3',
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY,
            region_name=S3_REGION,
            endpoint_url=S3_ENDPOINT,
            config=Config(signature_version='s3v4')
        )

        s3.upload_file(FILE_PATH, S3_BUCKET, f"backups/{FILE_NAME}")
        logger.info(f"Backup concluído com sucesso!")

        os.remove(FILE_PATH)

    except Exception as e:
        logger.error(f"ERRO no backup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_backup()
