import logging
import os
from pathlib import Path

import discord
from discord import app_commands
from dotenv import load_dotenv

BASE = Path(__file__).resolve().parent
load_dotenv(BASE / ".env")
log = logging.getLogger(__name__)

class Client(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default(), allowed_mentions=discord.AllowedMentions.none())
        self.tree = app_commands.CommandTree(self)
        self.tree.on_error = self.on_command_error

    async def setup_hook(self):
        guild_id = os.getenv("GUILD_ID", "").strip()
        if guild_id:
            guild = discord.Object(id=int(guild_id))
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        else:
            await self.tree.sync()

    async def on_command_error(self, interaction, error):
        if isinstance(error, app_commands.CommandOnCooldown):
            message = f"Aguarde {error.retry_after:.0f}s antes de repetir."
        elif isinstance(error, app_commands.CheckFailure):
            message = "Você ou o bot não têm permissão para este comando."
        elif isinstance(error, app_commands.CommandInvokeError) and isinstance(error.original, discord.Forbidden):
            message = "O Discord recusou a ação. Confira as permissões e a hierarquia dos cargos."
        else:
            log.exception("Falha em comando", exc_info=(type(error), error, error.__traceback__))
            message = "Não consegui concluir. Tente novamente e confira os logs do bot."
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)

def data_path():
    path = Path(os.getenv("DATABASE_PATH", "data/bot.sqlite3"))
    if not path.is_absolute():
        path = BASE / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path

def run(client):
    token = os.getenv("DISCORD_TOKEN", "").strip()
    if not token or token == "coloque_seu_token_aqui":
        raise SystemExit("Configure DISCORD_TOKEN no .env antes de iniciar.")
    client.run(token)
