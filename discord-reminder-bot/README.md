# Discord Reminder Bot

Lembretes agendados em canais de texto, com persistência, cancelamento e novas tentativas de envio.

## Comandos

| Comando | Uso |
| --- | --- |
| `/lembrar minutos texto` | Agenda no canal atual, entre 1 minuto e 30 dias. |
| `/lembretes` | Lista seus lembretes ativos no servidor. |
| `/cancelar numero` | Cancela um lembrete seu antes de entrar em envio. |

Exemplo: `/lembrar minutos:30 texto:Revisar o exercício de Python`.

## Permissões e comportamento

O bot precisa de **Ver canal** e **Enviar mensagens**. Use canais de texto comuns; threads e mensagens privadas não são aceitas. Cada pessoa pode ter até 20 lembretes ativos por servidor. A lista e a confirmação são privadas; o aviso final é **público no canal original** e menciona apenas seu autor. O conteúdo do texto não pode notificar outros membros, cargos ou `@everyone`.

O processo consulta lembretes a cada 15 segundos. Se ficar offline, os lembretes vencidos serão processados quando voltar. Entregas podem atrasar; não use para compromissos críticos. O autor precisa continuar no servidor e com acesso ao canal na hora do envio.

Falhas temporárias têm até cinco tentativas, com espera crescente. Canal apagado, falta de permissão ou saída do autor encerram o envio. Após uma queda durante o envio, a tarefa fica disponível novamente em cinco minutos. Existe uma pequena possibilidade de envio duplicado se o processo cair entre publicar a mensagem e registrar a conclusão. Não há garantia de entrega exatamente uma vez. Lembretes concluídos ou com falha continuam no banco; `/lembretes` mostra somente ativos.

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
