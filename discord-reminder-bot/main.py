import logging
import discord
from discord import app_commands
from discord.ext import tasks
from common import Client, data_path, run
from domain import Reminders

log=logging.getLogger(__name__)
reminders=Reminders(data_path())

class ReminderClient(Client):
    async def setup_hook(self):
        await super().setup_hook()
        self.deliver.start()

    async def close(self):
        self.deliver.cancel()
        await super().close()

    @tasks.loop(seconds=15)
    async def deliver(self):
        for _ in range(20):
            row=reminders.claim()
            if not row: break
            try:
                channel=self.get_channel(row['channel']) or await self.fetch_channel(row['channel'])
                if not isinstance(channel,discord.TextChannel) or channel.guild.id != row['guild']:
                    reminders.finish(row['id'],False,permanent=True)
                    continue
                member=await channel.guild.fetch_member(row['author'])
                if not channel.permissions_for(member).view_channel:
                    reminders.finish(row['id'],False,permanent=True)
                    continue
                text=discord.utils.escape_mentions(discord.utils.escape_markdown(row['text']))
                await channel.send(f"<@{row['author']}> Lembrete #{row['id']}: {text}",
                    allowed_mentions=discord.AllowedMentions(users=[discord.Object(id=row['author'])],roles=False,everyone=False,replied_user=False))
            except (discord.NotFound,discord.Forbidden):
                reminders.finish(row['id'],False,permanent=True)
            except discord.HTTPException:
                reminders.finish(row['id'],False)
            except Exception:
                log.exception('Falha ao entregar lembrete %s',row['id'])
                reminders.finish(row['id'],False)
            else:
                reminders.finish(row['id'],True)

    @deliver.before_loop
    async def before_deliver(self):
        await self.wait_until_ready()

client=ReminderClient()

@client.tree.command(name='lembrar',description='Agenda um lembrete no canal atual, de 1 minuto a 30 dias.')
@app_commands.guild_only()
@app_commands.checks.cooldown(1,5,key=lambda i:(i.guild_id,i.user.id))
@app_commands.checks.bot_has_permissions(send_messages=True)
async def create(interaction: discord.Interaction,minutos: app_commands.Range[int,1,43200],texto: app_commands.Range[str,1,500]):
    if not isinstance(interaction.channel,discord.TextChannel):
        return await interaction.response.send_message('Use um canal de texto comum, fora de threads.',ephemeral=True)
    try:
        number=reminders.create(interaction.guild_id,interaction.channel_id,interaction.user.id,texto,minutos)
    except ValueError as exc:
        return await interaction.response.send_message(str(exc),ephemeral=True)
    await interaction.response.send_message(f'Lembrete #{number} agendado para daqui a {minutos} minuto(s), neste canal. O aviso será público e o bot precisa estar online.',ephemeral=True)

@client.tree.command(name='lembretes',description='Lista seus lembretes ativos neste servidor.')
@app_commands.guild_only()
async def listing(interaction: discord.Interaction):
    rows=reminders.list(interaction.guild_id,interaction.user.id)
    text='\n'.join(f"#{r['id']} · <t:{int(r['due'])}:R> · {discord.utils.escape_markdown(r['text'][:45])}" for r in rows) or 'Nenhum lembrete ativo.'
    await interaction.response.send_message(text[:1900],ephemeral=True)

@client.tree.command(name='cancelar',description='Cancela um lembrete seu que ainda não entrou em envio.')
@app_commands.guild_only()
async def cancel(interaction: discord.Interaction,numero: app_commands.Range[int,1]):
    ok=reminders.cancel(interaction.guild_id,interaction.user.id,numero)
    await interaction.response.send_message('Lembrete cancelado.' if ok else 'Lembrete não encontrado, já enviado ou em envio.',ephemeral=True)

if __name__ == '__main__':
    run(client)
