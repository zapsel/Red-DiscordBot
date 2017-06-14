#Duplicate of Scenery cog except for scenery.


import discord
from discord.ext import commands
from __main__ import send_cmd_help
from cogs.utils.dataIO import dataIO
import os #Used to create folder at first load.
import random #Used for selecting random scenery

#Global variables
JSON_mainKey = "scenery" #Key for JSON files.
JSON_imageURLKey = "url" #Key for URL
JSON_isPixiv = "is_pixiv" #Key that specifies if image is from pixiv. If true, pixivID should be set.
JSON_pixivID = "id" #Key for Pixiv ID, used to create URL to pixiv image page, if applicable.
saveFolder = "data/lui-cogs/scenery/" #Path to save folder.

def checkFolder():
    """Used to create the data folder at first startup"""
    if not os.path.exists(saveFolder):
        print("Creating " + saveFolder + " folder...")
        os.makedirs(saveFolder)

def checkFiles():
    """Used to initialize an empty database at first startup"""
    base = { JSON_mainKey : [{ JSON_imageURLKey :"https://cdn.awwni.me/utpd.jpg" , "id" : "null", "is_pixiv" : False}]}
    empty = { JSON_mainKey : []}
    
    f = saveFolder + "links-web.json"
    if not dataIO.is_valid_json(f):
        print("Creating default Scenery links-web.json...")
        dataIO.save_json(f, base)
        
    f = saveFolder + "links-localx10.json"
    if not dataIO.is_valid_json(f):
        print("Creating default Scenery links-localx10.json...")
        dataIO.save_json(f, empty)
        
    f = saveFolder + "links-local.json"
    if not dataIO.is_valid_json(f):
        print("Creating default Scenery links-local.json...")
        dataIO.save_json(f, empty)
        
    f = saveFolder + "links-pending.json"
    if not dataIO.is_valid_json(f):
        print("Creating default Scenery links-pending.json...")
        dataIO.save_json(f, empty)
            
class Scenery_beta:
    """Display cute nyaas~"""


    def refreshDatabase(self):
        """Refreshes the JSON files"""
        #Local scenery allow for prepending predefined domain, if you have a place where you're hosting your own scenery.
        self.filepath_local = saveFolder + "links-local.json"
        self.filepath_localx10 = saveFolder + "links-localx10.json"
        
        #Web scenery will take on full URLs.
        self.filepath_web = saveFolder + "links-web.json"

        #List of pending scenery waiting to be added.
        self.filepath_pending = saveFolder + "links-pending.json"
        
        #scenery
        self.pictures_local = dataIO.load_json(self.filepath_local)
        self.pictures_localx10 = dataIO.load_json(self.filepath_localx10)
        self.pictures_web = dataIO.load_json(self.filepath_web)
        self.pictures_pending = dataIO.load_json(self.filepath_pending)
        

        #Custom key which holds an array of Scenery filenames/paths
        self.JSON_mainKey = "scenery"
        
        #Prepend local listings with domain name.
        for x in range(0,len(self.pictures_local[JSON_mainKey])):
            self.pictures_local[JSON_mainKey][x][JSON_imageURLKey] = "https://nekomimi.injabie3.moe/scenery/" + self.pictures_local[JSON_mainKey][x][JSON_imageURLKey]

        #Prepend hosted listings with domain name.
        for x in range(0,len(self.pictures_localx10[JSON_mainKey])):
            self.pictures_localx10[JSON_mainKey][x][JSON_imageURLKey] = "http://injabie3.x10.mx/scenery/" + self.pictures_localx10[JSON_mainKey][x][JSON_imageURLKey]
        
        self.scenery = self.pictures_local[JSON_mainKey] + self.pictures_web[JSON_mainKey] + self.pictures_localx10[JSON_mainKey]
        self.pending = self.pictures_pending[JSON_mainKey]
        
    def __init__(self, bot):
        self.bot = bot
        checkFolder()
        checkFiles()
        self.refreshDatabase()
        
    #[p]Scenery
    @commands.command(name="scenery")
    async def _scenerymain(self):
        """Display some beautiful scenery :3"""
        randScenery = random.choice(self.scenery)
        embed = discord.Embed()
        embed.colour = discord.Colour.red()
        embed.title = "Scenery"
        embed.url = randScenery[JSON_imageURLKey]
        if randScenery[JSON_isPixiv]:
            source = "[{}]({})".format("Original Source","http://www.pixiv.net/member_illust.php?mode=medium&illust_id="+randScenery[JSON_pixivID])
            embed.add_field(name="Pixiv",value=source)
            customFooter = "ID: " + randScenery[JSON_pixivID]
            embed.set_footer(text=customFooter)
        #Implemented the following with the help of http://stackoverflow.com/questions/1602934/check-if-a-given-key-already-exists-in-a-dictionary
        if "character" in randScenery:
            embed.add_field(name="Info",value=randScenery["character"], inline=False)
        embed.set_image(url=randScenery[JSON_imageURLKey])
        try:
            await self.bot.say("",embed=embed)
        except Exception as e:
            await self.bot.say("Please try again.")
            print("Scenery exception:")
            print(e)
            print("==========")


    @commands.group(name="scenery+", pass_context=True, no_pm=False)
    async def _scenery(self, ctx):
        """Scenery! \o/"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    #[p]scenery+ about
    @_scenery.command(pass_context=True, no_pm=False)
    async def about(self, ctx):
        """Displays information about this module"""
        customAuthor = "[{}]({})".format("@Injabie3#1660","https://injabie3.moe/")
        embed = discord.Embed()
        embed.title = "About this module"
        embed.add_field(name="Name", value="Scenery Module")
        embed.add_field(name="Author", value=customAuthor)
        embed.add_field(name="Initial Version Date", value="2017-02-11")
        embed.add_field(name="Description", value="A module to display pseudo-random scenery images.  Image links are stored in the local database, separated into different lists (depending on if they are hosted locally or on another domain).  See https://github.com/Injabie3/lui-cogs for more info.")
        embed.set_footer(text="lui-cogs/scenery")
        await self.bot.say(content="",embed=embed)
        
    #[p]scenery+ numbers
    @_scenery.command(pass_context=True, no_pm=False)
    async def numbers(self, ctx):
        """Displays the number of images in the database."""
        await self.bot.say("There are:\n - **" + str(len(self.scenery)) + "** images available.\n - **" + str(len(self.pictures_pending[JSON_mainKey])) + "** pending images.")

    #[p]scenery+ refresh - Also allow for refresh in a DM to the bot.
    @_scenery.command(pass_context=True, no_pm=False)
    async def refresh(self, ctx):
        """Refreshes the internal database of nekomimi images."""
        self.refreshDatabase()
        await self.bot.say("List reloaded.  There are:\n - **" + str(len(self.scenery)) + "** images available.\n - **" + str(len(self.pictures_pending[JSON_mainKey])) + "** pending images.")

    #[p] nyaa debug
    @_scenery.command(pass_context=True, no_pm=False)
    async def debug(self, ctx):
        """Sends entire list via DM for debugging."""
        msg = "Debug Mode\nscenery:\n```"
        for x in range(0,len(self.scenery)):
            msg += self.scenery[x][JSON_imageURLKey] + "\n"
            if len(msg) > 1900:
               msg += "```"
               await self.bot.send_message(ctx.message.author, msg)
               msg = "```"
        msg += "```"
        await self.bot.send_message(ctx.message.author, msg)
        
        msg = "Catboys:\n```"
        for x in range(0,len(self.catboys)):
            msg += self.catboys[x][JSON_imageURLKey] + "\n"
            if len(msg) > 1900:
               msg += "```"
               await self.bot.send_message(ctx.message.author, msg)
               msg = "```"
        msg += "```"
        await self.bot.send_message(ctx.message.author, msg)
    
    #[p]scenery+ add
    @_scenery.command(pass_context=True, no_pm=True)
    async def add(self, ctx, link: str, description: str=""):
        """
        Add a Scenery image to the pending database.
        Will be screened before it is added to the global list. WIP
        
        link          The full URL to an image, use \" \" around the link.
        description   Description of character (optional)
        """
    
        temp = {}
        temp["url"] = link
        temp["character"] = description
        temp["submitter"] = ctx.message.author.name
        temp["id"] = None
        temp["is_pixiv"] = False
        
    
        self.pictures_pending[JSON_mainKey].append(temp)
        dataIO.save_json(self.filepath_pending, self.pictures_pending)

        #Get owner ID.
        owner = discord.utils.get(self.bot.get_all_members(),id=self.bot.settings.owner)
                              
        try:
            await self.bot.send_message(owner, "New Scenery image is pending approval. Please check the list!")
        except discord.errors.InvalidArgument:
            await self.bot.say("Added, but could not notify owner.")
        else:
            await self.bot.say("Added, notified and pending approval. :ok_hand:")
                
        
            
        

def setup(bot):
    checkFolder()   #Make sure the data folder exists!
    checkFiles()    #Make sure we have a local database!
    bot.add_cog(Scenery_beta(bot))
