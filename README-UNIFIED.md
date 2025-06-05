# Continuity Protocol - Servidor Unificado

Este é o servidor unificado do Continuity Protocol, que combina todas as funcionalidades dos servidores anteriores em uma única implementação coesa e robusta.

## Visão Geral

O Continuity Protocol é uma implementação cibernética do Model Context Protocol (MCP) projetada para manter o contexto entre diferentes LLMs (Large Language Models) e ambientes de desenvolvimento.

## Funcionalidades

- **Recuperação Automática**: Restaura o contexto de trabalho em diferentes sessões
- **Sistema de Detecção Mágica**: Detecta automaticamente padrões e intenções
- **Backup de Emergência**: Sistema robusto de backup e recuperação
- **Integração com Claude Desktop**: Ferramentas MCP nativas no Claude

## Uso

### Iniciar o Servidor

```bash
cd /Users/lucascardoso/apps/MCP/CONTINUITY
./start-continuity-server.sh
```

### Parar o Servidor

```bash
cd /Users/lucascardoso/apps/MCP/CONTINUITY
./stop-continuity-server.sh
```

### Configurar Claude Desktop

A configuração do Claude Desktop já foi atualizada para usar o servidor unificado. Você precisa apenas reiniciar o Claude Desktop para aplicar as mudanças.

### Ferramentas Disponíveis

- `continuity_status`: Verifica o status do servidor
- `continuity_test`: Testa o funcionamento do servidor
- `continuity_where_stopped`: Executa recuperação automática
- `continuity_magic_system`: Processa entrada através do sistema de detecção
- `continuity_emergency_freeze`: Cria backup de emergência
- `continuity_emergency_unfreeze`: Restaura de backup de emergência
- `continuity_system_status`: Obtém status completo do sistema

## Arquivos Principais

- `unified-continuity-server.py`: Servidor MCP unificado
- `start-continuity-server.sh`: Script para iniciar o servidor
- `stop-continuity-server.sh`: Script para parar o servidor
- `autonomous-recovery.sh`: Script de recuperação automática
- `magic-system.sh`: Sistema de detecção mágica
- `emergency-absolute.sh`: Sistema de backup de emergência

## Logs

Os logs do servidor são armazenados em:

```
/Users/lucascardoso/apps/MCP/CONTINUITY/logs/continuity-server.log
```

## Backup de Emergência

Para criar um backup de emergência manualmente:

```bash
cd /Users/lucascardoso/apps/MCP/CONTINUITY
./emergency-absolute.sh freeze
```

Para restaurar de um backup de emergência:

```bash
cd /Users/lucascardoso/apps/MCP/CONTINUITY
./emergency-absolute.sh unfreeze
```