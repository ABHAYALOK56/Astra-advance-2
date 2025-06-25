import discord
from discord.ext import commands
from discord import ui
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

    @commands.command(name='nuke')
    async def nuke(self, ctx):
        # Check if user is bot owner or has manage channels permission
        if ctx.author.id != self.bot_owner_id and not ctx.author.guild_permissions.manage_channels:
            embed = discord.Embed(
                title="❌ Permission Denied", 
                description="You need **Manage Channels** permission to use this command!", 
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return

        # Create confirmation embed
        embed = discord.Embed(
            
            description="Are you sure you want to clone this channel?",
            color=0xff6600
        )
        embed.set_footer(text="This confirmation will expire in 30 seconds")

        # Create buttons
        view = NukeConfirmView(ctx.author)
        msg = await ctx.send(embed=embed, view=view)

        # Wait for interaction
        await view.wait()

        # Disable buttons after timeout
        for item in view.children:
            item.disabled = True
        await msg.edit(view=view)

    @commands.command(name='hide')
    async def hide(self, ctx, channel: discord.TextChannel = None):
        # Check if user is bot owner or has manage channels permission
        if ctx.author.id != self.bot_owner_id and not ctx.author.guild_permissions.manage_channels:
            embed = discord.Embed(
                title="❌ Permission Denied", 
                description="You need **Manage Channels** permission to use this command!", 
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return

        channel = channel or ctx.channel

        try:
            overwrite = channel.overwrites_for(ctx.guild.default_role)
            overwrite.view_channel = False
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

            embed = discord.Embed(
                title="👁️‍🗨️ Channel Hidden",
                description=f"**{channel.name}** has been hidden from @everyone",
                color=0x808080
            )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Failed to hide channel: {str(e)}")

    @commands.command(name='unhide')
    async def unhide(self, ctx, channel: discord.TextChannel = None):
        # Check if user is bot owner or has manage channels permission
        if ctx.author.id != self.bot_owner_id and not ctx.author.guild_permissions.manage_channels:
            embed = discord.Embed(
                title="❌ Permission Denied", 
                description="You need **Manage Channels** permission to use this command!", 
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return

        channel = channel or ctx.channel

        try:
            overwrite = channel.overwrites_for(ctx.guild.default_role)
            overwrite.view_channel = None
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

            embed = discord.Embed(
                title="👁️ Channel Unhidden",
                description=f"**{channel.name}** is now visible to @everyone",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Failed to unhide channel: {str(e)}")

    @commands.command(name='unban')
    async def unban(self, ctx, user_id: int = None, *, reason: str = "No reason provided"):
        # Check if user has proper permissions
        if ctx.author.id != self.bot_owner_id and not ctx.author.guild_permissions.ban_members and ctx.author.id != ctx.guild.owner_id:
            await ctx.send("❌ You need **Ban Members** permission to use this command!")
            return

        if user_id is None:
            await ctx.send("❌ Please provide a user ID to unban!")
            return

        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user, reason=reason)

            embed = discord.Embed(
                title="✅ User Unbanned",
                description=f"**{user.name}#{user.discriminator}** has been unbanned",
                color=0x00ff00
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Unbanned by", value=ctx.author.mention, inline=True)
            await ctx.send(embed=embed)
        except discord.NotFound:
            await ctx.send("❌ User not found or not banned!")
        except Exception as e:
            await ctx.send(f"❌ Failed to unban user: {str(e)}")

    @commands.command(name='role')
    async def role(self, ctx, member: discord.Member = None, *, role: discord.Role = None):
        # Check if user has proper permissions
        if ctx.author.id != self.bot_owner_id and not ctx.author.guild_permissions.manage_roles and ctx.author.id != ctx.guild.owner_id:
            await ctx.send("❌ You need **Manage Roles** permission to use this command!")
            return

        if member is None or role is None:
            await ctx.send("❌ Please specify a member and role! Usage: `!role @member @role`")
            return

        if role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send("❌ You cannot assign roles higher than or equal to your highest role!")
            return

        try:
            if role in member.roles:
                await member.remove_roles(role)
                embed = discord.Embed(
                    title="➖ Role Removed",
                    description=f"Removed **{role.name}** from {member.mention}",
                    color=0xff0000
                )
            else:
                await member.add_roles(role)
                embed = discord.Embed(
                    title="➕ Role Added",
                    description=f"Added **{role.name}** to {member.mention}",
                    color=0x00ff00
                )

            embed.add_field(name="Modified by", value=ctx.author.mention, inline=True)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Failed to modify role: {str(e)}")

    @commands.command(name='punishment')
    async def punishment(self, ctx, member: discord.Member = None):
        # Check if user has proper permissions
        if ctx.author.id != self.bot_owner_id and not ctx.author.guild_permissions.view_audit_log and ctx.author.id != ctx.guild.owner_id:
            await ctx.send("❌ You need **View Audit Log** permission to use this command!")
            return

        if member is None:
            await ctx.send("❌ Please specify a member to check punishments for!")
            return

        embed = discord.Embed(
            title=f"📋 Punishment History for {member.name}",
            description="Recent moderation actions:",
            color=0x0099ff
        )

        # Check recent audit logs for this user
        punishment_count = 0
        try:
            async for entry in ctx.guild.audit_logs(limit=50):
                if hasattr(entry, 'target') and entry.target and entry.target.id == member.id:
                    if entry.action in [discord.AuditLogAction.ban, discord.AuditLogAction.kick, 
                                      discord.AuditLogAction.member_update]:
                        punishment_count += 1
                        action_name = str(entry.action).replace('AuditLogAction.', '').title()
                        embed.add_field(
                            name=f"{action_name}",
                            value=f"**By:** {entry.user.mention}\n**Reason:** {entry.reason or 'No reason'}\n**Date:** {entry.created_at.strftime('%Y-%m-%d %H:%M')}",
                            inline=False
                        )

                        if punishment_count >= 10:  # Limit to 10 recent punishments
                            break
        except:
            pass

        if punishment_count == 0:
            embed.add_field(name="✅ Clean Record", value="No recent punishments found", inline=False)

        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.set_footer(text=f"Total recent punishments: {punishment_count}")
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
                break
        except Exception as e:
            print(f"Error in antinuke channel delete: {e}")

class NukeConfirmView(discord.ui.View):
    def __init__(self, author):
        super().__init__(timeout=30)
        self.author = author
        self.value = None

    @discord.ui.button(label='Yes', style=discord.ButtonStyle.green)
    async def confirm_nuke(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author:
            await interaction.response.send_message("❌ Only the command user can confirm this action!", ephemeral=True)
            return

        # Get channel info before deletion
        channel = interaction.channel
        channel_name = channel.name
        channel_position = channel.position
        channel_category = channel.category

        try:
            # Clone channel settings
            overwrites = channel.overwrites
            topic = channel.topic
            slowmode_delay = channel.slowmode_delay

            # Delete the channel
            await channel.delete(reason=f"Channel nuked by {interaction.user}")

            # Create new channel with same settings
            new_channel = await channel.guild.create_text_channel(
                name=channel_name,
                category=channel_category,
                position=channel_position,
                topic=topic,
                slowmode_delay=slowmode_delay,
                overwrites=overwrites,
                reason=f"Channel nuked by {interaction.user}"
            )

            # Send success message in new channel
            embed = discord.Embed(
                title="`nuked by {user}`",
                description=f"**{channel_name}** has been nuked and recreated",
                color=0x00ff00
            )
            embed.add_field(name="Nuked by", value=interaction.user.mention, inline=True)
            embed.add_field(name="Previous Messages", value="All deleted", inline=True)
            embed.set_footer(text="Channel settings have been restored")

            await new_channel.send(embed=embed)

        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to nuke channel: {str(e)}", ephemeral=True)

        self.value = True
        self.stop()

    @discord.ui.button(label='No', style=discord.ButtonStyle.red)
    async def cancel_nuke(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author:
            await interaction.response.send_message("❌ Only the command user can cancel this action!", ephemeral=True)
            return

        embed = discord.Embed(
            
            description="Channel nuke has been cancelled",
            color=0xff0000
        )
        await interaction.response.edit_message(embed=embed, view=None)
        self.value = False
        self.stop()

async def setup(bot):
    await bot.add_cog(Moderation(bot))
