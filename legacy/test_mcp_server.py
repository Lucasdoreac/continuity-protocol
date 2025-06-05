#!/usr/bin/env python3
"""
Teste simples do servidor MCP Continuity
"""
import asyncio
import subprocess
import json
import time

async def test_mcp_server():
    """Testa o servidor MCP com comandos básicos"""
    server_path = "/Users/lucascardoso/apps/MCP/CONTINUITY/mcp-continuity-server-fastmcp.py"
    
    # Inicia o servidor
    process = subprocess.Popen(
        ["python3", server_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0
    )
    
    try:
        # 1. Inicialização
        init_msg = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "id": 1,
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        
        print("🔄 Enviando inicialização...")
        process.stdin.write(json.dumps(init_msg) + "\n")
        process.stdin.flush()
        
        # Aguarda resposta
        response = process.stdout.readline()
        print("✅ Resposta de inicialização:")
        print(response)
        
        # 2. Lista ferramentas
        list_tools_msg = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": 2
        }
        
        print("\n🔄 Listando ferramentas...")
        process.stdin.write(json.dumps(list_tools_msg) + "\n")
        process.stdin.flush()
        
        # Aguarda resposta
        response = process.stdout.readline()
        print("✅ Lista de ferramentas:")
        print(response)
        
        # 3. Testa uma ferramenta
        call_tool_msg = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": 3,
            "params": {
                "name": "continuity_system_status",
                "arguments": {}
            }
        }
        
        print("\n🔄 Chamando ferramenta system_status...")
        process.stdin.write(json.dumps(call_tool_msg) + "\n")
        process.stdin.flush()
        
        # Aguarda resposta
        response = process.stdout.readline()
        print("✅ Resultado da ferramenta:")
        print(response)
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        
    finally:
        # Encerra o processo
        process.terminate()
        process.wait()
        print("\n🔒 Servidor encerrado")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
