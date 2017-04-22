import discord
from discord.ext import commands
from __main__ import send_cmd_help
from cogs.utils.dataIO import dataIO

# Requires checks utility from:
# https://github.com/Rapptz/RoboDanny/tree/master/cogs/utils
from .utils import checks

import os #Used to create folder at first load.

#Global variables

saveFolder = "data/lui-cogs/welcome/" #Path to save folder.
saveFile = "settings.json"
welcomeDefault_message = "Welcome to the server! Hope you enjoy your stay!"
welcomeDefault_title = "Welcome!"

def checkFolder():
    """Used to create the data folder at first startup"""
    if not os.path.exists(saveFolder):
        print("Creating " + saveFolder + " folder...")
        os.makedirs(saveFolder)

def checkFiles():
    """Used to initialize an empty database at first startup"""
    
    f = saveFolder + saveFile
    if not dataIO.is_valid_json(f):
        print("Creating default welcome settings.json...")
        dataIO.save_json(f, { "message" : "Welcome to the server!" })
        
            
class Welcome_beta:
    """Send a welcome DM on server join."""


    def loadSettings(self):
        """Loads settings from the JSON file"""
        self.settings = dataIO.load_json(saveFolder+saveFile)
        
    def saveSettings(self):
        """Loads settings from the JSON file"""
        dataIO.save_json(saveFolder+saveFile, self.settings)

    #Class constructor
    def __init__(self, bot):
        self.bot = bot
        checkFolder()
        checkFiles()
        self.loadSettings()
        
    #The async function that is triggered on new member join.
    async def send_welcome_message(self, newUser):
        """Sends the welcome message in DM."""
        #Get Channel object. Hard-coding for now.
        loggerID = "303321990792609792" #log
        
        #Do not send DM if it is disabled!
        if not self.settings[newUser.server.id]["welcomeDMEnabled"]:
            return
            
        try:
            welcomeEmbed = discord.Embed(title=self.settings[newUser.server.id]["welcomeTitle"])
            welcomeEmbed.description = self.settings[newUser.server.id]["welcomeMessage"]
            welcomeEmbed.colour = discord.Colour.red()
            await self.bot.send_message(newUser, embed=welcomeEmbed)
        except Exception as errorMsg:
            print("Server Welcome: Could not send message, make sure the server has a title and message set!")
            print(errorMsg)
            if self.settings[newUser.server.id]["welcomeLogEnabled"]:
                await self.bot.send_message(self.bot.get_channel(loggerID), "Server Welcome: Could not send message, make sure the server has a title and message set!")
                await self.bot.send_message(self.bot.get_channel(loggerID), errorMsg)
        else:
            if self.settings[newUser.server.id]["welcomeLogEnabled"]:
                await self.bot.send_message(self.bot.get_channel(loggerID), "Server Welcome: Welcome DM sent to " + newUser.name + "#" + newUser.discriminator + " (" + newUser.id + ").")
                print("Server Welcome: Welcome DM sent to " + newUser.name + "#" + newUser.discriminator + " (" + newUser.id + ").")
    
    #The async function that is triggered on member leave.
    async def send_leave_message(self, leavingUser):
        """Sends the server leave message in the console."""
        #Get Channel object. Hard-coding for now.
        loggerID = "303321990792609792" #log
        
        print("Server Leave: " + leavingUser.name + "#" + leavingUser.discriminator + " (" + leavingUser.id + ") has left")
        await self.bot.send_message(self.bot.get_channel(loggerID), "Server Leave: " + leavingUser.name + "#" + leavingUser.discriminator + " (" + leavingUser.id + ") has left")
    
    ####################
    # MESSAGE COMMANDS #
    ####################
    
    #[p]welcome
    @commands.group(name="welcome", pass_context=True, no_pm=False)
    @checks.serverowner() #Only allow server owner to execute the following command.
    async def _welcome(self, ctx):
        """Server welcome message settings."""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            
    #[p]welcome setmessage
    @_welcome.command(pass_context=True, no_pm=False)
    @checks.serverowner() #Only allow server owner to execute the following command.
    async def setmessage(self, ctx):
        """Interactively configure the contents of the welcome DM."""
        
        await self.bot.say("What would you like the welcome DM message to be?")
        message = await self.bot.wait_for_message(timeout=60, author=ctx.message.author, channel=ctx.message.channel)
        
        if message is None:
            await self.bot.say("No response received, not setting anything!")
            return
            
        if len(message.content) > 2048:
            await self.bot.say("Your message is too long!")
            return
        
        try:
            self.loadSettings()
            if ctx.message.author.server.id in self.settings:
                self.settings[ctx.message.author.server.id]["welcomeMessage"] = message.content
            else:
                self.settings[ctx.message.author.server.id] = {}
                self.settings[ctx.message.author.server.id]["welcomeMessage"] = message.content
            self.saveSettings()
        except Exception as errorMsg:
            await self.bot.say("Could not save settings! Check the console for details.")
            print(errorMsg)
        else:
            await self.bot.say("Message set to:")
            await self.bot.say("```" + message.content + "```")

    #[p]welcome toggledm
    @_welcome.command(pass_context=True, no_pm=False)
    @checks.serverowner() #Only allow server owner to execute the following command.
    async def toggledm(self, ctx):
        """Toggle sending a welcome DM."""
        key = "welcomeDMEnabled"
        self.loadSettings()
        try:
            if self.settings[ctx.message.author.server.id][key] is True:
                self.settings[ctx.message.author.server.id][key] = False
                set = False
            else:
                self.settings[ctx.message.author.server.id][key] = True
                set = True
        except: #Typically a KeyError
            self.settings[ctx.message.author.server.id][key] = True
            set = True
        self.saveSettings()
        if set:
            await self.bot.say(":white_check_mark: Server welcome DM enabled.")
        else:
            await self.bot.say(":negative_squared_cross_mark: Server welcome DM disabled.")
    #[p]welcome togglelog
    @_welcome.command(pass_context=True, no_pm=False)
    @checks.serverowner() #Only allow server owner to execute the following command.
    async def togglelog(self, ctx):
        """Toggle sending welcome DM logs to a channel."""
        key = "welcomeLogEnabled"
        self.loadSettings()
        try:
            if self.settings[ctx.message.author.server.id][key] is True:
                self.settings[ctx.message.author.server.id][key] = False
                set = False
            else:
                self.settings[ctx.message.author.server.id][key] = True
                set = True
        except: #Typically a KeyError
            self.settings[ctx.message.author.server.id][key] = True
            set = True
        self.saveSettings()
        if set:
            await self.bot.say(":white_check_mark: Server welcome DM logs enabled.")
        else:
            await self.bot.say(":negative_squared_cross_mark: Server welcome DM logs disabled.")
        
        
    #[p]welcome default
    @_welcome.command(pass_context=True, no_pm=False)
    @checks.serverowner() #Only allow server owner to execute the following command.
    async def default(self, ctx):
        """Revert to default, and enables welcome DM.  Will ask for confirmation."""
        await self.bot.say("Are you sure you want to revert to default settings? Type \"yes\", otherwise type something else.")
        message = await self.bot.wait_for_message(timeout=60,author=ctx.message.author, channel=ctx.message.channel)
        
        if message is None:
            await self.bot.say(":no_entry: No response received, aborting.")
            return
        
        if str.lower(message.content) == "yes":
            try:
                self.loadSettings()
                self.settings[ctx.message.author.server.id] = {}
                self.settings[ctx.message.author.server.id]["welcomeMessage"] = welcomeDefault_message
                self.settings[ctx.message.author.server.id]["welcomeTitle"] = welcomeDefault_title
                self.settings[ctx.message.author.server.id]["welcomeDMEnabled"] = True
                self.settings[ctx.message.author.server.id]["welcomeLogEnabled"] = False
                self.settings[ctx.message.author.server.id]["welcomeLogChannel"] = None
                self.saveSettings()
            except Exception as e:
                await self.bot.say(":no_entry: Could not set default settings! Please check the server logs.")
                print(e)
            else:
                await self.bot.say(":white_check_mark: Default settings applied.")
        else:
            await self.bot.say(":negative_squared_cross_mark: Not setting any default settings.")
        
        
    #[p]welcome settitle
    @_welcome.command(pass_context=True, no_pm=False)
    @checks.serverowner() #Only allow server owner to execute the following command.
    async def settitle(self, ctx):
        """Interactively configure the title for the welcome DM."""
        
        await self.bot.say("What would you like the welcome DM message to be?")
        title = await self.bot.wait_for_message(timeout=60, author=ctx.message.author, channel=ctx.message.channel)
        
        if title is None:
            await self.bot.say("No response received, not setting anything!")
            return
            
        if len(title.content) > 256:
            await self.bot.say("The title is too long!")
            return
        
        try:
            self.loadSettings()
            if ctx.message.author.server.id in self.settings:
                self.settings[ctx.message.author.server.id]["welcomeTitle"] = title.content
            else:
                self.settings[ctx.message.author.server.id] = {}
                self.settings[ctx.message.author.server.id]["welcomeTitle"] = title.content
            self.saveSettings()
        except:
            await self.bot.say("Could not save settings!")
        else:
            await self.bot.say("Title set to:")
            await self.bot.say("```" + title.content + "```")
    #[p]welcome test
    @_welcome.command(pass_context=True, no_pm=False)
    @checks.serverowner() #Only allow server owner to execute the following command.
    async def test(self, ctx):
        """Test the welcome DM by sending a DM to you."""
        try:
            welcomeEmbed = discord.Embed(title=self.settings[ctx.message.server.id]["welcomeTitle"])
            welcomeEmbed.description = self.settings[ctx.message.author.server.id]["welcomeMessage"]
            welcomeEmbed.colour = discord.Colour.red()
        except:
            await self.bot.say("Could not send message, try setting the title and message again!")
        else:
            await self.bot.send_message(ctx.message.author, embed=welcomeEmbed)
            await self.bot.say("I've slid it into your DMs ;)")
               

def setup(bot):
    checkFolder()   #Make sure the data folder exists!
    checkFiles()    #Make sure we have settings!
    customCog = Welcome_beta(bot)
    bot.add_listener(customCog.send_welcome_message, 'on_member_join')
    bot.add_listener(customCog.send_leave_message, 'on_member_remove')
    bot.add_cog(customCog)
    
