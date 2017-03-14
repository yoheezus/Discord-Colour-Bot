import json
import discord
from discord.ext import commands

description = '''A bot that allows users to choose their own name colour through use of a custom role based on id.'''


bot = commands.Bot(command_prefix='?', description=description)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    if not hasattr(bot, 'uptime'): 
        bot.uptime = datetime.datetime.utcnow()


@bot.event
async def on_member_remove(member):
    server = member.server
    role = discord.utils.get(server.roles, name="ColourID"+member.id)
    await bot.delete_role(server, role)

@bot.command(aliases=['nickcolor', 'nc'], pass_context=True)
async def nickcolour(ctx, value: discord.Colour):
    userauthor = ctx.message.author.id
    dserver = ctx.message.server
    if not discord.utils.get(dserver.roles, name="ColourID"+userauthor):
        try:
            role = await bot.create_role(dserver, name="ColourID"+userauthor, colour=value)
            await bot.add_roles(ctx.message.author, role)
        except PermissionError:
            await bot.say('Colourbot cannot create/edit roles.')
    else:
        try:
            role = discord.utils.get(dserver.roles, name="ColourID"+userauthor)
            await bot.add_roles(ctx.message.author, role)
            await bot.edit_role(dserver, role, colour=value)
        except PermissionError:
            await bot.say('Colourbot cannot create/edit roles.')
            
@bot.command(aliases=['cc'], pass_context=True)
async def currentcolour(ctx):
    userauthor = ctx.message.author
    rolecolour = userauthor.colour
    await bot.reply('current colour is: {0}'.format(rolecolour))
    
@commands.command()
async def uptime():
    await bot.say('{}'.format(datetime.datetime.utcnow() - bot.uptime))
    
try:
    bot.run('TOKEN HERE')
except KeyboardInterrupt:
    bot.stop()
finally:
    bot.close()
