# Bots para Discord

Três projetos em Python, cada um com comandos de barra, configuração própria e persistência em SQLite.

| Projeto | O que faz |
| --- | --- |
| [Moderação](discord-mod-bot/) | Advertências, consulta de histórico e timeout com verificação de cargos. |
| [Sugestões](discord-suggestions-bot/) | Sugestões, votos únicos e aprovação ou recusa pela equipe. |
| [Lembretes](discord-reminder-bot/) | Agendamento, cancelamento e novas tentativas de entrega. |

## Começar

Escolha uma pasta e siga o README dela. Requer Python 3.11 ou superior. Cada bot usa sua própria aplicação e token do Discord.

```powershell
cd discord-suggestions-bot
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
Copy-Item .env.example .env
# Preencha DISCORD_TOKEN e GUILD_ID no .env.
.venv\Scripts\python main.py
```

Os comandos aparecem com `/` no servidor. Tokens, bancos e ambientes virtuais ficam fora do repositório.

## Verificações

Há 17 testes automatizados de regras, persistência e entrega simulada. Eles não conectam ao Discord; o funcionamento em um servidor real depende de token, permissões e configuração. O workflow executa os testes de cada bot separadamente.

O [bot de moderação](https://github.com/skizyzkxx/bot-de-modera-o) também tem um repositório próprio.
