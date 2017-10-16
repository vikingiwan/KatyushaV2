#####KatyushaV2#####
import discord
from discord.ext import commands
import asyncio
import random
import time
import configparser
import os
import sqlite3
import pyjokes
from cleverwrap import CleverWrap

#Variables & objects
global VERSION
VERSION = '0.1'
iwanID = "142076624072867840"
botID = "217108205627637761"
bot = commands.Bot(command_prefix="!")
connection = sqlite3.connect('KatyushaData.db')
cur = connection.cursor()
killResponses = ["%s 'accidentally' fell in a ditch... RIP >:)", "Oh, %s did that food taste strange? Maybe it was.....*poisoned* :wink:", "I didn't mean to shoot %s, I swear the gun was unloaded!", "Hey %s, do me a favor? Put this rope around your neck and tell me if it feels uncomfortable.", "*stabs %s* heh.... *stabs again*....hehe, stabby stabby >:D", "%s fell into the ocean whilst holding an anvil...well that was stupid."]
userCommands = ["test", "hug", "pat", "roll", "remind", "kill", "calc", "addquote", "quote", "joke", "dirtyjoke", "pfp", "info", "version"]
operatorCommands = ["say", "purge", "getBot"]

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
        
def isOp(member):
    for r in member.roles:
        if r.id == "183109339991506945":
            return True
            return
        elif r.id == "183109993686499328":
            return True
            return
    return False
    
def create_tables():
    cur.execute('''CREATE TABLE IF NOT EXISTS quoteList
                     (QUOTES TEXT)''')
                     
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

#Bot Functions
@bot.event
async def on_ready():
    print("Logged in as: " + bot.user.name)
    print("ID: " + bot.user.id)
    print("------------------")
    await bot.change_presence(game=discord.Game(name="Victory Through Comradery!"))

#OPERATOR ONLY COMMANDS:
@bot.command(pass_context = True)
async def say(ctx, *, msg: str):
    if isOp(ctx.message.author) == True:
        await bot.delete_message(ctx.message)
        await bot.say(msg)
    else:
        await bot.say("ERROR: UNAUTHORIZED!")

@bot.command(pass_context = True)
async def purge(ctx):
    if isOp(ctx.message.author) == True:
        await bot.say("UNDERSTOOD, COMMANDER. I WILL DESTROY THE EVIDENCE!")
        await asyncio.sleep(4)
        async for msg in bot.logs_from(ctx.message.channel):
            await bot.delete_message(msg)
        await bot.say("CHANNEL HAS BEEN PURGED, SIR!")
    else:
        await bot.say("ERROR: UNAUTHORIZED")
        
@bot.command(pass_context = True)
async def getBot(ctx):
    if isOp(ctx.message.author) == True:
        await bot.delete_message(ctx.message)
        await bot.send_message(ctx.message.author, "Invite link:\nhttps://discordapp.com/api/oauth2/authorize?client_id=217108205627637761&scope=bot&permissions=1")
    else:
        await bot.say("ERROR: UNAUTHORIZED!")
        
        
#USER COMMANDS
@bot.command(pass_context = True)
async def help(ctx):
    usrCmds = '\n'.join("!" + str(c) for c in userCommands)
    em = discord.Embed(title='', description=usrCmds, colour=0xFF0000)
    em.set_author(name='Commands:', icon_url=bot.user.avatar_url)
    await bot.send_message(ctx.message.channel, embed=em)
    #If  user is operator, send dm with op commands
    if isOp(ctx.message.author) == True:
        opCmds = '\n'.join("!" + str(c) for c in operatorCommands)
        em = discord.Embed(title='', description=opCmds, colour=0xFF0000)
        em.set_author(name='High-Command Commands:', icon_url=bot.user.avatar_url)
        await bot.send_message(ctx.message.author, embed=em)

@bot.command()
async def version():
    await bot.say("I am currently on version " + VERSION)
        
@bot.command()
async def test():
    await bot.say("Hello World!")
    
@bot.command(pass_context = True)
async def hug(ctx):
    hug = random.choice([True, False])
    if hug == True:
        await bot.say(ctx.message.author.mention + ": :hugging:")
    else:
        await bot.say(ctx.message.author.mention + ": You don't deserve a hug, cyka.")
        
@bot.command()
async def roll(dice : str=None):
    if dice == None:
        await bot.say('Format has to be in NdN!')
        return
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await bot.say('Format has to be in NdN!')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await bot.say(result)
        
@bot.group(pass_context = True)
async def remind(ctx, time: str = "0", *, reminder: str="null"):
    time = int(time)
    if time == 0 or reminder == "null":
        await bot.say("Correct Usage: !remind <time in minutes> <reminder>")
        await bot.say("Example: !remind 5 Tell me how reminders work")
        return
    else:
        await bot.delete_message(ctx.message)
        await bot.say("Okay, " + ctx.message.author.mention + "! I'll remind you :smile:")
        await asyncio.sleep(time * 60)
        await bot.send_message(ctx.message.author, "You wanted me to remind you: " + reminder)
        
@bot.command(pass_context = True)
async def kill (ctx, *, member: discord.Member = None):
    if member is None:
        await bot.say(ctx.message.author.mention + ": I need a target!")
        return

    if member.id == botID and ctx.message.author.id == iwanID:
        await bot.say(ctx.message.author.mention + ": C-Commander, p-please...I'm useful! Please don't terminate me! :cry:")
    elif member.id == ctx.message.author.id:
        await bot.say(ctx.message.author.mention + ": Why do you want me to kill you? :open_mouth:")
    elif member.id == botID:
        await bot.say(ctx.message.author.mention + ": Hah! Don't get cocky kid, I could end you in less than a minute! :dagger:")
    elif member.id == iwanID:
        await bot.say(ctx.message.author.mention + ": Kill the Commander? I could never!")
    else:
        random.seed(time.time())
        choice = killResponses[random.randrange(len(killResponses))] % member.mention
        await bot.say(ctx.message.author.mention + ": " + choice)
      
@bot.command(pass_context = True)
async def pat(ctx, *, member: discord.Member = None):
    if member is None:
        await bot.say("Aww, does somebody need a headpat? I'll pat you, " + ctx.message.author.mention)
        await bot.send_file(ctx.message.channel, "img/headpat.gif")
    else:
        await bot.say(ctx.message.author.mention + " pats " + member.mention)
        await bot.send_file(ctx.message.channel, "img/headpat.gif")
        
@bot.group(pass_context = True)
async def calc(ctx):
    if ctx.invoked_subcommand is None:
        await bot.say("Invalid arguments! Supported operations are: `add` `subract` `multiply` `divide`")
        await bot.say("Example: `!calc add 1 1` will yield a result of 2")
@calc.command()
async def add(left: float, right: float):
    ans = left + right
    await bot.say(str(left) + " + " + str(right) + " = " + str(ans))
@calc.command()
async def subtract(left: float, right: float):
    ans = left - right
    await bot.say(str(left) + " - " + str(right) + " = " + str(ans))
@calc.command()
async def multiply(left: float, right: float):
    ans = left * right
    await bot.say(str(left) + " * " + str(right) + " = " + str(ans))
@calc.command()
async def divide(left: float, right: float):
    ans = left / right
    await bot.say(str(left) + " / " + str(right) + " = " + str(ans))
    
@bot.command(pass_context = True)
async def addquote(ctx, member: discord.Member = None, *, quote: str=None):
    if member == None or quote == None:
        await bot.say("You must mention a user and add a quote!")
        await bot.say("Example: `!addquote @Iwan I love quotes`")
    elif member.id == botID:
        await bot.say("ERROR: UNAUTHORIZED! You are not allowed to quote me. Muahahaha!")
        return
    else:
        register_quote(member, quote)
        await bot.delete_message(ctx.message)
        await bot.say("Quote added :thumbsup:")
        load_quotes()
       
@bot.command()
async def quote():
    await bot.say(get_quote())
    
@bot.command(pass_context = True)
async def poke(ctx, member: discord.Member=None):
    if member==None:
        await bot.say("I can't poke nobody! Try mentioning someone with `@`, like this\n`!poke @Iwan`")
        return
    else:
        await bot.say(ctx.message.author.mention + " just poked " + member.mention + "!")
        await bot.send_file(ctx.message.channel, "img/poke.gif")
        
@bot.command(pass_context = True)
async def joke(ctx):
    await bot.say(ctx.message.author.mention + ": " + pyjokes.get_joke())
    
@bot.command(pass_context = True)
async def dirtyjoke(ctx):
    await bot.say(ctx.message.author.mention + ": " + pyjokes.get_joke('en', 'adult'))
    
@bot.command(pass_context = True)
async def pfp(ctx, member: discord.Member=None):
    if member==None:
        member = ctx.message.author
#        await bot.say("You forgot to give me a user! try mentioning someone with @ next time!")
#        await bot.say("Example: `!pfp @Katyusha`")
#        return
    await bot.say(ctx.message.author.mention + ": Here you go!\n" + member.avatar_url)
        
@bot.command(pass_context = True)
async def info(ctx, member: discord.Member=None):
    if member == None:
        member = ctx.message.author
    info = "Joined server on: " + member.joined_at.strftime("%A %B %d, %Y at %I:%M%p") + "\n"
    info = info + "Account created on: " + member.created_at.strftime("%A %B %d, %Y at %I:%M%p")
    em = discord.Embed(title='', description=info, colour=0xFF0000)
    em.set_author(name=member.name, icon_url=member.avatar_url)
    await bot.send_message(ctx.message.channel, embed=em)
    
#Cleverbot integration
@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.content.startswith(message.server.get_member(botID).mention):
        await bot.send_typing(message.channel)
        stripmsg = message.content.replace('Katyusha, ', "")
        botmsg = cb.say(stripmsg)
        await bot.send_message(message.channel, message.author.mention + ': ' + botmsg)
    
    
#Runtime, baby! Let's go!    
print ('Getting ready...')
print('Loading Katyusha v' + VERSION)
create_tables()
load_quotes()
getTokens()
bot.run(botToken)