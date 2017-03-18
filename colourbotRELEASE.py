import json
import discord
import datetime
import asyncio
from discord.ext import commands


description = '''A bot that allows users to change their own name colours.coloubot
Note to Admins: Move the role of the bot **higher** than the roles it creates or else it won't work.
Other roles must have no colour or they may overwrite the
custom colour.'''


bot = commands.Bot(command_prefix='?', description=description)


@bot.event
async def on_server_join(server):
    data = loadjson()
    d = {'Perms': []}
    data['Servers'][server.id] = d
    with open('serverlist.json', 'w') as f:
        json.dump(data, f)


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
    """
    Shows how long the bot has been running for this session.\n
    usage: ?uptime"""
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
    """Shows the current colour of your colour role!\n
    usage: ?currentcolour, ?cc"""
    userauthor = ctx.message.author
    rolecolour = userauthor.colour
    embed = discord.Embed(title='__**Colour Picker**__',
                          description='Your current colour is: **{}**, {}'.format(
                              str(rolecolour), userauthor.name), colour=rolecolour)
    embed.set_thumbnail(url='https://www.beautycolorcode.com/{}.png'.format(str(rolecolour)[1:]))
    await bot.reply(content='', embed=embed)


@commands.check(server_check)
@bot.command(aliases=['nickcolor', 'nc'], pass_context=True)
async def nickcolour(ctx, value: discord.Colour):
    """Input your hexcode of choice to change the colour of your name!\n
    usage: ?nickcolour/?nickcolor/?nc #hexcode"""
    embed = discord.Embed(title='__**Colour Picker**__',
                          description='Colour changed to: **{}**'.format(str(value)),
                          colour=value)
    embed.set_thumbnail(url='https://www.beautycolorcode.com/{}.png'.format(str(value)[1:]))
    userauthor = ctx.message.author.id
    dserver = ctx.message.server
    if not discord.utils.get(dserver.roles, name="ColourID" + userauthor):
        try:
            role = await bot.create_role(dserver, name="ColourID" + userauthor, colour=value)
            await bot.add_roles(ctx.message.author, role)
            msg = bot.say(embed=embed)
            await asyncio.sleep(10)
            await bot.delete_message(msg)
        except PermissionError:
            await bot.say('Colourbot cannot create/edit roles.')
    else:
        try:
            role = discord.utils.get(dserver.roles, name="ColourID" + userauthor)
            await bot.add_roles(ctx.message.author, role)
            await bot.edit_role(dserver, role, colour=value)
            msg = await bot.say(embed=embed)
            await asyncio.sleep(10)
            await bot.delete_message(msg)
        except PermissionError:
            await bot.say("Couldnt not complete command")


@commands.has_permissions(manage_roles=True)
@bot.command(pass_context=True)
async def addperm(ctx, perm: str):
    """Used to add a role to the whitelist of roles.\n
    usage: ?addperm [role name]"""
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
    """Removes a role from the list of required roles.\n
    usage: ?removeperm [name of role]."""
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
    """Shows the roles that a User has to be in order to change their name colour.\n
    usage: ?displayperms"""
    data = loadjson()
    server = ctx.message.server.id
    serv_perms = data['Servers'][server]['Perms']
    if isinstance(serv_perms, list):
        if and len(serv_perms) == 1:
            await bot.say(serv_perms[0])
        elif len(serv_perms) > 1:
            toprint = ', '.join(serv_perms)
            msg = await bot.say("You need to be any of these: {}".format(toprint))
            await asyncio.sleep(5)
            await bot.delete_message(msg)
        elif len(serv_perms) == 0:
            msg = await bot.say("No roles needed!")
            await asyncio.sleep(5)
            await bot.delete_message(msg)
        else:
            msg = await bot.say("You need to be: {}".format(serv_perms))
            await asyncio.sleep(5)
            await bot.delete_message(msg)


def load_credentials():
    with open('credentials.json') as f:
        return json.load(f)


if __name__ == '__main__':
    credentials = load_credentials()
    token = credentials['Token']
    try:
        bot.run(token)
    except KeyboardInterrupt:
        bot.stop()
    finally:
        bot.close()
