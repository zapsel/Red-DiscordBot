from discord.ext import commands
from cogs.utils.dataIO import dataIO
from .utils import checks
import os

class Geordiespeak:
    def __init__(self, bot):
        self.bot = bot
        self.geordie = dataIO.load_json('data/downloader/paddo-cogs/geordiespeal/data/geordie.json')
        self.data = dataIO.load_json('data/geordiespeak/settings.json')

    @commands.command(pass_context=True, no_pm=True, name='geordietoggle')
    @checks.mod_or_permissions(administrator=True)
    async def _geordietoggle(self, context):
        server = context.message.server
        if server.id not in self.data:
            self.data[server.id] = True
        elif self.data[server.id]:
            self.data[server.id] = False
            await self.bot.say('Geordie Speak disabled')
        else:
            self.data[server.id] = True
            await self.bot.say('Geordie Speak enabled')
        dataIO.save_json('data/geordiespeak/settings.json', self.data)

    async def _translator(self, english):
        geordie = ''
        english = english.split(' ')
        for word in english:
            before = ''
            after =''
            c = ['.',',','!','?',';','*','```','(',')','[',']']
            if word:
                if word[0] in c:
                    before = word[0]
                    word = word[1:]
                if word[-1] in c:
                    after = word[-1]
                    word = word[:-1]
                if word.lower() in self.geordie:
                    word = self.geordie[word.lower()]
                word = before+word+after
                if word.istitle():
                    word = word.title()
                geordie+=word+' '
        return geordie

    async def listener(self, message):
        content = message.content
        server = message.server
        author = message.author
        if server.id in self.data and self.data[server.id]:
            if author.id == self.bot.user.id:
                await self.bot.edit_message(message, await self._translator(content))

def check_folder():
    if not os.path.exists('data/geordiespeak'):
        os.makedirs('data/geordiespeak')

def check_file():
    f = 'data/geordiespeak/settings.json'
    if dataIO.is_valid_json(f) is False:
        dataIO.save_json(f, {})

def setup(bot):
    check_folder()
    check_file()
    n = Geordiespeak(bot)
    bot.add_listener(n.listener, "on_message")
    bot.add_cog(n)
