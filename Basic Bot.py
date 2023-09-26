import discord
from discord.ext import commands, tasks
import asyncio

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandError):
        return

@bot.check
async def has_admin_permissions(ctx):
    if ctx.command:
        try:
            if ctx.author.guild_permissions.administrator:
                return True
        except AttributeError:
            pass
    return False

@bot.command()
async def say(ctx, *, message):
    await ctx.send(message)

@bot.command()
async def ban(ctx, member: discord.Member = None, *, reason=None):
    if member is None:
        await ctx.send("Please provide a user to ban. Usage: `!ban [user mention or user ID] [reason]`")
        return

    await member.ban(reason=reason)
    await ctx.send(f'{member.mention} has been banned.')

@bot.command()
async def unban(ctx, user_id=None):
    if user_id is None:
        await ctx.send("Please provide a user ID to unban. Usage: `!unban [user ID]`")
        return

    try:
        user_id = int(user_id)
    except ValueError:
        await ctx.send("Invalid user ID provided.")
        return

    user = discord.Object(id=user_id)

    try:
        await ctx.guild.unban(user)
        await ctx.send(f'User with ID {user_id} has been unbanned.')
    except discord.NotFound:
        await ctx.send(f'User with ID {user_id} not found in the ban list.')

@bot.command()
async def mute(ctx, member: discord.Member = None, time_minutes: int = 0, *, reason=None):
    if member is None:
        await ctx.send("Please provide a user to mute. Usage: `!mute [user mention or user ID] [time in minutes] [reason]`")
        return

    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not muted_role:
        muted_role = await ctx.guild.create_role(name="Muted", permissions=discord.Permissions.none())

        for channel in ctx.guild.text_channels:
            await channel.set_permissions(muted_role, send_messages=False)

    await member.add_roles(muted_role, reason=reason)
    await ctx.send(f'{member.mention} has been muted for {time_minutes} minutes.')

    if time_minutes > 0:
        await asyncio.sleep(time_minutes * 60)
        await member.remove_roles(muted_role, reason="Mute duration expired.")

bot_token = input("Enter your bot token: ")
bot.run(bot_token)
