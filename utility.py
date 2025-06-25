import discord
from discord.ext import commands
import json, os, asyncio
from datetime import datetime
import platform

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.afk_file = "afk_users.json"
        self.bot_owner_id = 1049708274032853003
        self.afk_users = self.load_afk_users()

    def load_afk_users(self):
        if os.path.exists(self.afk_file):
            with open(self.afk_file, 'r') as f:
                return json.load(f)
        return {}

    def save_afk_users(self):
        with open(self.afk_file, 'w') as f:
            json.dump(self.afk_users, f, indent=4)

    @commands.command(name="ping")
    async def ping(self, ctx):
        await ctx.send(f"🏓 Pong! `{round(self.bot.latency * 1000)}ms`")

    @commands.command(name="avatar", aliases=["av"])
    async def avatar(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        embed = discord.Embed(title=f"{member.display_name}'s Avatar", color=discord.Color.green())
        embed.set_image(url=member.avatar.url if member.avatar else member.default_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="serverinfo")
    async def serverinfo(self, ctx):
        guild = ctx.guild
        embed = discord.Embed(title=f"📊 {guild.name} Server Info", color=discord.Color.green())
        embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
        embed.add_field(name="Members", value=guild.member_count, inline=True)
        embed.add_field(name="Created", value=guild.created_at.strftime("%B %d, %Y"), inline=True)
        embed.add_field(name="Channels", value=len(guild.channels), inline=True)
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        embed.add_field(name="Boosts", value=guild.premium_subscription_count, inline=True)
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        await ctx.send(embed=embed)

    @commands.command(name="userinfo", aliases=["ui"])
    async def userinfo(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        embed = discord.Embed(title=f"👤 {member}", color=discord.Color.green())
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Joined", value=member.joined_at.strftime('%b %d, %Y'), inline=True)
        embed.add_field(name="Created", value=member.created_at.strftime('%b %d, %Y'), inline=True)
        embed.add_field(name="Top Role", value=member.top_role.mention, inline=True)
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="botinfo")
    async def botinfo(self, ctx):
        embed = discord.Embed(title="🤖 Bot Info", color=discord.Color.green())
        embed.add_field(name="Bot Name", value=self.bot.user.name, inline=True)
        embed.add_field(name="Servers", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Users", value=len(self.bot.users), inline=True)
        embed.add_field(name="Python", value=platform.python_version(), inline=True)
        embed.add_field(name="Library", value=discord.__version__, inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="membercount", aliases=["mc"])
    async def membercount(self, ctx):
        total = ctx.guild.member_count
        humans = len([m for m in ctx.guild.members if not m.bot])
        bots = len([m for m in ctx.guild.members if m.bot])
        embed = discord.Embed(title="👥 Member Count", color=discord.Color.green())
        embed.add_field(name="Total", value=total, inline=True)
        embed.add_field(name="Humans", value=Online, inline=True)
        embed.add_field(name="Bots", value=bots, inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="afk")
    async def afk(self, ctx, *, reason="AFK"):
        self.afk_users[str(ctx.author.id)] = {"reason": reason, "time": datetime.now().isoformat()}
        self.save_afk_users()
        await ctx.send(f"😴 {ctx.author.mention} is now AFK: {reason}")

    @commands.command(name="unafk")
    async def unafk(self, ctx):
        uid = str(ctx.author.id)
        if uid in self.afk_users:
            del self.afk_users[uid]
            self.save_afk_users()
            await ctx.send(f"👋 Welcome back {ctx.author.mention}, you are no longer AFK.")
        else:
            await ctx.send("❌ You are not AFK!")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Skip if it's a command (starts with prefix)
        ctx = await self.bot.get_context(message)
        if ctx.valid:
            return

        # Check if the author is AFK and remove AFK status (only for non-commands)
        uid = str(message.author.id)
        if uid in self.afk_users:
            del self.afk_users[uid]
            self.save_afk_users()
            try:
                await message.channel.send(f"👋 Welcome back {message.author.mention}, you are no longer AFK.", delete_after=5)
            except:
                pass

        # Show AFK status when someone mentions an AFK user
        for user in message.mentions:
            mentioned_uid = str(user.id)
            if mentioned_uid in self.afk_users and mentioned_uid != uid:
                reason = self.afk_users[mentioned_uid]['reason']
                try:
                    await message.channel.send(f"😴 {user.display_name} is AFK: {reason}", delete_after=10)
                except:
                    pass

    @commands.command(name="invite")
    async def invite(self, ctx):
        invite_url = f"https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot"
        await ctx.send(f"📨 [Invite Me]({invite_url})")

    @commands.command(name="purgemsg", aliases=["clearmsg"])
    async def clear_messages(self, ctx, amount: int = 10):
        if ctx.author.id != self.bot_owner_id and not ctx.author.guild_permissions.manage_messages:
            return await ctx.send("❌ You need Manage Messages permission.")
        amount = min(amount, 100)
        deleted = await ctx.channel.purge(limit=amount + 1)
        msg = await ctx.send(f"🧹 Deleted `{len(deleted) - 1}` messages.")
        await asyncio.sleep(3)
        await msg.delete()

async def setup(bot):
    await bot.add_cog(Utility(bot))
