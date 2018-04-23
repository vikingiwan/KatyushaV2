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
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

##Variables & objects##
#Bot stuff
global VERSION
VERSION = '0.4'
iwanID = "142076624072867840"
botID = "217108205627637761"
vtacServer = "183107747217145856"
bot = commands.Bot(command_prefix="!")
connection = sqlite3.connect('KatyushaData.db')
cur = connection.cursor()
#Lists
killResponses = ["%s 'accidentally' fell in a ditch... RIP >:)", "Oh, %s did that food taste strange? Maybe it was.....*poisoned* :wink:", "I didn't mean to shoot %s, I swear the gun was unloaded!", "Hey %s, do me a favor? Put this rope around your neck and tell me if it feels uncomfortable.", "*stabs %s* heh.... *stabs again*....hehe, stabby stabby >:D", "%s fell into the ocean whilst holding an anvil...well that was stupid."]
userCommands = ["test", "hug", "pat", "roll", "flip", "remind", "kill", "calc", "addquote", "quote", "joke", "dirtyjoke", "pfp", "info", "$", "pay", "version", "changelog"]
operatorCommands = ["say", "purge", "getBot", "$+", "$-", "!update"]
op_roles = ["183109339991506945", "183109993686499328", "437011917677264906"]
#Currency stuff
currName = "credits"
currSymbol = "©"
dodropCurr = True
dropCurrChannel = "183107747217145856"
#bot_testing dropCurrChannel = "282029355201462272"
updateChan = "281728643359834112"

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
        config.set("Tokens", "smtp-user", "null")
        config.set("Tokens", "smtp-pass", "null")
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
        global smtpUser
        smtpUser = config.get('Tokens', 'smtp-user')
        global smtpPass
        smtpPass = config.get('Tokens', 'smtp-pass')
        
def isOp(member):
    for r in member.roles:
        if r.id in op_roles:
            return True
            return
    return False
    
def create_tables():
    cur.execute('''CREATE TABLE IF NOT EXISTS quoteList
                     (QUOTES TEXT)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS Treasury
                     (ID TEXT, amount TEXT)''')
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
    
def getCurr(memID):
    cur.execute("SELECT amount FROM Treasury WHERE ID = (?)", (memID,))
    amt = str(cur.fetchall())
    if amt == "[]":
        cur.execute('''INSERT INTO Treasury (ID, amount) VALUES (?, 0)''', (memID,))
        connection.commit()
        return "0"
    amt = amt.strip("[(',)]")
    return amt
    
def addCurr(memID, amount):
    cur.execute("SELECT amount FROM Treasury WHERE ID = (?)", (memID,))
    amt = str(cur.fetchall())
    amt = int(amt.strip("[(',)]"))
    amt = amt + amount
    cur.execute("UPDATE Treasury SET amount = (?) WHERE ID = (?)", (amt, memID))
    connection.commit()
    
def subCurr(memID, amount):
    cur.execute("SELECT amount FROM Treasury WHERE ID = (?)", (memID,))
    amt = str(cur.fetchall())
    amt = int(amt.strip("[(',)]"))
    amt = amt - amount
    if amt < 0:
        amt = 0
    cur.execute("UPDATE Treasury SET amount = (?) WHERE ID = (?)", (amt, memID))
    connection.commit()
    
async def dropCurr(chan):
    print("Drop channel: " + chan.name)
    while dodropCurr == True:
        random.seed(time.time())
        _waitTime = random.randint(600, 900)
        await asyncio.sleep(_waitTime)
        msg = await bot.wait_for_message(timeout=120, channel=chan)
        if msg != None:
            await asyncio.sleep(10)
            dropmsg = await bot.send_message(chan, "Oopsies, I dropped a couple " + currName + "!\ntype `gimmie` to grab it!")
            _msg = await bot.wait_for_message(timeout=60, channel=chan, content="gimmie")
            if _msg != None:
                __ = getCurr(_msg.author.id)
                addCurr(_msg.author.id, 2)
                await bot.delete_message(dropmsg)
                await bot.send_message(chan, _msg.author.mention + " has grabbed the " + currName + "!")
            else:
                await bot.delete_message(dropmsg)
                
def emailIwan(sub, body):
    msg = MIMEMultipart()
    msg['From'] = 'vikingiwan@gmail.com'
    msg['To'] = 'vikingiwan@gmail.com'
    msg['Subject'] = sub
    msg.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(smtpUser, smtpPass)
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()
    
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
    print(list)
    return list
    

#Bot Functions
@bot.event
async def on_ready():
    print("Logged in as: " + bot.user.name)
    print("ID: " + bot.user.id)
    print("------------------")
    await bot.change_presence(game=discord.Game(name="Victory Through Comradery!"))
    await dropCurr(bot.get_server(vtacServer).get_channel(dropCurrChannel))

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
   
@bot.command(pass_context = True, aliases=['$+'])
async def addbal(ctx, member: discord.Member=None, *, amount: int):
    if isOp(ctx.message.author) == True:
        if member == None:
            member = ctx.message.author
        addCurr(member.id, amount)
        await bot.delete_message(ctx.message)
    else:
        await bot.say("ERROR: UNAUTHORIZED")
        
@bot.command(pass_context = True, aliases=['$-'])
async def subbal(ctx, member: discord.Member=None, *, amount: int):
    if isOp(ctx.message.author) == True:
        if member == None:
            member = ctx.message.author
        subCurr(member.id, amount)
        await bot.delete_message(ctx.message)
    else:
        await bot.say("ERROR: UNAUTHORIZED")
        
@bot.command(pass_context = True)
async def update(ctx):
    if ctx.message.channel == bot.get_server(vtacServer).get_channel(updateChan):
        await bot.delete_message(ctx.message)
        await bot.say("@here I've updated!")
        await bot.say("Changelog for version " + VERSION     + ":")
        for x in get_changelog(VERSION):
                await bot.say("`" + str(x).strip("['],").replace("'", "") + "`")
        
    else:
        await bot.delete_message(ctx.message)
        
@bot.command(pass_context = True)
async def addLink(ctx, name: str=None, *, link: str=None):
    if isOp(ctx.message.author) == True:
        print("name: " + name)
        print("link: " + link)
        add_link(name, link)
        await bot.delete_message(ctx.message)
        await bot.say("Link Saved!")
   
        
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
async def changelog(ctx, ver: str=VERSION):
    await bot.say("Changelog for version " + ver + ":")
    for x in get_changelog(ver):
        await bot.say("`" + str(x).strip("['],").replace("'", "") + "`")
    
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
      
@bot.command(pass_context = True)
async def flip(ctx):
    await bot.say("Okay, I'll flip it!")
    await bot.send_typing(ctx.message.channel)
    await asyncio.sleep(3)
    if random.choice([True, False]) == True:
        await bot.say(ctx.message.author.mention + ": the result is.......**HEADS**!")
    else:
        await bot.say(ctx.message.author.mention + ": the result is.......**TAILS**!")
      
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
  
@bot.command(pass_context = True, aliases=['$'])
async def bal(ctx, member: discord.Member=None):
    if member == None:
        member = ctx.message.author
    await bot.say(member.mention + "'s balance: " + getCurr(member.id) + currSymbol)
    
@bot.command(pass_context = True, aliases=['give'])
async def pay(ctx, target: discord.Member=None, *, amount: int=None):
    if target == None:
        await bot.say("You need to tell me who you want to pay!\nExample: `!pay @Katyusha 5` (pays katyusha 5 " + currName)
    elif (amount == None):
        await bot.say("You need to specify an amount to pay!\nExample: `!pay @Katyusha 5` (pays katyusha 5 " + currName)
    else:
        subCurr(ctx.message.author.id, amount)
        addCurr(target.id, amount)
        await bot.say(ctx.message.author.mention + " has payed " + target.mention + " " + str(amount) + " " + currName)


@bot.command(pass_context = True)
async def link(ctx, name: str=None):
    if name == None:
        await bot.say("ERROR: LINK NOT FOUND!")
    else:
        await bot.say(ctx.message.author.mention + " " + get_link(name))
        
@bot.command(pass_context = True)
async def links(ctx):
    await bot.say(list_links())
        
        
#Cleverbot integration
@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.content.startswith(message.server.get_member(botID).mention):
        if message.author.id != botID:
            await bot.send_typing(message.channel)
            stripmsg = message.content.replace('Katyusha, ', "")
            botmsg = cb.say(stripmsg)
            await bot.send_message(message.channel, message.author.mention + ': ' + botmsg)
    
    
#Runtime, baby! Let's go!    
print ('Getting ready...')
print('Loading Katyusha2 v' + VERSION)
create_tables()
load_quotes()
getTokens()
bot.run(botToken)