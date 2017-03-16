import json
import discord
import datetime
from discord.ext import commands
import asyncio


description = '''A bot for testing purposes'''


bot = commands.Bot(command_prefix='?', description=description)

@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.errors.CheckFailure):
        await bot.send_message(ctx.message.author, "Missing required permissions.")

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    if not hasattr(bot, 'uptime'):
        bot.uptime = datetime.datetime.utcnow()


def loadjson():
    with open('serverlist.json', 'r+') as f:
        return json.load(f)


@bot.command()
async def uptime():
    await bot.say('{}'.format(datetime.datetime.utcnow() - bot.uptime))


def server_check(ctx):
    server = ctx.message.server
    user = ctx.message.author
    data = loadjson()
    serv = data['Servers']
    if server.id in serv:
        if isinstance(serv[server.id]['Perms'], list):
            roles = []
            perm_role = serv[server.id]['Perms']
            if not perm_role:
                return True
            else:
                for perm in perm_role:
                        role = discord.utils.get(server.roles, name=perm)
                        roles.append(role)

            for x in roles:
                if x in user.roles:
                    return True

        if serv[server.id]['Perms'] is not None:
            perm_role = serv[server.id]['Perms']
            role = discord.utils.get(server.roles, name=perm_role)
            if role in user.roles:
                return True
            else:
                return False
        else:
            return True


@commands.check(server_check)
@bot.command(aliases=['cc'], pass_context=True)
async def currentcolour(ctx):
    userauthor = ctx.message.author
    rolecolour = userauthor.colour
    await bot.reply('current colour is: {0}'.format(rolecolour))


@commands.check(server_check)
@bot.command(aliases=['nickcolor', 'nc'], pass_context=True)
async def nickcolour(ctx, value: discord.Colour):
    userauthor = ctx.message.author.id
    dserver = ctx.message.server
    if not discord.utils.get(dserver.roles, name="ColourID"+userauthor):
        try:
            role = await bot.create_role(dserver, name="ColourID"+userauthor, colour=value)
            await bot.add_roles(ctx.message.author, role)
            msg = bot.reply("colour changed!")
            await asyncio.sleep(5)
            await bot.delete_message(msg)
        except PermissionError:
            await bot.say('Colourbot cannot create/edit roles.')
    else:
        try:
            role = discord.utils.get(dserver.roles, name="ColourID"+userauthor)
            await bot.add_roles(ctx.message.author, role)
            await bot.edit_role(dserver, role, colour=value)
            msg = await bot.reply("colour changed!")
            await asyncio.sleep(5)
            await bot.delete_message(msg)
        except PermissionError:
            await bot.say("Couldnt not complete command")


@commands.has_permissions(manage_roles=True)
@bot.command(pass_context=True)
async def addperm(ctx, perm: str):
    server = ctx.message.server.id
    role = discord.utils.get(ctx.message.server.roles, name=perm)
    if role:
        data = loadjson()
        serv = data['Servers']
        if server in serv:
            if isinstance(serv[server]['Perms'], list):
                currentroles = serv[server]['Perms']
                if role.name in currentroles:
                    pass
                else:
                    currentroles.append(role.name)
                    serv[server]['Perms'] = currentroles
            else:
                serv[server]['Perms'] = role.name
        with open('serverlist.json', 'w') as f:
            json.dump(data, f)


@bot.command(pass_context=True)
@commands.has_permissions(manage_roles=True)
async def removeperm(ctx, perm: str):
    server = ctx.message.server.id
    role = discord.utils.get(ctx.message.server.roles, name=perm)
    if role:
        data = loadjson()
        serv = data['Servers']
        if server in serv:
            if isinstance(serv[server]['Perms'], list):
                serv[server]['Perms'].remove(role.name)
            else:
                serv[server]['Perms'] = None
        with open('serverlist.json', 'w') as f:
            json.dump(data, f)


@bot.command(pass_context=True)
async def displayperms(ctx):
    data = loadjson()
    server = ctx.message.server.id
    serv_perms = data['Servers'][server]['Perms']
    if isinstance(serv_perms, list) and len(serv_perms) == 1:
        await bot.say(serv_perms[0])
    elif isinstance(serv_perms, list) and len(serv_perms) > 1:
        toprint = ', '.join(serv_perms)
        msg = await bot.say("You need to be any of these: {}".format(toprint))
        await asyncio.sleep(5)
        await bot.delete_message(msg)
    else:
        msg = await bot.say("You need to be: {}".format(serv_perms))
        await asyncio.sleep(5)
        await bot.delete_message(msg)

try:
    bot.run('MTg1ODEyNzIwMzY3NDM1Nzc2.CjBf_A.EADPXn9Xqadq33JEdnCJJQxIbi0')
except KeyboardInterrupt:
    bot.stop()
finally:
    bot.close()
