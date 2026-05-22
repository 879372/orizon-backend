import os
import sys
import subprocess
import logging
from datetime import datetime
from urllib.parse import urlparse
import boto3
from botocore.client import Config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_backup():
    logger.info("Iniciando processo de backup...")
    
    # 1. Carregar variáveis de ambiente
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        logger.error("Erro: A variável de ambiente DATABASE_URL não está configurada.")
        sys.exit(1)
        
    aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    bucket_name = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    
    if not all([aws_access_key, aws_secret_key, bucket_name]):
        logger.error("Erro: Credenciais AWS S3/Tigris incompletas no ambiente.")
        sys.exit(1)
        
    region_name = os.environ.get('AWS_S3_REGION_NAME', 'auto')
    endpoint_url = os.environ.get('AWS_S3_ENDPOINT_URL', 'https://t3.storageapi.dev')
    
    # 2. Parse da URL do banco de dados
    try:
        url = urlparse(database_url)
        db_user = url.username
        db_password = url.password
        db_host = url.hostname
        db_port = url.port or 5432
        db_name = url.path.lstrip('/')
    except Exception as e:
        logger.error(f"Erro ao processar DATABASE_URL: {e}")
        sys.exit(1)
        
    # 3. Executar o pg_dump
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"backup_{db_name}_{timestamp}.dump"
    
    logger.info(f"Gerando dump do banco de dados {db_name} para o arquivo local {backup_filename}...")
    
    env = os.environ.copy()
    if db_password:
        env['PGPASSWORD'] = db_password
        
    cmd = [
        'pg_dump',
        '-h', db_host,
        '-p', str(db_port),
        '-U', db_user,
        '-d', db_name,
        '-F', 'c', # Formato customizado binário comprimido postgresql
        '-f', backup_filename
    ]
    
    try:
        subprocess.run(cmd, env=env, check=True)
        logger.info("Dump gerado com sucesso.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro ao executar o pg_dump: {e}")
        if os.path.exists(backup_filename):
            os.remove(backup_filename)
        sys.exit(1)
        
    # 4. Upload para o bucket S3
    logger.info("Conectando ao bucket S3/Tigris e iniciando upload...")
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region_name,
            endpoint_url=endpoint_url,
            config=Config(signature_version='s3v4')
        )
        
        s3_key = f"backups/{backup_filename}"
        s3_client.upload_file(
            Filename=backup_filename,
            Bucket=bucket_name,
            Key=s3_key
        )
        logger.info(f"Backup enviado com sucesso para {bucket_name}/{s3_key}")
    except Exception as e:
        logger.error(f"Erro ao enviar o arquivo para o S3: {e}")
        sys.exit(1)
    finally:
        # Remover o arquivo temporário local
        if os.path.exists(backup_filename):
            try:
                os.remove(backup_filename)
                logger.info("Arquivo de backup local removido.")
            except Exception as e:
                logger.error(f"Erro ao remover arquivo temporário local: {e}")

if __name__ == '__main__':
    run_backup()
