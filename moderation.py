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
            
                description="Please mention a user or provide a valid user ID", 
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
            embed = discord.Embed(
                description="Please mention a user or provide a valid user ID", 
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
            
        if member is None:
            embed = discord.Embed(title="❌ Error", description="Please specify a member to ban!", color=0xff0000)
            await ctx.send(embed=embed)
            return

        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            embed = discord.Embed(title="❌ Error", description="You cannot ban this member!", color=0xff0000)
            await ctx.send(embed=embed)
            return

        try:
            await member.ban(reason=reason)
            embed = discord.Embed(
                title="🔨 Member Banned",
                description=f"{member.mention} has been banned\n**Reason:** {reason}",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="❌ Error", description=f"Failed to ban member: {str(e)}", color=0xff0000)
            await ctx.send(embed=embed)

    @commands.command(name='kick')
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        # Check if user has proper permissions (bot owner, guild owner, or kick permission)
        if ctx.author.id != self.bot_owner_id and not ctx.author.guild_permissions.kick_members and ctx.author.id != ctx.guild.owner_id:
            embed = discord.Embed(
                title="❌ Permission Denied", 
                description="You need **Kick Members** permission to use this command!", 
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
            
        if member is None:
            embed = discord.Embed(title="❌ Error", description="Please specify a member to kick!", color=0xff0000)
            await ctx.send(embed=embed)
            return

        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            embed = discord.Embed(title="❌ Error", description="You cannot kick this member!", color=0xff0000)
            await ctx.send(embed=embed)
            return

        try:
            await member.kick(reason=reason)
            embed = discord.Embed(
                title="👢 Member Kicked",
                description=f"{member.mention} has been kicked\n**Reason:** {reason}",
                color=0xff9900
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="❌ Error", description=f"Failed to kick member: {str(e)}", color=0xff0000)
            await ctx.send(embed=embed)

    @commands.command(name='timeout')
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member = None, duration: str = "10m", *, reason: str = "No reason provided"):
        # Check if user has proper permissions (bot owner, guild owner, or moderate permission)
        if ctx.author.id != self.bot_owner_id and not ctx.author.guild_permissions.moderate_members and ctx.author.id != ctx.guild.owner_id:
            embed = discord.Embed(
                title="❌ Permission Denied", 
                description="You need **Timeout Members** permission to use this command!", 
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
            
        if member is None:
            embed = discord.Embed(title="❌ Error", description="Please specify a member to timeout!", color=0xff0000)
            await ctx.send(embed=embed)
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
            embed = discord.Embed(
                title="⏰ Member Timed Out",
                description=f"{member.mention} has been timed out for {duration}\n**Reason:** {reason}",
                color=0xff9900
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="❌ Error", description=f"Failed to timeout member: {str(e)}", color=0xff0000)
            await ctx.send(embed=embed)

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
                                await channel.guild.kick(entry.user, reason="Antinuke: Unauthorized bot deleted channel")
                            except:
                                pass
                else:
                    # Ban the user who deleted channel
                    await entry.user.ban(reason="Antinuke: Channel deletion detected")
                
                # Try to recreate the channel
                await channel.guild.create_text_channel(
                    name=channel.name,
                    category=channel.category,
                    position=channel.position,
                    reason="Antinuke: Restoring deleted channel"
                )
                
                # Send alert
                user_type = "Bot" if entry.user.bot else "User"
                embed = discord.Embed(
                    title="🛡️ Antinuke Triggered",
                    description=f"**{user_type} {entry.user.mention}** deleted channel and was banned\nChannel has been restored",
                    color=0xff0000
                )
                for ch in channel.guild.text_channels:
                    if ch.permissions_for(channel.guild.me).send_messages:
                        await ch.send(embed=embed)
                        break
                break
        except Exception as e:
            print(f"Antinuke error: {e}")

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        """Antinuke protection for role deletion"""
        guild_id = str(role.guild.id)
        if guild_id not in self.config or not self.config[guild_id].get('antinuke', False):
            return

        try:
            async for entry in role.guild.audit_logs(action=discord.AuditLogAction.role_delete, limit=1):
                # Get the member object to check permissions
                member = role.guild.get_member(entry.user.id)
                
                if member and member.guild_permissions.administrator:
                    continue
                
                # Check if it's a bot and if bots are not whitelisted
                if entry.user.bot:
                    # Ban bots that delete roles (unless they're whitelisted)
                    if guild_id not in self.whitelist or entry.user.id not in self.whitelist[guild_id]:
                        try:
                            await entry.user.ban(reason="Antinuke: Unauthorized bot deleted role")
                        except:
                            try:
                                await role.guild.kick(entry.user, reason="Antinuke: Unauthorized bot deleted role")
                            except:
                                pass
                else:
                    # Ban the user who deleted role
                    await entry.user.ban(reason="Antinuke: Role deletion detected")
                
                # Send alert
                user_type = "Bot" if entry.user.bot else "User"
                embed = discord.Embed(
                    title="🛡️ Antinuke Triggered",
                    description=f"**{user_type} {entry.user.mention}** deleted role '{role.name}' and was banned",
                    color=0xff0000
                )
                for ch in role.guild.text_channels:
                    if ch.permissions_for(role.guild.me).send_messages:
                        await ch.send(embed=embed)
                        break
                break
        except Exception as e:
            print(f"Antinuke error: {e}")

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        """Antinuke protection for mass banning"""
        guild_id = str(guild.id)
        if guild_id not in self.config or not self.config[guild_id].get('antinuke', False):
            return

        try:
            async for entry in guild.audit_logs(action=discord.AuditLogAction.ban, limit=1):
                # Get the member object to check permissions
                member = guild.get_member(entry.user.id)
                
                if member and member.guild_permissions.administrator:
                    continue
                
                # Check if user has banned multiple people recently
                ban_count = 0
                async for ban_entry in guild.audit_logs(action=discord.AuditLogAction.ban, limit=5):
                    if ban_entry.user == entry.user:
                        ban_count += 1
                
                if ban_count >= 3:  # If banned 3+ people recently
                    await entry.user.ban(reason="Antinuke: Mass ban detected")
                    
                    # Send alert
                    user_type = "Bot" if entry.user.bot else "User"
                    embed = discord.Embed(
                        title="🛡️ Antinuke Triggered",
                        description=f"**{user_type} {entry.user.mention}** mass banned members and was banned",
                        color=0xff0000
                    )
                    for ch in guild.text_channels:
                        if ch.permissions_for(guild.me).send_messages:
                            await ch.send(embed=embed)
                            break
                break
        except Exception as e:
            print(f"Antinuke error: {e}")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Antinuke protection for unauthorized bot addition"""
        guild_id = str(member.guild.id)
        
        # Check if antinuke is enabled
        if guild_id not in self.config or not self.config[guild_id].get('antinuke', False):
            return
        
        # Only check for bots
        if not member.bot:
            return
        
        try:
            # Check if bot is whitelisted
            is_whitelisted = (guild_id in self.whitelist and 
                            member.id in self.whitelist[guild_id])
            
            if not is_whitelisted:
                # Find who added the bot
                async for entry in member.guild.audit_logs(action=discord.AuditLogAction.bot_add, limit=1):
                    if entry.target.id == member.id:
                        # Check if the person who added bot is admin
                        member_in_guild = member.guild.get_member(entry.user.id)
                        if not member_in_guild or not member_in_guild.guild_permissions.administrator:
                            # Kick the unauthorized bot
                            await member.kick(reason="Antinuke: Unauthorized bot addition")
                            
                            # Send alert
                            embed = discord.Embed(
                                title="🛡️ Antinuke Triggered",
                                description=f"**{entry.user.mention}** added unauthorized bot **{member.mention}**\nBot has been kicked",
                                color=0xff0000
                            )
                            embed.add_field(name="Bot Name", value=member.name, inline=True)
                            embed.add_field(name="Added by", value=entry.user.mention, inline=True)
                            embed.add_field(name="Action", value="Bot kicked from server", inline=False)
                            
                            for ch in member.guild.text_channels:
                                if ch.permissions_for(member.guild.me).send_messages:
                                    await ch.send(embed=embed)
                                    break
                        break
        except Exception as e:
            print(f"Bot addition protection error: {e}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        guild_id = str(message.guild.id)

        # Check for @everyone or @here pings by non-whitelisted users
        if ("@everyone" in message.content or "@here" in message.content):
            # Check if user is whitelisted
            is_whitelisted = (guild_id in self.whitelist and 
                            message.author.id in self.whitelist[guild_id])

            # Check if user has administrator permissions
            has_admin = message.author.guild_permissions.administrator

            if not is_whitelisted and not has_admin:
                try:
                    # Hide the channel from @everyone
                    overwrite = message.channel.overwrites_for(message.guild.default_role)
                    overwrite.view_channel = False
                    await message.channel.set_permissions(message.guild.default_role, overwrite=overwrite)

                    # Delete the message
                    await message.delete()

                    # Send warning to admins
                    embed = discord.Embed(
                        title="🚨 Ping Security Triggered",
                        description=f"**{message.author.mention}** tried to ping @everyone/@here\n"
                                   f"Channel {message.channel.mention} has been hidden",
                        color=0xff0000
                    )
                    embed.add_field(name="Message Content", value=message.content[:1000], inline=False)
                    embed.add_field(name="Action", value="Channel hidden from @everyone\nMessage deleted", inline=False)

                    # Try to send to a log channel or the first available channel
                    for channel in message.guild.text_channels:
                        if channel.permissions_for(message.guild.me).send_messages:
                            await channel.send(embed=embed)
                            break

                except Exception as e:
                    print(f"Ping security error: {e}")

    @commands.command(name='hide')
    async def hide_channel(self, ctx):
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
        overwrite.view_channel = False
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

        embed = discord.Embed(
            title="🙈 Channel Hidden",
            description=f"This channel is now hidden from everyone",
            color=0xff9900
        )
        await ctx.send(embed=embed)

    @commands.command(name='unhide')
    async def unhide_channel(self, ctx):
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
        overwrite.view_channel = None
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

        embed = discord.Embed(
            title="👁️ Channel Unhidden",
            description=f"This channel is now visible to everyone",
            color=0x00ff00
        )
        await ctx.send(embed=embed)

    @commands.command(name='nuke')
    async def nuke_channel(self, ctx):
        # Check if user is bot owner or has administrator permission
        if ctx.author.id != self.bot_owner_id and not ctx.author.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Permission Denied", 
                description="You need **Administrator** permission to use this command!", 
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        channel = ctx.channel

        # Create a confirmation embed
        embed = discord.Embed(
            title="⚠️ Nuke Channel Confirmation",
            description="Are you sure you want to nuke this channel? This will delete all messages!",
            color=0xff0000
        )

        # Send confirmation message
        confirm_msg = await ctx.send(embed=embed)
        await confirm_msg.add_reaction("✅")
        await confirm_msg.add_reaction("❌")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["✅", "❌"] and reaction.message.id == confirm_msg.id

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)

            if str(reaction.emoji) == "✅":
                # Clone the channel
                new_channel = await channel.clone(reason="Channel nuked")
                await new_channel.edit(position=channel.position)

                # Delete the old channel
                await channel.delete(reason="Channel nuked")

                # Send success message to new channel
                embed = discord.Embed(
                    title="💥 Channel Nuked",
                    description="Channel has been successfully nuked!",
                    color=0x00ff00
                )
                await new_channel.send(embed=embed)
            else:
                await confirm_msg.edit(embed=discord.Embed(
                    title="❌ Nuke Cancelled",
                    description="Channel nuke has been cancelled",
                    color=0x00ff00
                ))

        except asyncio.TimeoutError:
            await confirm_msg.edit(embed=discord.Embed(
                title="⏰ Timeout",
                description="Nuke confirmation timed out",
                color=0xff9900
            ))

    @commands.command(name='unban')
    async def unban(self, ctx, user_id: int = None):
        # Check if user is bot owner or has ban members permission
        if ctx.author.id != self.bot_owner_id and not ctx.author.guild_permissions.ban_members:
            embed = discord.Embed(
                title="❌ Permission Denied", 
                description="You need **Ban Members** permission to use this command!", 
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        if user_id is None:
            embed = discord.Embed(title="❌ Error", description="Please provide a user ID!", color=0xff0000)
            await ctx.send(embed=embed)
            return

        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user)
            embed = discord.Embed(
                title="✅ User Unbanned",
                description=f"{user.mention} has been unbanned",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="❌ Error", description=f"Failed to unban user: {str(e)}", color=0xff0000)
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
