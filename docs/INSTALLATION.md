# Guia de Instalação

Este guia explica como instalar e configurar o Protocolo de Continuidade de Projetos (PCP) em diferentes sistemas operacionais.

## Requisitos

- Python 3.8+
- Git
- Node.js 14+ (para extensão VSCode)

## Instalação via pip

A maneira mais simples de instalar o Protocolo de Continuidade é usando pip:

```bash
pip install git+https://github.com/Lucasdoreac/continuity-protocol.git
```

Isso instalará o pacote e suas dependências, além de disponibilizar o comando `continuity` no seu terminal.

## Instalação para Desenvolvimento

Se você deseja contribuir para o projeto ou personalizar a instalação, siga estas etapas:

```bash
# Clone o repositório
git clone https://github.com/Lucasdoreac/continuity-protocol.git
cd continuity-protocol

# Instale em modo de desenvolvimento
pip install -e .
```

Isso instalará o pacote em modo de desenvolvimento, permitindo que você faça alterações no código e veja os resultados imediatamente.

## Configuração

### 1. Inicializar o Servidor

O servidor de continuidade é responsável por gerenciar o contexto entre diferentes ferramentas:

```bash
continuity server
```

Por padrão, o servidor é executado em `localhost:8765`. Você pode alterar a porta usando a opção `--port`:

```bash
continuity server --port 9000
```

### 2. Estabelecer Simbiose com um Projeto

Para começar a usar o Protocolo de Continuidade com um projeto específico:

```bash
continuity project /caminho/do/seu/projeto
```

Isso analisará o projeto e estabelecerá uma simbiose com ele, permitindo que o sistema mantenha o contexto do projeto.

### 3. Criar uma Sessão

Crie uma sessão para começar a trabalhar:

```bash
continuity create-session --name "Meu Projeto" --description "Desenvolvimento da funcionalidade X"
```

### 4. Definir o Foco Atual

Defina o foco atual da sessão para ajudar a manter o contexto:

```bash
continuity focus --focus "Implementando autenticação de usuários"
```

### 5. Verificar Onde Você Parou

Quando precisar lembrar onde parou:

```bash
continuity where
```

## Configuração por Sistema Operacional

### Windows

No Windows, você pode configurar o Protocolo de Continuidade para iniciar automaticamente:

```bash
# Instalar como serviço Windows
python -m continuity.cross_platform.windows.setup
```

### macOS

No macOS, você pode usar o LaunchAgent para iniciar o servidor automaticamente:

```bash
# Criar arquivo LaunchAgent
mkdir -p ~/Library/LaunchAgents
cat > ~/Library/LaunchAgents/com.continuity.protocol.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.continuity.protocol</string>
    <key>ProgramArguments</key>
    <array>
        <string>$(which python)</string>
        <string>-m</string>
        <string>continuity.server.continuity_server</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>~/Library/Logs/continuity-protocol.log</string>
    <key>StandardErrorPath</key>
    <string>~/Library/Logs/continuity-protocol-error.log</string>
</dict>
</plist>
EOF

# Carregar o LaunchAgent
launchctl load ~/Library/LaunchAgents/com.continuity.protocol.plist
```

### Linux

No Linux, você pode usar o systemd para iniciar o servidor automaticamente:

```bash
# Criar arquivo de serviço systemd
cat > ~/.config/systemd/user/continuity-protocol.service << EOF
[Unit]
Description=Continuity Protocol Server
After=network.target

[Service]
ExecStart=$(which python) -m continuity.server.continuity_server
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=default.target
EOF

# Habilitar e iniciar o serviço
systemctl --user enable continuity-protocol.service
systemctl --user start continuity-protocol.service
```

## Integração com IDEs

### VSCode

1. Instale a extensão Continuity Protocol do VSCode Marketplace
2. Abra um projeto
3. Clique em "Iniciar Continuidade" na barra de status
4. Use o comando "Continuity: Onde Paramos?" no painel de comandos

### Integração com Amazon Q CLI

```bash
# Configure o Amazon Q CLI para usar o servidor de continuidade
q configure --mcp-server http://localhost:8765
```

### Integração com Claude Desktop

1. Abra as configurações do Claude Desktop
2. Adicione `http://localhost:8765` como servidor MCP
3. Ative o servidor "Continuity Protocol"

## Solução de Problemas

### Verificar Status

Para verificar o status do sistema:

```bash
continuity status
```

### Logs

Os logs do servidor são armazenados em:

- Windows: `%APPDATA%\Continuity\logs\`
- macOS: `~/Library/Application Support/Continuity/logs/`
- Linux: `~/.continuity/logs/`

### Problemas Comuns

1. **Servidor não inicia**
   - Verifique se a porta não está sendo usada por outro processo
   - Verifique se todas as dependências estão instaladas

2. **Erro de permissão**
   - Verifique se você tem permissão para escrever no diretório de armazenamento

3. **Integração com IDE não funciona**
   - Verifique se o servidor está em execução
   - Verifique se a configuração da IDE está correta
