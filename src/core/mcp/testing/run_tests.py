#!/usr/bin/env python3
"""
Test Runner - Continuity Protocol
Script para executar todos os testes do Continuity Protocol
"""

import os
import sys
import time
import unittest
import argparse
from datetime import datetime

# Adicionar diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Importar testes
from core.mcp.testing.integration_tests import IntegrationTests
from core.mcp.testing.functional_tests import FunctionalTests
from core.mcp.testing.stress_tests import StressTests

# Importar componentes para relatório
try:
    from core.mcp.integration_v2 import enhanced_context_protocol
except ImportError:
    print("Erro ao importar componentes do Continuity Protocol")
    sys.exit(1)

def run_tests(test_type=None, verbose=False):
    """
    Executa os testes especificados
    
    Args:
        test_type: Tipo de teste a ser executado ("integration", "functional", "stress", "all")
        verbose: Se True, exibe saída detalhada
    
    Returns:
        tuple: (sucesso, resultado)
    """
    # Configurar verbosidade
    verbosity = 2 if verbose else 1
    
    # Criar suite de testes
    suite = unittest.TestSuite()
    
    if test_type == "integration" or test_type == "all":
        suite.addTest(unittest.makeSuite(IntegrationTests))
    
    if test_type == "functional" or test_type == "all":
        suite.addTest(unittest.makeSuite(FunctionalTests))
    
    if test_type == "stress" or test_type == "all":
        suite.addTest(unittest.makeSuite(StressTests))
    
    # Executar testes
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    return result.wasSuccessful(), result

def create_test_report(test_type, result, start_time, end_time):
    """
    Cria relatório de testes
    
    Args:
        test_type: Tipo de teste executado
        result: Resultado dos testes
        start_time: Hora de início dos testes
        end_time: Hora de término dos testes
    
    Returns:
        str: ID do artefato de relatório
    """
    # Calcular estatísticas
    elapsed_time = end_time - start_time
    success_count = result.testsRun - len(result.errors) - len(result.failures)
    success_rate = success_count / result.testsRun if result.testsRun > 0 else 0
    
    # Criar conteúdo do relatório
    content = f"# Relatório de Testes - Continuity Protocol\n\n"
    content += f"## Resumo\n\n"
    content += f"- **Tipo de Teste**: {test_type}\n"
    content += f"- **Data de Execução**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    content += f"- **Tempo de Execução**: {elapsed_time:.2f} segundos\n"
    content += f"- **Testes Executados**: {result.testsRun}\n"
    content += f"- **Testes Bem-Sucedidos**: {success_count}\n"
    content += f"- **Taxa de Sucesso**: {success_rate*100:.2f}%\n\n"
    
    # Adicionar erros e falhas
    if result.errors:
        content += f"## Erros ({len(result.errors)})\n\n"
        for i, (test, error) in enumerate(result.errors):
            content += f"### Erro {i+1}: {test}\n\n"
            content += f"```\n{error}\n```\n\n"
    
    if result.failures:
        content += f"## Falhas ({len(result.failures)})\n\n"
        for i, (test, failure) in enumerate(result.failures):
            content += f"### Falha {i+1}: {test}\n\n"
            content += f"```\n{failure}\n```\n\n"
    
    # Adicionar conclusão
    if result.wasSuccessful():
        content += f"## Conclusão\n\n"
        content += f"✅ **TODOS OS TESTES PASSARAM**\n\n"
        content += f"O sistema está funcionando conforme esperado.\n"
    else:
        content += f"## Conclusão\n\n"
        content += f"❌ **ALGUNS TESTES FALHARAM**\n\n"
        content += f"É necessário corrigir os problemas identificados.\n"
    
    # Criar artefato
    artifact_info = enhanced_context_protocol.store_artifact(
        content,
        "test_report",
        "mcp-continuity-service",
        "test_runner",
        {
            "title": f"Relatório de Testes - {test_type.capitalize()}",
            "description": f"Relatório de execução de testes {test_type}",
            "version": "1.0.0",
            "test_type": test_type,
            "tests_run": result.testsRun,
            "success_rate": success_rate
        }
    )
    
    return artifact_info["id"]

def main():
    """Função principal"""
    # Configurar parser de argumentos
    parser = argparse.ArgumentParser(description="Executa testes do Continuity Protocol")
    parser.add_argument("--type", choices=["integration", "functional", "stress", "all"],
                        default="all", help="Tipo de teste a ser executado")
    parser.add_argument("--verbose", action="store_true", help="Exibe saída detalhada")
    parser.add_argument("--report", action="store_true", help="Cria relatório de testes")
    
    # Parsear argumentos
    args = parser.parse_args()
    
    # Exibir informações
    print(f"Executando testes do tipo: {args.type}")
    print(f"Verbosidade: {'ativada' if args.verbose else 'desativada'}")
    print(f"Relatório: {'será criado' if args.report else 'não será criado'}")
    print()
    
    # Executar testes
    start_time = time.time()
    success, result = run_tests(args.type, args.verbose)
    end_time = time.time()
    
    # Exibir resultado
    print()
    print(f"Tempo de execução: {end_time - start_time:.2f} segundos")
    print(f"Resultado: {'SUCESSO' if success else 'FALHA'}")
    
    # Criar relatório
    if args.report:
        try:
            report_id = create_test_report(args.type, result, start_time, end_time)
            print(f"Relatório criado: {report_id}")
        except Exception as e:
            print(f"Erro ao criar relatório: {str(e)}")
    
    # Retornar código de saída
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
