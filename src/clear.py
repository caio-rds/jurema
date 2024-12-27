import time
import discord
from discord import Embed
from discord.ext.commands.context import Context
from discord.ui import Select, View
from discord.ext.commands import Bot
import logging

async def clear(ctx: Context, amount=5):
    if ctx.message.author.guild_permissions.administrator:
        logging.info(f'User {ctx.message.author.name} cleared {amount} messages.')
        await ctx.channel.purge(limit=amount+1)
        await ctx.send(f'Removido as {amount} ultimas mensagens.', delete_after=10)
    else:
        logging.warning(f'User {ctx.message.author.name} tried to clear {amount} messages,'
                        f' but does not have permission.')
        await ctx.send('Você não tem permissão para usar este comando.', delete_after=10)
        await ctx.message.delete()