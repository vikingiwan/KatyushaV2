 #####KatyushaV2#####
import discord
from discord.ext import commands
import asyncio
import sys
import random
import time
import configparser
import os
import sqlite3
import pyjokes
from cleverwrap import CleverWrap

##Variables & objects##
#Bot stuff
global VERSION
VERSION = '3.0'
global DEBUG
DEBUG = False
global iwanID
iwanID = 142076624072867840
global botID
botID = 217108205627637761
global vtacGuild
vtacGuild = 183107747217145856
global mainChannel
mainChannel= 622144477233938482
global logChannel
logChannel = 646211007294865408
global activeGiveaway
activeGiveaway = False
bot = commands.Bot(command_prefix="!")
connection = sqlite3.connect('KatyushaData.db')
cur = connection.cursor()
#Lists
killResponses = ["%s 'accidentally' fell in a ditch... RIP >:)", "Oh, %s did that food taste strange? Maybe it was.....*poisoned* :wink:", "I didn't mean to shoot %s, I swear the gun was unloaded!", "Hey %s, do me a favor? Put this rope around your neck and tell me if it feels uncomfortable.", "*stabs %s* heh.... *stabs again*....hehe, stabby stabby >:D", "%s fell into the ocean whilst holding an anvil...well that was stupid."]
userCommands = ["hug", "pat", "roll", "flip", "remind", "kill", "addquote", "quote", "joke", "dirtyjoke", "pfp", "info", "version", "changelog", "links", "link", "giveaway"]
#op_roles = [183109993686499328, 183109339991506945]
#officer_roles = [183110198188179456, 183109339991506945, 183109993686499328]

welcome_message='''
Welcome to Viking Tactical!

If you'd like to apply for full-membership, you can submit an application at <http://vikingtactical.ml/index.php?link-forums/apply-here.3/> (It usually takes 3-5 mins to complete) and then someone would read your application and either accept or decline it. Either way, you'd receive an e-mail with the decision (might need to check your spam folder, sometimes our emails end up in there, i'm working on fixing that lol)

Some of the benefits of becoming a full member are access to more channels on discord and categories on our forums, assignment to a division which has its own private chat channels, access to giveaways, and the ability to climb the ranks and gain promotions within the clan.
There's no rush, obligation or pressure to make an app though!
'''

##########
###RANKS###

#Recruit Rank
rank_rec = 469376345672253451

#Enlisted Ranks
rank_enlisted = 281727465968369665
rank_cpl = 492801929794158612
rank_lcpl = 632127911033569290
rank_pfc = 492801780002979850
rank_pvt = 574741329448534038

#Sub-Command Ranks
rank_subcommand = 594343305987489808
rank_msg = 492802360616419338
rank_sgt = 492802074140999691

#Command Ranks
rank_command = 569278265857015818
rank_cpt = 183109339991506945
rank_lt = 183110198188179456

#High-Command Ranks
rank_highcommand = 577169836476465153
rank_com = 183109993686499328
rank_col = 632122115096838144

#Rank Class Lists
rankClass_enlisted = [rank_pvt, rank_pfc, rank_lcpl, rank_cpl]
rankClass_subcommand = [rank_sgt, rank_msg]
rankClass_command = [rank_lt, rank_cpt]
rankClass_highcommand = [rank_col, rank_com]


##########



#Remove default help command
bot.remove_command('help')

#Util funcs
def getTokens():
    config = configparser.ConfigParser()
    if not os.path.isfile("tokens.cfg"):
        print("tokens file missing. ")
        print("Creating one now.")
        config.add_section("Tokens")
        config.set("Tokens", "Bot", "null")
        config.set("Tokens", "Cleverbot", "null")
        with open ('tokens.cfg', 'w') as configfile:
            config.write(configfile)
        print("File created.")
        print("Please edit tokens.cfg and then restart.")
        _ = input()
    else:
        config.read('tokens.cfg')
        global botToken
        botToken = config.get('Tokens', 'Bot')
        global cb
        cb = CleverWrap(config.get('Tokens', 'Cleverbot'))
    
def getRankClass(member):
    _rankClass = "null"
    for r in member.roles:
        if r.id in rankClass_enlisted:
            _rankClass = "enlisted"
        if r.id in rankClass_subcommand:
            _rankClass = "subcommand"
        if r.id in rankClass_command:
            _rankClass = "command"
        if r.id in rankClass_highcommand:
            _rankClass = "highcommand"
    debug(_rankClass)
    return _rankClass
    
#def isEnlisted(member):
#    for r in member.roles:
#        if  r.id in enlisted_ranks:
#            return True
#            return
#    return False
    
def getPromoRank(member):
    for r in member.roles:
        #_promoRank = None
        if r.id == rank_col:
            _promoRank = None
        elif r.id == rank_cpt:
            _promoRank = rank_col
        elif r.id == rank_lt:
            _promoRank = rank_cpt
        elif r.id == rank_msg:
            _promoRank = rank_lt
        elif r.id == rank_sgt:
            _promoRank = rank_msg
        elif r.id == rank_cpl:
            _promoRank = rank_sgt
        elif r.id == rank_lcpl:
            _promoRank = rank_cpl
        elif r.id == rank_pfc:
            _promoRank = rank_lcpl
        elif r.id == rank_pvt:
            _promoRank = rank_pfc
        elif r.id == rank_rec:
            _promoRank = rank_pvt
    return _promoRank
    
def debug(msg):
    if DEBUG == True:
        print("DEBUG: " + msg)
    
def create_tables():
    cur.execute('''CREATE TABLE IF NOT EXISTS quoteList
                     (QUOTES TEXT)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS Links
                     (name TEXT, link TEXT)''')
                     
def register_quote(usr, quote):
    quote = usr.name + ': "' + quote + '"'
    cur.execute("INSERT INTO quoteList (quotes) VALUES (?)", (quote,))
    connection.commit()
    
def load_quotes():
    print("Loading Quotes...")
    cur.execute('''SELECT * FROM quoteList''')
    global quotes
    quotes = cur.fetchall()
def get_quote():
    quote = random.choice(quotes)
    quote = str(quote)
    quote = quote.strip("('',)")
    return quote
    
def get_changelog(ver):
    with open ('changelogs/' + ver + '.txt', 'r') as changelog:
        changelog = changelog.read()
        changelog = changelog.splitlines()
    changelog = str(changelog)
    changelog = changelog.replace("',", "\n")
    changelog = changelog.split("['],")
    return changelog
    
    
    
def get_link(name):
    cur.execute("SELECT link FROM Links WHERE name = (?)", (name,))
    link = str(cur.fetchall())
    link = link.strip("[(',)]")
    return link
    
def add_link(name, link):
    cur.execute("INSERT INTO Links (name, link) VALUES (?, ?)", (name, link))
    connection.commit()
    print("Link Added")
    
def list_links():
    list = []
    cur.execute('''SELECT name FROM Links''')
    rows = cur.fetchall()
    for row in rows:
        _row = str(row)
        _row = _row.strip("[(',)]")
        list.append(_row)
    debug(list)
    return list
    

    
    

#Bot Events
@bot.event
async def on_ready():
    print("Discord.py version: " + discord.__version__)
    print("Logged in as: " + bot.user.name)
    print("ID: " + str(bot.user.id))
    print("------------------")
    _activity = discord.Game("Victory Through Comradery!")
    await bot.change_presence(activity=_activity)
    #_debugRoles = bot.get_guild(vtacGuild).get_role(rank_rec).name
    #print("Roles: " + _debugRoles)
    
@bot.event
async def on_member_join(member):
    print(member.name + " has joined the guild...assigning rank...")
    _role = bot.get_guild(vtacGuild).get_role(rank_rec)
    await member.add_roles(_role, reason="New member", atomic=True)
    print("Recruit rank added to " + member.display_name)
    print("Adding rank prefix...")
    _nick = "Rec. " + member.display_name
    await member.edit(nick=_nick, reason="New User")
    print("Added prefix to " + member.display_name)
    _chan = bot.get_guild(vtacGuild).get_channel(mainChannel)
    await _chan.send(":thumbsup: " + member.mention + " has joined Viking Tactical.")
    await member.send(welcome_message)
    
@bot.event
async def on_member_remove(member):
    _chan = bot.get_guild(vtacGuild).get_channel(mainChannel)
    await _chan.send(":thumbsdown: " + member.display_name + " has left Viking Tactical.")

#OPERATOR ONLY COMMANDS:
@bot.command(pass_context = True)
async def say(ctx, *, msg: str):
    if getRankClass(ctx.author) == "highcommand":
        await ctx.message.delete()
        await ctx.channel.send(msg)
    else:
        await bot.say("ERROR: UNAUTHORIZED!")

@bot.command(pass_context = True)
async def purge(ctx):
    if getRankClass(ctx.author) == "highcommand":
        await ctx.send("UNDERSTOOD, COMMANDER. I WILL DESTROY THE EVIDENCE!")
        await asyncio.sleep(4)
        await ctx.channel.purge(limit=100, bulk=True)
        await ctx.send("CHANNEL HAS BEEN PURGED, SIR!")
    else:
        await ctx.send("ERROR: UNAUTHORIZED")
        
@bot.command(pass_context = True)
async def getBot(ctx):
    if getRankClass(ctx.author) == "highcommand":
        await ctx.message.delete()
        await ctx.author.send("Invite link:\nhttps://discordapp.com/api/oauth2/authorize?client_id=217108205627637761&scope=bot&permissions=1")
    else:
        await ctx.author("ERROR: UNAUTHORIZED!")
        
@bot.command(pass_context = True)
async def addLink(ctx, name: str=None, *, link: str=None):
    if getRankClass(ctx.author) == "highcommand":
        print("name: " + name)
        print("link: " + link)
        add_link(name, link)
        await ctx.message.delete()
        await ctx.author.send("Link Saved!")
        
@bot.command(pass_context = True)
async def terminate(ctx):
    if getRankClass(ctx.author) == "highcommand":
        await ctx.author.send("Affirmative. Terminating now...")
        sys.exit()
    else:
        await ctx.author.send("ERROR: UNAUTHORIZED!")
        
        
@bot.command(pass_context = True)
async def startGiveaway(ctx, *, msg: str=None):
    if getRankClass(ctx.author) == "command":
        global activeGiveaway
        if activeGiveaway == True:
            await ctx.author.send("ERROR: There is already a giveaway in progress!")
        else:
            if msg == None:
                await ctx.author.send("ERROR: You cannot start a giveaway with a blank message!")
            else:
                global giveawayEntries
                giveawayEntries = []
                await ctx.message.delete()
                await bot.get_guild(vtacGuild).get_channel(mainChannel).send("@everyone A giveaway is  starting!\n(Remember, you must be a full member to participate in giveaways)\n")
                await asyncio.sleep(5)
                msg = "\n" + msg + "\n\nUse !giveaway to enter the giveaway!"
                em = discord.Embed(title='', description=msg, colour=0xFF0000)
                em.set_author(name='Giveaway Info:', icon_url="https://i.imgur.com/0DCg8JB.png")
                await bot.get_guild(vtacGuild).get_channel(mainChannel).send(embed=em)
                activeGiveaway = True
    else:
        await ctx.author.send("ERROR: UNAUTHORIZED!")
        
@bot.command(pass_context = True)
async def endGiveaway(ctx):
    if getRankClass(ctx.author) == "command":
        global activeGiveaway
        activeGiveaway = False
        await bot.get_guild(vtacGuild).get_channel(mainChannel).send("@everyone The current giveaway is ending! I'm now deciding the winner...")
        await asyncio.sleep(5)
        await bot.get_guild(vtacGuild).get_channel(mainChannel).send("And the winner is...")
        winner = random.choice(giveawayEntries)
        await asyncio.sleep(10)
        await bot.get_guild(vtacGuild).get_channel(mainChannel).send(winner.mention + "! Congratulations! :clap:")    
    else:
        await ctx.author.send("ERROR: UNAUTHORIZED!")
   
        
#OFFICER COMMANDS
@bot.command(pass_context = True)
async def promote(ctx, *, member: discord.Member = None):
    await ctx.author.send("Promote command = WIP")
        
#USER COMMANDS
@bot.command(pass_context = True)
async def help(ctx):
    usrCmds = '\n'.join("!" + str(c) for c in userCommands)
    em = discord.Embed(title='', description=usrCmds, colour=0xFF0000)
    em.set_author(name='Commands:', icon_url=bot.user.avatar_url)
    await ctx.message.channel.send(embed=em)

@bot.command()
async def version(ctx):
    await ctx.channel.send("I am currently on version " + VERSION)
    
@bot.command(pass_context = True)
async def changelog(ctx, ver: str=VERSION):
    await ctx.channel.send("Changelog for version " + ver + ":")
    for x in get_changelog(ver):
        await ctx.channel.send("`" + str(x).strip("['],").replace("'", "") + "`")
    
@bot.command(pass_context = True)
async def hug(ctx):
    hug = random.choice([True, False])
    if hug == True:
        await ctx.channel.send(ctx.message.author.mention + ": :hugging:")
    else:
        await ctx.channel.send(ctx.message.author.mention + ": You don't deserve a hug, cyka.")
        
@bot.command()
async def roll(ctx, *, dice : str=None):
    if dice == None:
        await ctx.channel.send('Format has to be in NdN!')
        return
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await ctx.channel.send('Format has to be in NdN!')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await ctx.channel.send(result)
      
@bot.command(pass_context = True)
async def flip(ctx):
    await ctx.channel.send("Okay, I'll flip it!")
    await asyncio.sleep(3)
    if random.choice([True, False]) == True:
        await ctx.channel.send(ctx.message.author.mention + ": the result is.......**HEADS**!")
    else:
        await ctx.channel.send(ctx.message.author.mention + ": the result is.......**TAILS**!")
      
@bot.group(pass_context = True)
async def remind(ctx, time: str = "0", *, reminder: str="null"):
    time = int(time)
    if time == 0 or reminder == "null":
        await ctx.channel.send("Correct Usage: !remind <time in minutes> <reminder>")
        await ctx.channel.send("Example: !remind 5 Tell me how reminders work")
        return
    else:
        await ctx.message.delete()
        await ctx.channel.send("Okay, " + ctx.message.author.mention + "! I'll remind you :smile:")
        await asyncio.sleep(time * 60)
        await ctx.message.author.send("You wanted me to remind you: " + reminder)
        
@bot.command(pass_context = True)
async def kill (ctx, *, member: discord.Member = None):
    if member is None:
        await ctx.channel.send(ctx.message.author.mention + ": I need a target!")
        return

    if member.id == botID and ctx.message.author.id == iwanID:
        await ctx.channel.send(ctx.message.author.mention + ": C-Commander, p-please...I'm useful! Please don't terminate me! :cry:")
    elif member.id == ctx.message.author.id:
        await ctx.channel.send(ctx.message.author.mention + ": Why do you want me to kill you? :open_mouth:")
    elif member.id == botID:
        await ctx.channel.send(ctx.message.author.mention + ": Hah! Don't get cocky kid, I could end you in less than a minute! :dagger:")
    elif member.id == iwanID:
        await ctx.channel.send(ctx.message.author.mention + ": Kill the Commander? I could never!")
    else:
        random.seed(time.time())
        choice = killResponses[random.randrange(len(killResponses))] % member.mention
        await ctx.channel.send(ctx.message.author.mention + ": " + choice)
      
@bot.command(pass_context = True)
async def pat(ctx, *, member: discord.Member = None):
    if member is None:
        await ctx.channel.send("Aww, does somebody need a headpat? I'll pat you, " + ctx.message.author.mention)
        await ctx.channel.send(file=discord.File("img/headpat.gif"))
    else:
        await ctx.channel.send(ctx.message.author.mention + " pats " + member.mention)
        await ctx.channel.send(file=discord.File("img/headpat.gif"))
           
@bot.command(pass_context = True)
async def addquote(ctx, member: discord.Member = None, *, quote: str=None):
    if member == None or quote == None:
        await ctx.channel.send("You must mention a user and add a quote!")
        await ctx.channel.send("Example: `!addquote @Iwan I love quotes`")
    elif member.id == botID:
        await ctx.channel.send("ERROR: UNAUTHORIZED! You are not allowed to quote me. Muahahaha!")
        return
    else:
        register_quote(member, quote)
        await ctx.message.delete()
        await ctx.channel.send("Quote added :thumbsup:")
        load_quotes()
       
@bot.command()
async def quote(ctx):
    await ctx.channel.send(get_quote())
    
@bot.command(pass_context = True)
async def poke(ctx, member: discord.Member=None):
    if member==None:
        await ctx.channel.send("I can't poke nobody! Try mentioning someone with `@`, like this\n`!poke @Iwan`")
        return
    else:
        await ctx.channel.send(ctx.message.author.mention + " just poked " + member.mention + "!")
        await ctx.channel.send(file=discord.File("img/poke.gif"))
        
@bot.command(pass_context = True)
async def joke(ctx):
    await ctx.channel.send(ctx.message.author.mention + ": " + pyjokes.get_joke())
    
@bot.command(pass_context = True)
async def dirtyjoke(ctx):
    await ctx.channel.send(ctx.message.author.mention + ": " + pyjokes.get_joke('en', 'adult'))
    
@bot.command(pass_context = True)
async def pfp(ctx, member: discord.Member=None):
    if member==None:
        member = ctx.message.author
#        await bot.say("You forgot to give me a user! try mentioning someone with @ next time!")
#        await bot.say("Example: `!pfp @Katyusha`")
#        return
    await ctx.channel.send(ctx.author.mention + ": Here you go!\n" + str(member.avatar_url_as(static_format="png", size=1024)))
        
@bot.command(pass_context = True)
async def info(ctx, member: discord.Member=None):
    if member == None:
        member = ctx.message.author
    info = "Joined guild on: " + member.joined_at.strftime("%A %B %d, %Y at %I:%M%p") + "\n"
    info = info + "Account created on: " + member.created_at.strftime("%A %B %d, %Y at %I:%M%p")
    em = discord.Embed(title='', description=info, colour=0xFF0000)
    em.set_author(name=member.name, icon_url=member.avatar_url)
    await ctx.channel.send(embed=em)

@bot.command(pass_context = True)
async def link(ctx, name: str=None):
    if name == None:
        await ctx.channel.send("ERROR: LINK NOT FOUND!")
    else:
        await ctx.channel.send(ctx.message.author.mention + " " + get_link(name))
        
@bot.command(pass_context = True)
async def links(ctx):
    await ctx.channel.send(list_links())
    
    
@bot.command(pass_context = True)
async def giveaway(ctx):
    if getRankClass(ctx.author) != "null":
        global activeGiveaway
        if activeGiveaway == False:
            await ctx.channel.send(ctx.message.author.mention + " There is no active giveaway!")
        else:
            global giveawayEntries
            if ctx.message.author in giveawayEntries:
                await ctx.channel.send(ctx.message.author.mention + " You're already entered into the giveaway. No cheating!")
            else:
                _entry = [ctx.message.author]
                giveawayEntries = giveawayEntries + _entry
                await ctx.channel.send(ctx.message.author.mention + " has entered into the giveaway!")
    else:
        await ctx.channel.send("ERROR: UNAUTHORIZED\nYou are not a full member! To gain access to giveaways, please submit an application.")
    
        
        
#Cleverbot integration
@bot.event
async def on_message(message):
    await bot.process_commands(message)
#    if message.content.startswith(message.guild.get_member(botID).mention):
#        if message.author.id != botID:
#            stripmsg = message.content.replace('Katyusha, ', "")
#            botmsg = cb.say(stripmsg)
#            await ctx.channel.send(message.author.mention + ': ' + botmsg)
    
    
#Runtime, baby! Let's go!    
print ('Getting ready...')
print('Loading Katyusha v' + VERSION)
create_tables()
load_quotes()
getTokens()
bot.run(botToken)