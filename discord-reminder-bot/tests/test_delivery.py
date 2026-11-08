import os
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
import discord

IMPORT_TEMP = tempfile.TemporaryDirectory()
previous_path = os.environ.get('DATABASE_PATH')
os.environ['DATABASE_PATH'] = str(Path(IMPORT_TEMP.name)/'import.sqlite3')
import main
if previous_path is None:
    os.environ.pop('DATABASE_PATH',None)
else:
    os.environ['DATABASE_PATH']=previous_path
from domain import Reminders

def tearDownModule():
    IMPORT_TEMP.cleanup()

class DeliveryTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db=Reminders(Path(self.temp.name)/'test.sqlite3')
        self.channel=MagicMock(spec=discord.TextChannel)
        self.channel.guild.id=1
        self.channel.guild.fetch_member=AsyncMock(return_value=MagicMock())
        self.channel.permissions_for.return_value=SimpleNamespace(view_channel=True)
        self.channel.send=AsyncMock()
        self.number=self.db.create(1,2,3,'Revisar @everyone',1,now=time.time()-120)

    async def deliver(self):
        with patch.object(main,'reminders',self.db),patch.object(main.client,'get_channel',return_value=self.channel):
            await main.client.deliver.coro(main.client)

    async def test_delivery_mentions_only_author_and_finishes(self):
        await self.deliver()
        self.channel.send.assert_awaited_once()
        call=self.channel.send.call_args
        self.assertIn('<@3>',call.args[0])
        self.assertNotIn('@everyone',call.args[0])
        mentions=call.kwargs['allowed_mentions'].to_dict()
        self.assertEqual(mentions['users'],[3])
        self.assertEqual(mentions['parse'],[])
        self.assertEqual(self.db.list(1,3),[])

    async def test_revoked_channel_access_prevents_delivery(self):
        self.channel.permissions_for.return_value.view_channel=False
        await self.deliver()
        self.channel.send.assert_not_awaited()
        self.assertEqual(self.db.list(1,3),[])

    async def test_transient_http_failure_keeps_reminder_for_retry(self):
        self.channel.send.side_effect=discord.HTTPException(SimpleNamespace(status=503,reason='Unavailable'),'Retry later')
        await self.deliver()
        row=self.db.list(1,3)[0]
        self.assertEqual(row['status'],'pending')
        self.assertEqual(row['attempts'],1)

    async def test_wrong_guild_never_receives_reminder(self):
        self.channel.guild.id=99
        await self.deliver()
        self.channel.send.assert_not_awaited()
