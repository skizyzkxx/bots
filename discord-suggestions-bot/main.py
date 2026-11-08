import discord
from discord import app_commands
from common import Client, data_path, run
from domain import Suggestions

client = Client()
suggestions = Suggestions(data_path())

def render(row):
    embed = discord.Embed(title=f"Sugestão #{row['id']}", description=discord.utils.escape_markdown(row['text']), color=0xEEEEEE)
    embed.add_field(name='Situação',value=row['status'])
    embed.add_field(name='Votos',value=f"{row['yes']} a favor · {row['no']} contra")
    embed.set_footer(text=f"Use /votar numero:{row['id']} e /sugestao para consultar o placar atualizado.")
    return embed

@client.tree.command(name='sugerir', description='Envia uma sugestão para a comunidade no canal atual.')
@app_commands.guild_only()
@app_commands.checks.cooldown(1,30,key=lambda i:(i.guild_id,i.user.id))
@app_commands.checks.bot_has_permissions(send_messages=True,embed_links=True)
async def suggest(interaction: discord.Interaction, texto: app_commands.Range[str,5,1000]):
    try:
        number = suggestions.create(interaction.guild_id,interaction.user.id,texto)
    except ValueError as exc:
        return await interaction.response.send_message(str(exc),ephemeral=True)
    row = suggestions.get(interaction.guild_id,number)
    await interaction.response.send_message(embed=render(row))

@client.tree.command(name='votar', description='Registra ou altera seu voto em uma sugestão aberta.')
@app_commands.guild_only()
@app_commands.choices(voto=[app_commands.Choice(name='A favor',value=1),app_commands.Choice(name='Contra',value=-1)])
async def vote(interaction: discord.Interaction, numero: app_commands.Range[int,1], voto: app_commands.Choice[int]):
    ok = suggestions.vote(interaction.guild_id,numero,interaction.user.id,voto.value)
    await interaction.response.send_message('Voto registrado. Use /sugestao para ver o placar.' if ok else 'Sugestão não encontrada neste servidor ou já encerrada.',ephemeral=True)

@client.tree.command(name='sugestao', description='Consulta o placar e a situação de uma sugestão.')
@app_commands.guild_only()
async def show(interaction: discord.Interaction, numero: app_commands.Range[int,1]):
    row = suggestions.get(interaction.guild_id,numero)
    if not row:
        return await interaction.response.send_message('Sugestão não encontrada neste servidor.',ephemeral=True)
    await interaction.response.send_message(embed=render(row),ephemeral=True)

@client.tree.command(name='decidir', description='Aprova ou recusa uma sugestão aberta.')
@app_commands.guild_only()
@app_commands.default_permissions(manage_guild=True)
@app_commands.checks.has_permissions(manage_guild=True)
@app_commands.choices(decisao=[app_commands.Choice(name='Aprovar',value='aprovada'),app_commands.Choice(name='Recusar',value='recusada')])
async def decide(interaction: discord.Interaction, numero: app_commands.Range[int,1], decisao: app_commands.Choice[str]):
    ok = suggestions.decide(interaction.guild_id,numero,decisao.value)
    await interaction.response.send_message('Decisão registrada. Consulte /sugestao para ver a situação atual.' if ok else 'Sugestão não encontrada neste servidor ou já encerrada.',ephemeral=True)

if __name__ == '__main__':
    run(client)
