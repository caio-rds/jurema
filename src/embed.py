import time
import discord
from discord import Embed
from discord.ext.commands.context import Context
from discord.ui import Select, View
from discord.ext.commands import Bot
import logging

embed_category = {
    'warning': {
        'color': 0xC91C28,
    },
    'links': {
        'color': 0x9A13D4,
    },
    'tutorial': {
        'color': 0xD2E010
    }
}


class EmbedMessage:
    def __init__(self, ctx: Context, bot: Bot):
        self.ctx = ctx
        self.bot = bot
        self.description = None
        self.title = None
        self.category = None

    async def cancel_embed(self):
        await self.ctx.send('Cancelado!', delete_after=10)
        await self.ctx.channel.purge(limit=1)
        logging.info(f'User {self.ctx.message.author.name} canceled embed creation.')
        return

    async def new_message(self):
        """Create a new message embed."""
        logging.info(f'User {self.ctx.message.author.name} requested a new embed.')
        await self.ctx.message.delete()
        category = Select(
            custom_id='select_category',
            placeholder='Selecione uma categoria',
            options=[
                discord.SelectOption(label='Aviso',
                                     emoji='⚠️',
                                     value='warning',
                                     description='Avisos importantes'),
                discord.SelectOption(label='Links',
                                     emoji='🔗',
                                     value='links',
                                     description='Links importantes'),
                discord.SelectOption(label='Tutorial',
                                     emoji='👍',
                                     value='tutorial',
                                     description='Tutoriais')
            ]
        )

        view = View()
        view.add_item(category)
        category.callback = self.embed_callback
        select_embed = Embed(
            title='Criar Embed',
            description='Escolha a categoria do embed que deseja criar',
            color=0x00FF00
        )
        await self.ctx.send(embed=select_embed, view=view)

    async def embed_callback(self, interaction):
        questions = {
            'title': 'Qual o título do Embed ?',
            'description': 'Qual a descrição do Embed ?'
        }
        if interaction.data['custom_id'] == 'select_category':
            logging.info(f'User {self.ctx.message.author.name} selected {interaction.data["values"][0]} category.')
            self.category = interaction.data['values'][0]
            await interaction.message.delete()
            for quest, text in questions.items():
                ask = await self.ctx.send(text)
                answer = await self.bot.wait_for('message',
                                                 check=lambda message: message.author == self.ctx.author,
                                                 timeout=300)
                if quest == 'title':
                    self.title = answer.content
                elif quest == 'description':
                    self.description = answer.content
                await ask.delete()
                await answer.delete()
            if self.title is None or self.description is None:
                await self.cancel_embed()
                return
            logging.info(f'User {self.ctx.message.author.name} answered questions.')
            await self.finish_embed()

    async def finish_embed(self):
        my_embed = Embed(
            title=self.title,
            description=self.description,
            color=embed_category[self.category]['color']
        )
        #my_embed.set_thumbnail(url=self.ctx.guild.icon.url)
        my_embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar)
        my_embed.set_footer(
            text=f'Criado em: {self.ctx.message.created_at.date()} -'
                 f' {self.ctx.message.created_at.hour}:'
                 f'{self.ctx.message.created_at.minute}:'
                 f'{self.ctx.message.created_at.second}'
        )
        message = await self.ctx.send(embed=my_embed)
        logging.info(f'User {self.ctx.message.author.name} created a new embed.')
        if self.category == 'warning':
            await message.add_reaction('⚠️')
        elif self.category == 'tutorial':
            await message.add_reaction('👍')
        elif self.category == 'links':
            await message.add_reaction('🔗')
