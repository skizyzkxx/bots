from datetime import timedelta
import discord
from discord import app_commands
from common import Client, data_path, run
from domain import Warnings, can_target

client = Client()
warnings = Warnings(data_path())

def target_allowed(interaction, member):
    guild = interaction.guild
    actor = interaction.user
    return bool(guild and isinstance(actor, discord.Member) and guild.me and can_target(
        actor.id, actor.top_role.position, member.id, member.top_role.position,
        guild.owner_id, guild.me.top_role.position, member.bot))

@client.tree.command(name='aviso', description='Registra uma advertência para um membro.')
@app_commands.guild_only()
@app_commands.default_permissions(moderate_members=True)
@app_commands.checks.has_permissions(moderate_members=True)
async def warn(interaction: discord.Interaction, membro: discord.Member, motivo: app_commands.Range[str,1,400]):
    if not target_allowed(interaction, membro):
        return await interaction.response.send_message('Não posso agir sobre esse membro. Confira os cargos.', ephemeral=True)
    try:
        warning_id = warnings.add(interaction.guild_id, membro.id, interaction.user.id, motivo)
    except ValueError as exc:
        return await interaction.response.send_message(str(exc), ephemeral=True)
    await interaction.response.send_message(f'Advertência #{warning_id} registrada para {membro.display_name}.', ephemeral=True)

@client.tree.command(name='avisos', description='Consulta as dez advertências ativas mais recentes.')
@app_commands.guild_only()
@app_commands.default_permissions(moderate_members=True)
@app_commands.checks.has_permissions(moderate_members=True)
async def list_warnings(interaction: discord.Interaction, membro: discord.Member):
    rows = warnings.list(interaction.guild_id, membro.id)
    text = '\n'.join(f"#{r['id']} · {r['reason'][:120]}" for r in rows) or 'Nenhuma advertência ativa.'
    await interaction.response.send_message(text, ephemeral=True)

@client.tree.command(name='remover_aviso', description='Arquiva uma advertência pelo número.')
@app_commands.guild_only()
@app_commands.default_permissions(moderate_members=True)
@app_commands.checks.has_permissions(moderate_members=True)
async def remove_warning(interaction: discord.Interaction, numero: app_commands.Range[int,1]):
    result = warnings.remove(interaction.guild_id, numero)
    await interaction.response.send_message('Advertência arquivada.' if result else 'Advertência não encontrada neste servidor.', ephemeral=True)

@client.tree.command(name='silenciar', description='Aplica timeout de 1 a 1440 minutos.')
@app_commands.guild_only()
@app_commands.default_permissions(moderate_members=True)
@app_commands.checks.has_permissions(moderate_members=True)
@app_commands.checks.bot_has_permissions(moderate_members=True)
async def timeout(interaction: discord.Interaction, membro: discord.Member, minutos: app_commands.Range[int,1,1440], motivo: app_commands.Range[str,1,400]):
    if not target_allowed(interaction, membro) or membro.guild_permissions.administrator:
        return await interaction.response.send_message('Não posso silenciar esse membro. Confira os cargos.', ephemeral=True)
    await interaction.response.defer(ephemeral=True)
    await membro.timeout(timedelta(minutes=minutos), reason=f'{interaction.user.id}: {motivo}')
    await interaction.followup.send(f'Timeout aplicado por {minutos} minuto(s).', ephemeral=True)

@client.tree.command(name='dessilenciar', description='Remove o timeout de um membro.')
@app_commands.guild_only()
@app_commands.default_permissions(moderate_members=True)
@app_commands.checks.has_permissions(moderate_members=True)
@app_commands.checks.bot_has_permissions(moderate_members=True)
async def untimeout(interaction: discord.Interaction, membro: discord.Member):
    if not target_allowed(interaction, membro):
        return await interaction.response.send_message('Não posso agir sobre esse membro.', ephemeral=True)
    await interaction.response.defer(ephemeral=True)
    await membro.timeout(None, reason=f'Removido por {interaction.user.id}')
    await interaction.followup.send('Timeout removido.', ephemeral=True)

if __name__ == '__main__':
    run(client)
