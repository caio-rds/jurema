import asyncio
import logging
import os

import discord
from aiohttp import web
from aiohttp.web_request import Request
from discord.ext import commands
from discord.ext.commands import CommandNotFound
from discord.ext.commands.context import Context

from src.embed import EmbedMessage
from src.ticket import new_ticket


intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

allowed_channels = ['1179955774118690847', '1187063580084928572']

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S',
                    encoding='utf-8')


async def start_app():

    @bot.event
    async def on_ready():
        logging.info(f'{bot.user} Is Online!')
        logging.info(f'Used in {len(bot.guilds)} servers, servers: {[server.name for server in bot.guilds]}')

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, CommandNotFound):
            await ctx.message.delete()
            logging.warning(f'User {ctx.message.author.name} tentou usar um comando que não existe.')
            return
        raise error

    @bot.event
    async def on_member_exit(member):
        logging.info(f'User {member.name} left the server.')

    @bot.event
    async def on_raw_reaction_add(payload):
        if payload.message_id == 1196616657255288972:
            if payload.emoji.name == '👍':
                guild = bot.get_guild(payload.guild_id)
                member = guild.get_member(payload.user_id)
                role = discord.utils.get(guild.roles, name='Membro')
                if role:
                    await member.add_roles(role)
                    logging.info(f'User {member.name} added role {role.name}.')
                    return
                logging.error(f'Role {role.name} not found')


    @bot.event
    async def on_raw_reaction_remove(payload):
        if payload.message_id == 1196616657255288972:
            if payload.emoji.name == '👍':
                guild = bot.get_guild(payload.guild_id)
                member = guild.get_member(payload.user_id)
                role = discord.utils.get(guild.roles, name='Membro')
                if role:
                    await member.remove_roles(role)
                    logging.info(f'User {member.name} removed role {role.name}.')
                    return
                logging.error(f'Role {role.name} not found')

    @bot.command(name='ticket')
    async def create_ticket(ctx: Context):
        await new_ticket(ctx=ctx, bot=bot)

    @bot.command(name='clear')
    async def clear(ctx: Context, amount: int):
        if ctx.message.author.guild_permissions.administrator:
            logging.info(f'User {ctx.message.author.name} cleared {amount} messages.')
            await ctx.channel.purge(limit=amount)
        else:
            logging.warning(f'User {ctx.message.author.name} tried to clear {amount} messages,'
                            f' but does not have permission.')
            await ctx.send('Você não tem permissão para usar este comando.', delete_after=10)
            await ctx.message.delete()

    @bot.command(name='embed')
    async def embed(ctx: Context):
        await EmbedMessage(ctx=ctx, bot=bot).new_message()

    await bot.start(os.getenv('TOKEN'))

async def handle_options(request: Request):
    return web.Response(headers={
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    })

@web.middleware
async def cors_middleware(request, handler):
    response = await handler(request)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Access-Control-Allow-Headers, access-control-allow-origin'
    return response

async def handle(request: Request):
    data = await request.json()
    if data.get('discord_id'):
        try:
            user = await bot.fetch_user(data.get('discord_id'))
            if user:
                embed_message = discord.Embed(title='Código de Verificação', description=f'Olá, {user.name}! Você está recebendo seu código.', color=0x00ff00)
                embed_message.set_thumbnail(url='https://cdn.discordapp.com/attachments/119661124660731907/1196611246607319071/1196611246607319071.png')
                embed_message.add_field(name='Código:', value=data.get('code'), inline=False)
                embed_message.set_footer(text='Insira o código no FiveM.')
                await user.send(embed=embed_message)
                logging.info(f'Mensagem enviada para usuário {data.get("discord_id")}.')
                return web.Response(text=f'Mensagem enviada para {user.name}.', status=200)

            return web.Response(text='Usuário não encontrado.')
        except discord.NotFound:
            logging.error(f"Usuário com ID {data.get('discord_id')} não foi encontrado.")
            return web.Response(text='Usuário não encontrado.', status=404)
        except discord.Forbidden:
            logging.error(f"Não foi possível enviar mensagem para o usuário {data.get('discord_id')} (bloqueado ou sem permissões).")
            return web.Response(text='Não foi possível enviar mensagem.', status=403)
        except Exception as e:
            logging.error(f"Erro inesperado: {e}")
            return web.Response(text='Erro interno.', status=500)
    return web.Response(text='Erro ao enviar mensagem: discord_id não fornecido.', status=400)

async def start_wh():
    logging.info('Starting webhook...')
    app = web.Application()
    app.router.add_post('/webhook', handle)
    app.router.add_options('/webhook', handle_options)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, port=5000)
    await site.start()


async def main():
    asyncio.create_task(start_wh())
    await start_app()
#
# try:
#     public_ip = requests.get('https://api.ipify.org').text
#     print(f"Public IP Address: {public_ip}")
# except requests.RequestException as e:
#     print(f"Error retrieving public IP address: {e}")

if __name__ == '__main__':
    asyncio.run(main())

# 1196611246607319071
