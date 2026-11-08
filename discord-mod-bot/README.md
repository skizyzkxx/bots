# Discord Mod Bot

Moderação com advertências persistentes e timeout. Os registros ficam separados por servidor.

## Comandos

| Comando | Uso |
| --- | --- |
| `/aviso membro motivo` | Registra uma advertência. |
| `/avisos membro` | Mostra as dez advertências ativas mais recentes. |
| `/remover_aviso numero` | Arquiva uma advertência, preservando o registro no banco. |
| `/silenciar membro minutos motivo` | Aplica timeout de 1 minuto a 24 horas. |
| `/dessilenciar membro` | Remove o timeout. |

## Permissões e comportamento

Todos os comandos exigem **Moderar membros** do operador. Para timeout, o bot também precisa dessa permissão. Dê ao bot **Ver canal** e **Enviar mensagens**, e coloque o cargo dele acima dos cargos que deverá moderar. A hierarquia é conferida pelo código e pelo Discord. O bot não age contra si mesmo, outros bots, o dono do servidor ou membros com cargo igual/superior ao operador. O dono pode moderar cargos inferiores ao bot. Administradores não podem receber timeout.

Respostas são visíveis apenas para quem executou o comando. Advertências não geram punições automáticas e não enviam mensagens privadas. O motivo de timeout e o ID do moderador aparecem no registro de auditoria do Discord; advertências ficam no SQLite. Não há banimento, expulsão nem exclusão em massa de mensagens.

## Executar localmente

Requer Python 3.11 ou superior. Cada pasta é um projeto independente e precisa de sua própria aplicação de bot no Discord.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

No Linux/macOS, use `.venv/bin/python` e `cp .env.example .env`.

1. Crie uma aplicação no [Discord Developer Portal](https://discord.com/developers/applications) e adicione um bot.
2. Preencha `DISCORD_TOKEN` no `.env`. Não publique esse arquivo.
3. Informe `GUILD_ID` com o ID do servidor de teste para sincronizar comandos apenas nele. Se ficar vazio, os comandos serão globais e podem demorar a aparecer. Ao trocar de modo, remova manualmente registros antigos para evitar comandos duplicados.
4. Em OAuth2 / URL Generator, selecione `bot` e `applications.commands`, escolha as permissões listadas abaixo e convide o bot para um servidor que você administra.
5. Execute:

```powershell
.venv\Scripts\python main.py
```

Os comandos são de barra (`/`). Não é necessário habilitar os intents privilegiados de conteúdo de mensagens, presença ou membros. O bot não lê conversas para responder a comandos.

## Dados e hospedagem

O arquivo `data/bot.sqlite3` é criado automaticamente. `DATABASE_PATH` aceita um caminho relativo à pasta do projeto ou um caminho absoluto. Guarde a pasta `data/` em disco persistente e faça backup; não a envie para o GitHub. O banco contém IDs e conteúdo dos comandos usados. Limite o acesso à máquina e ao banco.

Execute uma única instância por token e banco. Um VPS ou serviço com processo Python contínuo e volume persistente é suficiente. O bot para quando o processo é encerrado; GitHub Pages não executa bots. Use variáveis de ambiente na hospedagem para o token.

## Testes

```powershell
.venv\Scripts\python -m unittest discover -s tests -v
```

Os testes verificam as regras e a persistência usando bancos temporários. Não conectam ao Discord. A execução em um servidor real ainda requer seu token e uma verificação das permissões. O workflow do GitHub executa a suíte automaticamente em pushes e pull requests.

## Arquivos

- `main.py`: comandos e integração com Discord.
- `domain.py`: regras e consultas do projeto.
- `storage.py`: conexão e transações SQLite.
- `common.py`: configuração, sincronização e mensagens de erro.
- `tests/`: testes locais sem token.

## Referência

Biblioteca: [discord.py](https://discordpy.readthedocs.io/en/stable/). Os arquivos `.env`, bancos e ambientes virtuais ficam fora do controle de versão.
