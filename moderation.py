import discord
from discord.ext import commands
import asyncio
import json
import os
from datetime import datetime, timedelta

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_file = "moderation_config.json"
        self.whitelist_file = "whitelist_users.json"
        self.bot_owner_id = 1049708274032853003  # Bot owner ID
        self.load_config()
        self.load_whitelist()

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {}

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    def load_whitelist(self):
        if os.path.exists(self.whitelist_file):
            with open(self.whitelist_file, 'r') as f:
                self.whitelist = json.load(f)
        else:
            self.whitelist = {}

    def save_whitelist(self):
        with open(self.whitelist_file, 'w') as f:
            json.dump(self.whitelist, f, indent=4)

    @commands.command(name='antinuke')
    async def antinuke(self, ctx, status: str = None):
        # Check if user is bot owner or has administrator permissions
        if ctx.author.id != self.bot_owner_id and not ctx.author.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Permission Denied", 
                description="You need **Administrator** permission to use this command!", 
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        if status not in ['on', 'off']:
            embed = discord.Embed(title="❌ Error", description="Use `!antinuke on` or `!antinuke off`", color=0xff0000)
            await ctx.send(embed=embed)
            return

        guild_id = str(ctx.guild.id)
        if guild_id not in self.config:
            self.config[guild_id] = {}

        self.config[guild_id]['antinuke'] = status == 'on'
        self.save_config()

        # Update bot status when antinuke is enabled
        if status == 'on':
            await self.bot.change_presence(
                activity=discord.Streaming(
                    name=f"🛡️ Antinuke Active | {len(self.bot.guilds)} servers",
                    url="https://www.twitch.tv/discord"
                ),
                status=discord.Status.online
            )

        embed = discord.Embed(
            title="✅ Antinuke Updated",
            description=f"Antinuke has been turned **{status}** for **ALL CHANNELS** in this server\n"
                       f"🛡️ Protection enabled for:\n"
                       f"• Channel deletion/creation\n"
                       f"• Role deletion/creation\n"
                       f"• Mass banning\n"
                       f"• Unauthorized bot addition",
            color=0x00ff00
        )
        embed.add_field(name="Server", value=ctx.guild.name, inline=True)
        embed.add_field(name="Total Channels Protected", value=len(ctx.guild.channels), inline=True)
        embed.add_field(name="Status", value="🟢 ACTIVE" if status == 'on' else "🔴 DISABLED", inline=True)
        await ctx.send(embed=embed)

    @commands.command(name='automod')
    async def automod(self, ctx, status: str = None):
        # Check if user is bot owner or has administrator permissions
        if ctx.author.id != self.bot_owner_id and not ctx.author.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Permission Denied", 
                description="You need **Administrator** permission to use this command!", 
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        if status not in ['on', 'off']:
            embed = discord.Embed(title="❌ Error", description="Use `!automod on` or `!automod off`", color=0xff0000)
            await ctx.send(embed=embed)
            return

        guild_id = str(ctx.guild.id)
        if guild_id not in self.config:
            self.config[guild_id] = {}

        self.config[guild_id]['automod'] = status == 'on'
        self.save_config()

        embed = discord.Embed(
            title="✅ Automod Updated",
            description=f"Automoderation has been turned **{status}**",
            color=0x00ff00
        )
        await ctx.send(embed=embed)

    @commands.command(name='ban')
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        # Check if user has proper permissions (bot owner, guild owner, or ban permission)
        if ctx.author.id != self.bot_owner_id and not ctx.author.guild_permissions.ban_members and ctx.author.id != ctx.guild.owner_id:
            await ctx.send("❌ You need **Ban Members** permission to use this command!")
            return

        if member is None:
            await ctx.send("❌ Please specify a member to ban!")
            return

        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send("❌ You cannot ban this member!")
            return

        try:
            await member.ban(reason=reason)
            await ctx.send(f"🔨 **{member.name}** has been banned from the server\nReason: {reason}\nBanned by: {ctx.author.name}")
        except Exception as e:
            await ctx.send(f"❌ Failed to ban member: {str(e)}")

    @commands.command(name='kick')
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        # Check if user has proper permissions (bot owner, guild owner, or kick permission)
        if ctx.author.id != self.bot_owner_id and not ctx.author.guild_permissions.kick_members and ctx.author.id != ctx.guild.owner_id:
            await ctx.send("❌ You need **Kick Members** permission to use this command!")
            return

        if member is None:
            await ctx.send("❌ Please specify a member to kick!")
            return

        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send("❌ You cannot kick this member!")
            return

        try:
            await member.kick(reason=reason)
            await ctx.send(f"👢 **{member.name}** has been kicked from the server\nReason: {reason}\nKicked by: {ctx.author.name}")
        except Exception as e:
            await ctx.send(f"❌ Failed to kick member: {str(e)}")

    @commands.command(name='timeout')
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member = None, duration: str = "10m", *, reason: str = "No reason provided"):
        # Check if user has proper permissions (bot owner, guild owner, or moderate permission)
        if ctx.author.id != self.bot_owner_id and not ctx.author.guild_permissions.moderate_members and ctx.author.id != ctx.guild.owner_id:
            await ctx.send("❌ You need **Timeout Members** permission to use this command!")
            return

        if member is None:
            await ctx.send("❌ Please specify a member to timeout!")
            return

        # Parse duration
        time_units = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
        try:
            if duration[-1] in time_units:
                seconds = int(duration[:-1]) * time_units[duration[-1]]
            else:
                seconds = int(duration) * 60  # Default to minutes
        except:
            seconds = 600  # Default 10 minutes

        timeout_until = discord.utils.utcnow() + timedelta(seconds=seconds)

        try:
            await member.timeout(timeout_until, reason=reason)
            await ctx.send(f"⏰ **{member.name}** has been timed out for {duration}\nReason: {reason}\nTimed out by: {ctx.author.name}")
        except Exception as e:
            await ctx.send(f"❌ Failed to timeout member: {str(e)}")

    @commands.command(name='clear')
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int = 10):
        # Check if user has proper permissions (bot owner, guild owner, or manage messages permission)
        if ctx.author.id != self.bot_owner_id and not ctx.author.guild_permissions.manage_messages and ctx.author.id != ctx.guild.owner_id:
            embed = discord.Embed(
                title="❌ Permission Denied", 
                description="You need **Manage Messages** permission to use this command!", 
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return

        if amount > 100:
            amount = 100

        deleted = await ctx.channel.purge(limit=amount + 1)

        embed = discord.Embed(
            title="🧹 Messages Cleared",
            description=f"Deleted {len(deleted) - 1} messages",
            color=0x00ff00
        )
        msg = await ctx.send(embed=embed)
        await asyncio.sleep(3)
        await msg.delete()

    @commands.command(name='lock')
    async def lock(self, ctx):
        # Check if user is bot owner or has manage channels permission
        if ctx.author.id != self.bot_owner_id and not ctx.author.guild_permissions.manage_channels:
            embed = discord.Embed(
                title="❌ Permission Denied", 
                description="You need **Manage Channels** permission to use this command!", 
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        channel = ctx.channel

        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

        embed = discord.Embed(
            title="🔒 Channel Locked",
            description=f"This channel has been locked",
            color=0xff0000
        )
        await ctx.send(embed=embed)

    @commands.command(name='unlock')
    async def unlock(self, ctx):
        # Check if user is bot owner or has manage channels permission
        if ctx.author.id != self.bot_owner_id and not ctx.author.guild_permissions.manage_channels:
            embed = discord.Embed(
                title="❌ Permission Denied", 
                description="You need **Manage Channels** permission to use this command!", 
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        channel = ctx.channel

        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = None
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

        embed = discord.Embed(
            title="🔓 Channel Unlocked",
            description=f"This channel has been unlocked",
            color=0x00ff00
        )
        await ctx.send(embed=embed)

    @commands.command(name='slowmode')
    async def slowmode(self, ctx, seconds: int = 0):
        # Check if user is bot owner or has manage channels permission
        if ctx.author.id != self.bot_owner_id and not ctx.author.guild_permissions.manage_channels:
            embed = discord.Embed(
                title="❌ Permission Denied", 
                description="You need **Manage Channels** permission to use this command!", 
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        await ctx.channel.edit(slowmode_delay=seconds)

        if seconds == 0:
            embed = discord.Embed(
                title="⏱️ Slowmode Disabled",
                description="Slowmode has been disabled for this channel",
                color=0x00ff00
            )
        else:
            embed = discord.Embed(
                title="⏱️ Slowmode Enabled",
                description=f"Slowmode set to {seconds} seconds",
                color=0x00ff00
            )

        await ctx.send(embed=embed)

    @commands.command(name='whitelist')
    async def whitelist_user(self, ctx, user: discord.Member = None):
        # Check if user is bot owner or has administrator permission
        if ctx.author.id != self.bot_owner_id and not ctx.author.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Permission Denied", 
                description="You need **Administrator** permission to use this command!", 
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        if user is None:
            embed = discord.Embed(title="❌ Error", description="Please specify a user to whitelist!", color=0xff0000)
            await ctx.send(embed=embed)
            return

        guild_id = str(ctx.guild.id)
        if guild_id not in self.whitelist:
            self.whitelist[guild_id] = []

        if user.id in self.whitelist[guild_id]:
            embed = discord.Embed(title="❌ Error", description="User is already whitelisted!", color=0xff0000)
            await ctx.send(embed=embed)
            return

        self.whitelist[guild_id].append(user.id)
        self.save_whitelist()

        embed = discord.Embed(
            title="✅ User Whitelisted",
            description=f"{user.mention} has been whitelisted for ping security",
            color=0x00ff00
        )
        await ctx.send(embed=embed)

    @commands.command(name='unwhitelist')
    async def unwhitelist_user(self, ctx, user: discord.Member = None):
        # Check if user is bot owner or has administrator permission
        if ctx.author.id != self.bot_owner_id and not ctx.author.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Permission Denied", 
                description="You need **Administrator** permission to use this command!", 
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        if user is None:
            embed = discord.Embed(title="❌ Error", description="Please specify a user to unwhitelist!", color=0xff0000)
            await ctx.send(embed=embed)
            return

        guild_id = str(ctx.guild.id)
        if guild_id not in self.whitelist or user.id not in self.whitelist[guild_id]:
            embed = discord.Embed(title="❌ Error", description="User is not whitelisted!", color=0xff0000)
            await ctx.send(embed=embed)
            return

        self.whitelist[guild_id].remove(user.id)
        self.save_whitelist()

        embed = discord.Embed(
            title="✅ User Unwhitelisted",
            description=f"{user.mention} has been removed from ping security whitelist",
            color=0x00ff00
        )
        await ctx.send(embed=embed)

    @commands.command(name='whitelistview')
    async def whitelist_view(self, ctx):
        # Check if user is bot owner or has administrator permission
        if ctx.author.id != self.bot_owner_id and not ctx.author.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Permission Denied", 
                description="You need **Administrator** permission to use this command!", 
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        guild_id = str(ctx.guild.id)
        if guild_id not in self.whitelist or not self.whitelist[guild_id]:
            embed = discord.Embed(title="📝 Security Whitelist", description="No users/bots are whitelisted", color=0x00ff00)
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(title="📝 Security Whitelist", color=0x00ff00)

        user_list = []
        bot_list = []
        for user_id in self.whitelist[guild_id]:
            try:
                user = await self.bot.fetch_user(user_id)
                if user.bot:
                    bot_list.append(f"🤖 {user.name}")
                else:
                    user_list.append(f"👤 {user.name}#{user.discriminator}")
            except:
                user_list.append(f"❓ Unknown User ({user_id})")

        all_users = user_list + bot_list
        embed.description = "\n".join(all_users) if all_users else "No users/bots found"
        await ctx.send(embed=embed)

    @commands.command(name='botwhitelist')
    async def botwhitelist(self, ctx, bot_id: int = None):
        # Check if user is bot owner or has administrator permission
        if ctx.author.id != self.bot_owner_id and not ctx.author.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Permission Denied", 
                description="You need **Administrator** permission to use this command!", 
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        if bot_id is None:
            embed = discord.Embed(title="❌ Error", description="Please provide a bot ID to whitelist!", color=0xff0000)
            await ctx.send(embed=embed)
            return

        try:
            bot_user = await self.bot.fetch_user(bot_id)
            if not bot_user.bot:
                embed = discord.Embed(title="❌ Error", description="This ID belongs to a user, not a bot!", color=0xff0000)
                await ctx.send(embed=embed)
                return

            guild_id = str(ctx.guild.id)
            if guild_id not in self.whitelist:
                self.whitelist[guild_id] = []

            if bot_id in self.whitelist[guild_id]:
                embed = discord.Embed(title="❌ Error", description="Bot is already whitelisted!", color=0xff0000)
                await ctx.send(embed=embed)
                return

            self.whitelist[guild_id].append(bot_id)
            self.save_whitelist()

            embed = discord.Embed(
                title="✅ Bot Whitelisted",
                description=f"🤖 **{bot_user.name}** has been whitelisted for antinuke protection",
                color=0x00ff00
            )
            embed.add_field(name="Bot ID", value=bot_id, inline=True)
            embed.add_field(name="Status", value="Protected from antinuke", inline=True)
            await ctx.send(embed=embed)

        except discord.NotFound:
            embed = discord.Embed(title="❌ Error", description="Bot not found with that ID!", color=0xff0000)
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="❌ Error", description=f"Failed to whitelist bot: {str(e)}", color=0xff0000)
            await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        """Antinuke protection for channel deletion"""
        guild_id = str(channel.guild.id)
        if guild_id not in self.config or not self.config[guild_id].get('antinuke', False):
            return

        try:
            async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1):
                # Get the member object to check permissions
                member = channel.guild.get_member(entry.user.id)

                # Skip if user is administrator OR if it's a whitelisted bot
                if member and member.guild_permissions.administrator:
                    continue

                # Check if it's a bot and if bots are not whitelisted
                if entry.user.bot:
                    # Ban bots that delete channels (unless they're whitelisted)
                    if guild_id not in self.whitelist or entry.user.id not in self.whitelist[guild_id]:
                        try:
                            await entry.user.ban(reason="Antinuke: Unauthorized bot deleted channel")
                        except:
                            # If can't ban, try to kick
                            try:
                                await channel.guild.kick(entry.user, reason="Antinuke: Unauthorized bot deleted channe
