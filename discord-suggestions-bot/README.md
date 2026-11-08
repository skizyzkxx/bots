# Discord Suggestions Bot

Sugestões de comunidade com votação e decisão da equipe. O histórico e os votos ficam em SQLite.

## Comandos

| Comando | Uso |
| --- | --- |
| `/sugerir texto` | Publica uma sugestão no canal atual. |
| `/votar numero voto` | Vota a favor ou contra. Repetir altera o voto, sem duplicá-lo. |
| `/sugestao numero` | Consulta o placar e a situação atuais. |
| `/decidir numero decisao` | Aprova ou recusa; exige **Gerenciar servidor**. |

## Permissões e comportamento

O bot precisa de **Ver canal**, **Enviar mensagens** e **Inserir links** para os embeds. Sugestões têm entre 5 e 1000 caracteres, com intervalo de 30 segundos por pessoa e servidor. Votos e consultas ficam restritos ao mesmo servidor; um voto por pessoa e sugestão. Uma decisão encerra a votação.

A publicação inicial é pública. Ela não é editada a cada voto: use `/sugestao` para consultar o placar atualizado. As consultas, votos e confirmações de decisão são visíveis somente para quem usou o comando. Não há anonimato: o banco guarda o ID do autor e dos votantes, embora o placar mostre somente contagens. Menções no conteúdo não notificam pessoas ou cargos.

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
