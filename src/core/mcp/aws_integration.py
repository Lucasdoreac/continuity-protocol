#!/usr/bin/env python3
"""
AWS Integration - Continuity Protocol
Integração com serviços AWS para armazenamento, notificações e processamento
"""

import os
import sys
import json
import time
import logging
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Callable

# Adicionar diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Importar componentes
try:
    from core.mcp.notification import notification_system
except ImportError:
    print("Erro ao importar componentes do Continuity Protocol")
    sys.exit(1)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                        "logs", "aws_integration.log"))
    ]
)

logger = logging.getLogger("aws_integration")

class AWSIntegration:
    """
    Integração com serviços AWS para o Continuity Protocol
    """
    
    def __init__(self, config_file: str = None):
        """
        Inicializa a integração com AWS
        
        Args:
            config_file: Arquivo de configuração AWS
        """
        # Configurar arquivo de configuração
        if config_file:
            self.config_file = config_file
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.config_file = os.path.join(base_dir, "config", "aws_config.json")
        
        # Criar diretório de configuração se não existir
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        # Carregar ou criar configuração
        self.config = self._load_or_create_config()
        
        # Verificar dependências
        self.boto3_available = self._check_boto3()
        
        if not self.boto3_available:
            logger.warning("Biblioteca boto3 não encontrada. Funcionalidades AWS estarão limitadas.")
            notification_system.create_notification(
                "Dependência AWS não encontrada",
                "A biblioteca boto3 não está instalada. Funcionalidades AWS estarão limitadas.",
                "warning",
                "aws_integration"
            )
        
        # Inicializar clientes AWS
        self.s3_client = None
        self.sns_client = None
        self.lambda_client = None
        self.cloudwatch_client = None
        
        # Inicializar clientes se boto3 estiver disponível
        if self.boto3_available:
            self._initialize_clients()
    
    def _check_boto3(self) -> bool:
        """
        Verifica se boto3 está disponível
        
        Returns:
            bool: True se boto3 está disponível, False caso contrário
        """
        try:
            import boto3
            return True
        except ImportError:
            return False
    
    def _load_or_create_config(self) -> Dict[str, Any]:
        """
        Carrega ou cria configuração AWS
        
        Returns:
            Dict: Configuração AWS
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Criar configuração padrão
        config = {
            "region": "us-east-1",
            "s3": {
                "bucket": "continuity-protocol-artifacts",
                "enabled": False
            },
            "sns": {
                "topic_arn": "",
                "enabled": False
            },
            "lambda": {
                "function_name": "",
                "enabled": False
            },
            "cloudwatch": {
                "log_group": "continuity-protocol",
                "enabled": False
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Salvar configuração
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def _save_config(self) -> None:
        """Salva configuração AWS"""
        self.config["updated_at"] = datetime.now().isoformat()
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def _initialize_clients(self) -> None:
        """Inicializa clientes AWS"""
        if not self.boto3_available:
            return
        
        try:
            import boto3
            
            # Inicializar clientes
            self.s3_client = boto3.client('s3', region_name=self.config["region"])
            self.sns_client = boto3.client('sns', region_name=self.config["region"])
            self.lambda_client = boto3.client('lambda', region_name=self.config["region"])
            self.cloudwatch_client = boto3.client('logs', region_name=self.config["region"])
            
            logger.info("Clientes AWS inicializados com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar clientes AWS: {str(e)}")
            self.s3_client = None
            self.sns_client = None
            self.lambda_client = None
            self.cloudwatch_client = None
    
    def update_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Atualiza configuração AWS
        
        Args:
            config: Nova configuração
            
        Returns:
            Dict: Resultado da atualização
        """
        # Validar configuração
        if not isinstance(config, dict):
            return {
                "success": False,
                "error": "Configuração inválida"
            }
        
        # Atualizar campos
        for key in ["region", "s3", "sns", "lambda", "cloudwatch"]:
            if key in config:
                self.config[key] = config[key]
        
        # Salvar configuração
        self._save_config()
        
        # Reinicializar clientes
        self._initialize_clients()
        
        return {
            "success": True,
            "config": self.config
        }
    
    def get_config(self) -> Dict[str, Any]:
        """
        Obtém configuração AWS
        
        Returns:
            Dict: Configuração AWS
        """
        return {
            "success": True,
            "config": self.config
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Testa conexão com AWS
        
        Returns:
            Dict: Resultado do teste
        """
        if not self.boto3_available:
            return {
                "success": False,
                "error": "Biblioteca boto3 não encontrada"
            }
        
        results = {}
        
        # Testar S3
        if self.s3_client and self.config["s3"]["enabled"]:
            try:
                response = self.s3_client.list_buckets()
                results["s3"] = {
                    "success": True,
                    "buckets": [bucket["Name"] for bucket in response["Buckets"]]
                }
            except Exception as e:
                results["s3"] = {
                    "success": False,
                    "error": str(e)
                }
        else:
            results["s3"] = {
                "success": False,
                "error": "S3 não configurado ou desabilitado"
            }
        
        # Testar SNS
        if self.sns_client and self.config["sns"]["enabled"]:
            try:
                response = self.sns_client.list_topics()
                results["sns"] = {
                    "success": True,
                    "topics": [topic["TopicArn"] for topic in response["Topics"]]
                }
            except Exception as e:
                results["sns"] = {
                    "success": False,
                    "error": str(e)
                }
        else:
            results["sns"] = {
                "success": False,
                "error": "SNS não configurado ou desabilitado"
            }
        
        # Testar Lambda
        if self.lambda_client and self.config["lambda"]["enabled"]:
            try:
                response = self.lambda_client.list_functions()
                results["lambda"] = {
                    "success": True,
                    "functions": [function["FunctionName"] for function in response["Functions"]]
                }
            except Exception as e:
                results["lambda"] = {
                    "success": False,
                    "error": str(e)
                }
        else:
            results["lambda"] = {
                "success": False,
                "error": "Lambda não configurado ou desabilitado"
            }
        
        # Testar CloudWatch
        if self.cloudwatch_client and self.config["cloudwatch"]["enabled"]:
            try:
                response = self.cloudwatch_client.describe_log_groups()
                results["cloudwatch"] = {
                    "success": True,
                    "log_groups": [log_group["logGroupName"] for log_group in response["logGroups"]]
                }
            except Exception as e:
                results["cloudwatch"] = {
                    "success": False,
                    "error": str(e)
                }
        else:
            results["cloudwatch"] = {
                "success": False,
                "error": "CloudWatch não configurado ou desabilitado"
            }
        
        # Determinar sucesso geral
        overall_success = any([results[service]["success"] for service in results])
        
        return {
            "success": overall_success,
            "results": results
        }
    
    def upload_to_s3(self, file_path: str, object_key: str = None, metadata: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Faz upload de arquivo para S3
        
        Args:
            file_path: Caminho do arquivo
            object_key: Chave do objeto no S3 (usa nome do arquivo se None)
            metadata: Metadados do objeto
            
        Returns:
            Dict: Resultado do upload
        """
        if not self.boto3_available or not self.s3_client or not self.config["s3"]["enabled"]:
            return {
                "success": False,
                "error": "S3 não configurado ou desabilitado"
            }
        
        # Verificar se arquivo existe
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"Arquivo não encontrado: {file_path}"
            }
        
        # Determinar chave do objeto
        if object_key is None:
            object_key = os.path.basename(file_path)
        
        # Preparar metadados
        if metadata is None:
            metadata = {}
        
        # Converter metadados para strings
        string_metadata = {k: str(v) for k, v in metadata.items()}
        
        try:
            # Fazer upload
            with open(file_path, 'rb') as f:
                self.s3_client.upload_fileobj(
                    f,
                    self.config["s3"]["bucket"],
                    object_key,
                    ExtraArgs={"Metadata": string_metadata}
                )
            
            # Obter URL do objeto
            url = f"https://{self.config['s3']['bucket']}.s3.{self.config['region']}.amazonaws.com/{object_key}"
            
            logger.info(f"Arquivo {file_path} enviado para S3: {url}")
            
            return {
                "success": True,
                "bucket": self.config["s3"]["bucket"],
                "object_key": object_key,
                "url": url
            }
        except Exception as e:
            logger.error(f"Erro ao enviar arquivo para S3: {str(e)}")
            
            return {
                "success": False,
                "error": f"Erro ao enviar arquivo para S3: {str(e)}"
            }
    
    def download_from_s3(self, object_key: str, file_path: str) -> Dict[str, Any]:
        """
        Faz download de arquivo do S3
        
        Args:
            object_key: Chave do objeto no S3
            file_path: Caminho para salvar o arquivo
            
        Returns:
            Dict: Resultado do download
        """
        if not self.boto3_available or not self.s3_client or not self.config["s3"]["enabled"]:
            return {
                "success": False,
                "error": "S3 não configurado ou desabilitado"
            }
        
        try:
            # Criar diretório se não existir
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Fazer download
            self.s3_client.download_file(
                self.config["s3"]["bucket"],
                object_key,
                file_path
            )
            
            logger.info(f"Arquivo {object_key} baixado do S3 para {file_path}")
            
            return {
                "success": True,
                "bucket": self.config["s3"]["bucket"],
                "object_key": object_key,
                "file_path": file_path
            }
        except Exception as e:
            logger.error(f"Erro ao baixar arquivo do S3: {str(e)}")
            
            return {
                "success": False,
                "error": f"Erro ao baixar arquivo do S3: {str(e)}"
            }
    
    def list_s3_objects(self, prefix: str = None) -> Dict[str, Any]:
        """
        Lista objetos no S3
        
        Args:
            prefix: Prefixo para filtrar objetos
            
        Returns:
            Dict: Lista de objetos
        """
        if not self.boto3_available or not self.s3_client or not self.config["s3"]["enabled"]:
            return {
                "success": False,
                "error": "S3 não configurado ou desabilitado"
            }
        
        try:
            # Listar objetos
            if prefix:
                response = self.s3_client.list_objects_v2(
                    Bucket=self.config["s3"]["bucket"],
                    Prefix=prefix
                )
            else:
                response = self.s3_client.list_objects_v2(
                    Bucket=self.config["s3"]["bucket"]
                )
            
            # Extrair informações dos objetos
            objects = []
            if "Contents" in response:
                for obj in response["Contents"]:
                    objects.append({
                        "key": obj["Key"],
                        "size": obj["Size"],
                        "last_modified": obj["LastModified"].isoformat(),
                        "url": f"https://{self.config['s3']['bucket']}.s3.{self.config['region']}.amazonaws.com/{obj['Key']}"
                    })
            
            return {
                "success": True,
                "bucket": self.config["s3"]["bucket"],
                "objects": objects,
                "count": len(objects)
            }
        except Exception as e:
            logger.error(f"Erro ao listar objetos no S3: {str(e)}")
            
            return {
                "success": False,
                "error": f"Erro ao listar objetos no S3: {str(e)}"
            }
    
    def delete_s3_object(self, object_key: str) -> Dict[str, Any]:
        """
        Remove objeto do S3
        
        Args:
            object_key: Chave do objeto no S3
            
        Returns:
            Dict: Resultado da remoção
        """
        if not self.boto3_available or not self.s3_client or not self.config["s3"]["enabled"]:
            return {
                "success": False,
                "error": "S3 não configurado ou desabilitado"
            }
        
        try:
            # Remover objeto
            self.s3_client.delete_object(
                Bucket=self.config["s3"]["bucket"],
                Key=object_key
            )
            
            logger.info(f"Objeto {object_key} removido do S3")
            
            return {
                "success": True,
                "bucket": self.config["s3"]["bucket"],
                "object_key": object_key
            }
        except Exception as e:
            logger.error(f"Erro ao remover objeto do S3: {str(e)}")
            
            return {
                "success": False,
                "error": f"Erro ao remover objeto do S3: {str(e)}"
            }
    
    def publish_to_sns(self, message: str, subject: str = None, attributes: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Publica mensagem no SNS
        
        Args:
            message: Mensagem a ser publicada
            subject: Assunto da mensagem
            attributes: Atributos da mensagem
            
        Returns:
            Dict: Resultado da publicação
        """
        if not self.boto3_available or not self.sns_client or not self.config["sns"]["enabled"]:
            return {
                "success": False,
                "error": "SNS não configurado ou desabilitado"
            }
        
        # Verificar se topic_arn está configurado
        if not self.config["sns"]["topic_arn"]:
            return {
                "success": False,
                "error": "ARN do tópico SNS não configurado"
            }
        
        try:
            # Preparar parâmetros
            params = {
                "TopicArn": self.config["sns"]["topic_arn"],
                "Message": message
            }
            
            if subject:
                params["Subject"] = subject
            
            if attributes:
                # Converter atributos para formato SNS
                message_attributes = {}
                for key, value in attributes.items():
                    if isinstance(value, str):
                        message_attributes[key] = {
                            "DataType": "String",
                            "StringValue": value
                        }
                    elif isinstance(value, (int, float)):
                        message_attributes[key] = {
                            "DataType": "Number",
                            "StringValue": str(value)
                        }
                    elif isinstance(value, bool):
                        message_attributes[key] = {
                            "DataType": "String",
                            "StringValue": str(value).lower()
                        }
                
                params["MessageAttributes"] = message_attributes
            
            # Publicar mensagem
            response = self.sns_client.publish(**params)
            
            logger.info(f"Mensagem publicada no SNS: {response['MessageId']}")
            
            return {
                "success": True,
                "topic_arn": self.config["sns"]["topic_arn"],
                "message_id": response["MessageId"]
            }
        except Exception as e:
            logger.error(f"Erro ao publicar mensagem no SNS: {str(e)}")
            
            return {
                "success": False,
                "error": f"Erro ao publicar mensagem no SNS: {str(e)}"
            }
    
    def invoke_lambda(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoca função Lambda
        
        Args:
            payload: Payload para a função
            
        Returns:
            Dict: Resultado da invocação
        """
        if not self.boto3_available or not self.lambda_client or not self.config["lambda"]["enabled"]:
            return {
                "success": False,
                "error": "Lambda não configurado ou desabilitado"
            }
        
        # Verificar se function_name está configurado
        if not self.config["lambda"]["function_name"]:
            return {
                "success": False,
                "error": "Nome da função Lambda não configurado"
            }
        
        try:
            # Converter payload para JSON
            payload_json = json.dumps(payload)
            
            # Invocar função
            response = self.lambda_client.invoke(
                FunctionName=self.config["lambda"]["function_name"],
                InvocationType="RequestResponse",
                Payload=payload_json
            )
            
            # Ler resposta
            response_payload = json.loads(response["Payload"].read().decode())
            
            logger.info(f"Função Lambda invocada: {self.config['lambda']['function_name']}")
            
            return {
                "success": True,
                "function_name": self.config["lambda"]["function_name"],
                "status_code": response["StatusCode"],
                "response": response_payload
            }
        except Exception as e:
            logger.error(f"Erro ao invocar função Lambda: {str(e)}")
            
            return {
                "success": False,
                "error": f"Erro ao invocar função Lambda: {str(e)}"
            }
    
    def log_to_cloudwatch(self, message: str, log_stream: str = None, log_level: str = "INFO") -> Dict[str, Any]:
        """
        Envia log para CloudWatch
        
        Args:
            message: Mensagem de log
            log_stream: Stream de log (usa timestamp se None)
            log_level: Nível de log
            
        Returns:
            Dict: Resultado do envio
        """
        if not self.boto3_available or not self.cloudwatch_client or not self.config["cloudwatch"]["enabled"]:
            return {
                "success": False,
                "error": "CloudWatch não configurado ou desabilitado"
            }
        
        # Verificar se log_group está configurado
        if not self.config["cloudwatch"]["log_group"]:
            return {
                "success": False,
                "error": "Grupo de log CloudWatch não configurado"
            }
        
        # Determinar stream de log
        if log_stream is None:
            log_stream = f"continuity-protocol-{datetime.now().strftime('%Y-%m-%d')}"
        
        try:
            # Verificar se grupo de log existe
            try:
                self.cloudwatch_client.describe_log_groups(
                    logGroupNamePrefix=self.config["cloudwatch"]["log_group"]
                )
            except:
                # Criar grupo de log se não existir
                self.cloudwatch_client.create_log_group(
                    logGroupName=self.config["cloudwatch"]["log_group"]
                )
            
            # Verificar se stream de log existe
            try:
                self.cloudwatch_client.describe_log_streams(
                    logGroupName=self.config["cloudwatch"]["log_group"],
                    logStreamNamePrefix=log_stream
                )
            except:
                # Criar stream de log se não existir
                self.cloudwatch_client.create_log_stream(
                    logGroupName=self.config["cloudwatch"]["log_group"],
                    logStreamName=log_stream
                )
            
            # Enviar log
            self.cloudwatch_client.put_log_events(
                logGroupName=self.config["cloudwatch"]["log_group"],
                logStreamName=log_stream,
                logEvents=[
                    {
                        "timestamp": int(time.time() * 1000),
                        "message": f"[{log_level}] {message}"
                    }
                ]
            )
            
            logger.info(f"Log enviado para CloudWatch: {log_stream}")
            
            return {
                "success": True,
                "log_group": self.config["cloudwatch"]["log_group"],
                "log_stream": log_stream
            }
        except Exception as e:
            logger.error(f"Erro ao enviar log para CloudWatch: {str(e)}")
            
            return {
                "success": False,
                "error": f"Erro ao enviar log para CloudWatch: {str(e)}"
            }
    
    def backup_to_s3(self, directory: str, prefix: str = None) -> Dict[str, Any]:
        """
        Faz backup de diretório para S3
        
        Args:
            directory: Diretório a ser copiado
            prefix: Prefixo para os objetos no S3
            
        Returns:
            Dict: Resultado do backup
        """
        if not self.boto3_available or not self.s3_client or not self.config["s3"]["enabled"]:
            return {
                "success": False,
                "error": "S3 não configurado ou desabilitado"
            }
        
        # Verificar se diretório existe
        if not os.path.exists(directory) or not os.path.isdir(directory):
            return {
                "success": False,
                "error": f"Diretório não encontrado: {directory}"
            }
        
        # Determinar prefixo
        if prefix is None:
            prefix = f"backup/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}/"
        
        # Garantir que prefixo termina com /
        if not prefix.endswith('/'):
            prefix += '/'
        
        try:
            # Listar arquivos no diretório
            uploaded_files = []
            total_size = 0
            
            for root, _, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Determinar chave do objeto
                    rel_path = os.path.relpath(file_path, directory)
                    object_key = f"{prefix}{rel_path}"
                    
                    # Fazer upload
                    with open(file_path, 'rb') as f:
                        self.s3_client.upload_fileobj(
                            f,
                            self.config["s3"]["bucket"],
                            object_key
                        )
                    
                    # Adicionar à lista de arquivos enviados
                    file_size = os.path.getsize(file_path)
                    uploaded_files.append({
                        "file_path": file_path,
                        "object_key": object_key,
                        "size": file_size
                    })
                    total_size += file_size
            
            logger.info(f"Backup concluído: {len(uploaded_files)} arquivos enviados para S3")
            
            return {
                "success": True,
                "bucket": self.config["s3"]["bucket"],
                "prefix": prefix,
                "files_count": len(uploaded_files),
                "total_size": total_size,
                "files": uploaded_files
            }
        except Exception as e:
            logger.error(f"Erro ao fazer backup para S3: {str(e)}")
            
            return {
                "success": False,
                "error": f"Erro ao fazer backup para S3: {str(e)}"
            }
    
    def restore_from_s3(self, prefix: str, directory: str) -> Dict[str, Any]:
        """
        Restaura backup do S3
        
        Args:
            prefix: Prefixo dos objetos no S3
            directory: Diretório para restaurar os arquivos
            
        Returns:
            Dict: Resultado da restauração
        """
        if not self.boto3_available or not self.s3_client or not self.config["s3"]["enabled"]:
            return {
                "success": False,
                "error": "S3 não configurado ou desabilitado"
            }
        
        # Garantir que prefixo termina com /
        if not prefix.endswith('/'):
            prefix += '/'
        
        try:
            # Criar diretório se não existir
            os.makedirs(directory, exist_ok=True)
            
            # Listar objetos com o prefixo
            response = self.s3_client.list_objects_v2(
                Bucket=self.config["s3"]["bucket"],
                Prefix=prefix
            )
            
            if "Contents" not in response:
                return {
                    "success": False,
                    "error": f"Nenhum objeto encontrado com o prefixo: {prefix}"
                }
            
            # Baixar cada objeto
            downloaded_files = []
            total_size = 0
            
            for obj in response["Contents"]:
                object_key = obj["Key"]
                
                # Determinar caminho do arquivo
                rel_path = object_key[len(prefix):]
                file_path = os.path.join(directory, rel_path)
                
                # Criar diretório pai se não existir
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                # Baixar arquivo
                self.s3_client.download_file(
                    self.config["s3"]["bucket"],
                    object_key,
                    file_path
                )
                
                # Adicionar à lista de arquivos baixados
                downloaded_files.append({
                    "object_key": object_key,
                    "file_path": file_path,
                    "size": obj["Size"]
                })
                total_size += obj["Size"]
            
            logger.info(f"Restauração concluída: {len(downloaded_files)} arquivos baixados do S3")
            
            return {
                "success": True,
                "bucket": self.config["s3"]["bucket"],
                "prefix": prefix,
                "files_count": len(downloaded_files),
                "total_size": total_size,
                "files": downloaded_files
            }
        except Exception as e:
            logger.error(f"Erro ao restaurar do S3: {str(e)}")
            
            return {
                "success": False,
                "error": f"Erro ao restaurar do S3: {str(e)}"
            }

# Instância global para uso em todo o sistema
aws_integration = AWSIntegration()
