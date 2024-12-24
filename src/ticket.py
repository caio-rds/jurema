import time

import discord
from discord import Embed
from discord.ext.commands.context import Context
from discord.ui import Select, View
from discord.ext.commands import Bot
import logging

users = {}


class Ticket:
    def __init__(self, ctx: Context, bot_param: Bot):
        self.ctx = ctx
        self.bot = bot_param
        self.answers = {}
        self.channel = None

    async def ask_reason(self):
        select_reason = Select(
            custom_id='select_reason',
            placeholder='Selecione uma categoria',
            options=[
                discord.SelectOption(label='Reportar Player',
                                     emoji='👤',
                                     description='Reportar um jogador que violou as regras'),
                discord.SelectOption(label='Reportar um Bug',
                                     emoji='🐛',
                                     description='Reportar um problema que você percebeu.'),
                discord.SelectOption(label='Outros',
                                     emoji='📁',
                                     description='Outros motivos')
            ]
        )
        view = View()
        view.add_item(select_reason)
        select_reason.callback = self.my_callback
        select_embed = Embed(
            title='Criar Embed',
            description='Escolha a categoria do embed que deseja criar',
            color=0x00FF00
        )
        await self.ctx.message.author.send(embed=select_embed, view=view)

    async def my_callback(self, interaction):
        if interaction.data['custom_id'] == 'select_reason':
            self.answers['reason'] = interaction.data['values'][0]
            await interaction.message.delete()
            await self.ctx.message.author.send(f'Você escolheu {self.answers["reason"]}')
            await self.ask_situation()

    async def ask_situation(self):
        await self.ctx.message.author.send('Descreva a situação: \n(Caso seja um bug, descreva como reproduzir)')
        answer = await self.bot.wait_for('message', check=lambda message: message.author == self.ctx.author)
        if answer.content == 'cancelar':
            await self.cancel_ticket()
        if answer.content:
            self.answers['situation'] = answer.content
        await self.ask_proofs()

    async def ask_proofs(self):
        await self.ctx.message.author.send('Insira as provas: \n (prints ou vídeos que comprovem, links do youtube, imgur, drive, etc)')
        answer = await self.bot.wait_for('message', check=lambda message: message.author == self.ctx.author)
        if answer.content == 'cancelar':
            await self.cancel_ticket()
        self.answers['evidence'] = {}
        if answer.attachments:
            self.answers['evidence']['attachs'] = []
            for attachment in answer.attachments:
                self.answers['evidence']['attachs'].append(attachment.url)
        if answer.content:
            self.answers['evidence']['content'] = answer.content

        await self.create_channel()

    async def cancel_ticket(self):
        await self.ctx.message.author.send('Ticket cancelado!')
        del users[self.ctx.message.author.id]
        logging.info(f'Mensagem de {self.ctx.message.author.name} deletada.')
        await self.ctx.message.delete()

    async def create_channel(self):

        self.channel = await self.ctx.guild.create_text_channel(
            name=f"bug-{self.ctx.message.author.name}",
            category=self.ctx.guild.get_channel(1187482572146606150)
        )
        logging.info(f"Canal {self.channel.name} criado com sucesso para {self.ctx.author.name}!")
        await self.finish_ticket()

    async def finish_ticket(self):
        embed = discord.Embed(title="Ticket", description=f"Ticket de <@{self.ctx.author.id}>", color=0x71368A)
        for question, answer in self.answers.items():
            if question == 'evidence':
                embed.add_field(name=question, value=self.answers[question]['content'], inline=False)
                if self.answers[question].get('attachs'):
                    for attach in self.answers[question]['attachs']:
                        embed.add_field(name="Anexos", value=attach, inline=True)
            else:
                embed.add_field(name=question, value=answer, inline=False)
        embed.set_thumbnail(url=self.ctx.author.avatar)
        created = self.ctx.message.created_at
        embed.set_footer(text=f"Criado em {created.date()} - {created.hour}:{created.minute}:{created.second} ")
        await self.channel.send(embed=embed)
        logging.info(f"Ticket de {self.ctx.author.name} criado com sucesso!")
        await self.ctx.message.author.send(f"Ticket criado com sucesso! {self.channel.mention}")
        del users[self.ctx.message.author.id]


async def new_ticket(ctx: Context, bot: Bot):
    if str(ctx.channel.id) in '1187063751564873819':
        logging.info(f'User {ctx.message.author.name} requested creation of ticket.')
    else:
        logging.warning(f'{ctx.message.author.name} tentou criar ticket em um canal inválido: {ctx.channel.name}')
        await ctx.message.delete()
        response = await ctx.send('Você não pode enviar esse comando aqui!')
        time.sleep(5)
        await response.delete()
        return

    logging.info(f'Mensagem de {ctx.message.author.name} deletada.')
    await ctx.message.delete()

    if await ticket_exists(ctx):
        return await ctx.author.send('Você já possui um ticket aberto!')
    new = Ticket(ctx, bot)
    users[ctx.message.author.id] = new
    await new.ask_reason()


async def ticket_exists(ctx: Context):
    if users.get(ctx.message.author.id):
        return users[ctx.message.author.id]
