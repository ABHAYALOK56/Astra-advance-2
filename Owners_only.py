import discord
from discord.ext import commands
import json
import os

class OwnersOnly(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.premium_file = "premium_users.json"
        self.ip_ban_file = "ip_banned_users.json"
        self.no_prefix_file = "no_prefix_users.json"
        self.load_premium_users()
        self.load_ip_banned_users()
        self.load_no_prefix_users()
        # Replace with your actual Discord user ID
        self.bot_owner_id = 1049708274032853003

    def load_ip_banned_users(self):
        if os.path.exists(self.ip_ban_file):
            with open(self.ip_ban_file, 'r') as f:
                self.ip_banned_users = json.load(f)
        else:
            self.ip_banned_users = {}

    def save_ip_banned_users(self):
        with open(self.ip_ban_file, 'w') as f:
            json.dump(self.ip_banned_users, f, indent=4)

    def load_premium_users(self):
        if os.path.exists(self.premium_file):
            with open(self.premium_file, 'r') as f:
                self.premium_users = json.load(f)
        else:
            self.premium_users = {}

    def save_premium_users(self):
        with open(self.premium_file, 'w') as f:
            json.dump(self.premium_users, f, indent=4)

    def load_no_prefix_users(self):
        if os.path.exists(self.no_prefix_file):
            with open(self.no_prefix_file, 'r') as f:
                self.no_prefix_users = json.load(f)
        else:
            self.no_prefix_users = {}

    def save_no_prefix_users(self):
        with open(self.no_prefix_file, 'w') as f:
            json.dump(self.no_prefix_users, f, indent=4)

    def is_bot_owner():
        def predicate(ctx):
            return ctx.author.id == 1049708274032853003
        return commands.check(predicate)

    def is_premium_server(self, guild_id):
        return str(guild_id) in self.premium_users
    
    def is_premium_user(self, user_id):
        return str(user_id) in self.premium_users

    def is_no_prefix_user(self, user_id):
        return str(user_id) in self.no_prefix_users

    @commands.command(name='addnoprefix')
    @is_bot_owner()
    async def add_no_prefix(self, ctx, user: discord.Member = None):
        if user is None:
            embed = discord.Embed(title="❌ Error", description="Please specify a user!", color=0xff0000)
            await ctx.send(embed=embed)
            return

        self.no_prefix_users[str(user.id)] = {}
        self.save_no_prefix_users()

        embed = discord.Embed(
            title="✅ No Prefix Added",
            description=f"{user.mention} has been added to no prefix list",
            color=0x00ff00
        )
        await ctx.send(embed=embed)

    @commands.command(name='removenoprefix')
    @is_bot_owner()
    async def remove_no_prefix(self, ctx, user: discord.Member = None):
        if user is None:
            embed = discord.Embed(title="❌ Error", description="Please specify a user!", color=0xff0000)
            await ctx.send(embed=embed)
            return

        if str(user.id) in self.no_prefix_users:
            del self.no_prefix_users[str(user.id)]
            self.save_no_prefix_users()

            embed = discord.Embed(
                title="✅ No Prefix Removed",
                description=f"{user.mention} has been removed from no prefix list",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="❌ Error", description="User is not in no prefix list!", color=0xff0000)
            await ctx.send(embed=embed)

    @commands.group(name='np')
    @is_bot_owner()
    async def np(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="🚫 No Prefix Commands",
                description="Available commands:\n`!np add <user>` - Add user to no prefix list\n`!np remove <user>` - Remove user from no prefix list",
                color=0x00ff00
            )
            await ctx.send(embed=embed)

    @np.command(name='add')
    @is_bot_owner()
    async def np_add(self, ctx, user: discord.Member = None):
        await self.add_no_prefix(ctx, user)

    @np.command(name='remove')
    @is_bot_owner()
    async def np_remove(self, ctx, user: discord.Member = None):
        await self.remove_no_prefix(ctx, user)

    @commands.command(name='premium')
    async def premium_status(self, ctx):
        guild_id = str(ctx.guild.id)
        is_premium = guild_id in self.premium_users

        embed = discord.Embed(
            title="👑 Server Premium Status",
            color=0xffd700 if is_premium else 0x808080
        )

        if is_premium:
            premium_data = self.premium_users[guild_id]
            embed.description = f"**{ctx.guild.name}** has **Premium Access**"
            embed.add_field(name="Activated On", value=premium_data.get('activated_on', 'Unknown'), inline=True)
            embed.add_field(name="Features", value="• IP Ban Commands\n• Premium Features\n• Priority Support", inline=False)
        else:
            embed.description = f"**{ctx.guild.name}** does **not** have Premium Access"
            embed.add_field(name="Get Premium", value="Contact bot owner for server premium access", inline=False)

        await ctx.send(embed=embed)

    @commands.command(name='activate')
    @is_bot_owner()
    async def premium_activate(self, ctx):
        from datetime import datetime
        
        guild_id = str(ctx.guild.id)
        self.premium_users[guild_id] = {
            'server_name': ctx.guild.name,
            'activated_on': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'activated_by': ctx.author.id
        }
        self.save_premium_users()

        embed = discord.Embed(
            title="✅ Server Premium Activated",
            description=f"Premium access has been granted to **{ctx.guild.name}**",
            color=0x00ff00
        )
        embed.add_field(name="Features Unlocked", value="• IP Ban Commands\n• Premium Features\n• Priority Support", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name='deactivate')
    @is_bot_owner()
    async def premium_deactivate(self, ctx):
        guild_id = str(ctx.guild.id)
        
        if guild_id in self.premium_users:
            del self.premium_users[guild_id]
            self.save_premium_users()

            embed = discord.Embed(
                title="✅ Server Premium Deactivated",
                description=f"Premium access has been removed from **{ctx.guild.name}**",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="❌ Error", description="This server doesn't have premium access!", color=0xff0000)
            await ctx.send(embed=embed)

    @commands.command(name='ipban')
    async def ip_ban(self, ctx, user: discord.Member = None, *, reason: str = "No reason provided"):
        # Check if user is bot owner or server has premium
        if ctx.author.id != self.bot_owner_id and not self.is_premium_server(ctx.guild.id):
            embed = discord.Embed(
                title="🔒 Premium Feature",
                description="This command requires Server Premium access!",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return

        if user is None:
            embed = discord.Embed(title="❌ Error", description="Please specify a user to IP ban!", color=0xff0000)
            await ctx.send(embed=embed)
            return

        if not ctx.author.guild_permissions.ban_members:
            embed = discord.Embed(title="❌ Error", description="You don't have permission to ban members!", color=0xff0000)
            await ctx.send(embed=embed)
            return

        try:
            # Add user to IP ban tracking
            from datetime import datetime
            self.ip_banned_users[str(user.id)] = {
                'username': f"{user.name}#{user.discriminator}",
                'guild_id': ctx.guild.id,
                'banned_by': ctx.author.id,
                'reason': reason,
                'banned_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.save_ip_banned_users()

            # Regular ban with tracking
            await user.ban(reason=f"IP Ban: {reason}", delete_message_days=7)

            embed = discord.Embed(
                title="🔨 IP Ban Applied",
                description=f"{user.mention} has been IP banned and tracked\n**Reason:** {reason}",
                color=0xff0000
            )
            embed.add_field(name="⚠️ Warning", value="User is now tracked and any alt accounts will be detected", inline=False)
            embed.add_field(name="📝 Note", value="User has been banned, messages deleted, and added to IP ban database", inline=False)
            embed.set_footer(text=f"Banned by {ctx.author.name}")
            await ctx.send(embed=embed)

        except Exception as e:
            embed = discord.Embed(title="❌ Error", description=f"Failed to IP ban user: {str(e)}", color=0xff0000)
            await ctx.send(embed=embed)

    @commands.command(name='ipunban')
    async def ip_unban(self, ctx, user_id: int = None):
        if ctx.author.id != self.bot_owner_id and not self.is_premium_server(ctx.guild.id):
            embed = discord.Embed(
                title="🔒 Premium Feature",
                description="This command requires Server Premium access!",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return

        if user_id is None:
            embed = discord.Embed(title="❌ Error", description="Please specify a user ID to IP unban!", color=0xff0000)
            await ctx.send(embed=embed)
            return

        if str(user_id) in self.ip_banned_users:
            user_data = self.ip_banned_users[str(user_id)]
            del self.ip_banned_users[str(user_id)]
            self.save_ip_banned_users()

            try:
                await ctx.guild.unban(discord.Object(id=user_id))
                embed = discord.Embed(
                    title="✅ IP Ban Removed",
                    description=f"User **{user_data['username']}** has been IP unbanned",
                    color=0x00ff00
                )
                embed.add_field(name="User ID", value=user_id, inline=True)
                embed.add_field(name="Originally banned for", value=user_data['reason'], inline=True)
                await ctx.send(embed=embed)
            except:
                embed = discord.Embed(
                    title="⚠️ Partial Success",
                    description=f"User **{user_data['username']}** removed from IP ban database, but couldn't unban from server",
                    color=0xffaa00
                )
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="❌ Error", description="User is not IP banned!", color=0xff0000)
            await ctx.send(embed=embed)

    @commands.command(name='ipbanlist')
    async def ip_ban_list(self, ctx):
        if ctx.author.id != self.bot_owner_id and not self.is_premium_server(ctx.guild.id):
            embed = discord.Embed(
                title="🔒 Premium Feature",
                description="This command requires Server Premium access!",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return

        if not self.ip_banned_users:
            embed = discord.Embed(title="🔨 IP Banned Users", description="No IP banned users found", color=0xff0000)
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(title="🔨 IP Banned Users", color=0xff0000)

        for user_id, data in self.ip_banned_users.items():
            embed.add_field(
                name=f"{data['username']} ({user_id})",
                value=f"**Reason:** {data['reason']}\n**Banned:** {data['banned_at']}",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name='premiumlist')
    @is_bot_owner()
    async def premium_list(self, ctx):
        if not self.premium_users:
            embed = discord.Embed(title="👑 Premium Servers", description="No premium servers found", color=0xffd700)
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(title="👑 Premium Servers", color=0xffd700)

        for guild_id, data in self.premium_users.items():
            try:
                guild = self.bot.get_guild(int(guild_id))
                if guild:
                    embed.add_field(
                        name=f"{guild.name}",
                        value=f"ID: {guild_id}\nActivated: {data.get('activated_on', 'Unknown')}",
                        inline=False
                    )
                else:
                    embed.add_field(
                        name=f"{data.get('server_name', 'Unknown Server')}",
                        value=f"ID: {guild_id}\nActivated: {data.get('activated_on', 'Unknown')}",
                        inline=False
                    )
            except:
                embed.add_field(
                    name=f"Unknown Server ({guild_id})",
                    value=f"Activated: {data.get('activated_on', 'Unknown')}",
                    inline=False
                )

        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Check if the user is IP banned
        if str(member.id) in self.ip_banned_users:
            try:
                await member.ban(reason="IP Banned user attempted to rejoin")
                # Try to notify admins
                for channel in member.guild.text_channels:
                    if channel.permissions_for(member.guild.me).send_messages:
                        embed = discord.Embed(
                            title="🚨 IP Banned User Detected",
                            description=f"**{member.name}#{member.discriminator}** (ID: {member.id}) tried to rejoin but was automatically banned",
                            color=0xff0000
                        )
                        embed.add_field(name="Original Reason", value=self.ip_banned_users[str(member.id)]['reason'], inline=False)
                        await channel.send(embed=embed)
                        break
            except:
                pass

    @commands.command(name='botowner')
    @is_bot_owner()
    async def botowner(self, ctx):
        embed = discord.Embed(
            title="👑 Bot Owner Panel",
            description="Welcome to the bot owner panel!",
            color=0x9900ff
        )
        embed.add_field(
            name="Available Commands:",
            value="• `!activate <user>` - Grant premium access\n"
                  "• `!deactivate <user>` - Remove premium access\n"
                  "• `!premiumlist` - View all premium users\n"
                  "• `!ipban <user>` - IP ban a user\n"
                  "• `!ipunban <user_id>` - Remove IP ban\n"
                  "• `!ipbanlist` - View IP banned users\n"
                  "• `!addnoprefix <user>` - Add user to no prefix list\n"
                  "• `!removenoprefix <user>` - Remove user from no prefix list\n"
                  "• No prefix required for bot owner",
            inline=False
        )
        embed.add_field(
            name="Permissions:",
            value="• Full bot access\n• Premium command access\n• User management\n• IP ban tracking\n• No prefix required",
            inline=False
        )

        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Check if user is not whitelisted and is using @everyone or @here
        moderation_cog = self.bot.get_cog('Moderation')
        if (moderation_cog and hasattr(moderation_cog, 'whitelist') and 
            str(message.guild.id) in moderation_cog.whitelist and
            message.author.id not in moderation_cog.whitelist[str(message.guild.id)] and
            ("@everyone" in message.content or "@here" in message.content)):
            
            # Hide channel from the user
            try:
                await message.channel.set_permissions(message.author, read_messages=False)
                
                # Send warning message
                embed = discord.Embed(
                    title="🚨 Security Alert",
                    description=f"{message.author.mention}, you have been restricted from viewing this channel due to unauthorized use of @everyone or @here ping.",
                    color=0xff0000
                )
                embed.add_field(name="Action Required", value="Contact moderators to regain access", inline=False)
                await message.channel.send(embed=embed)
                
            except Exception as e:
                print(f"Failed to restrict user: {e}")


async def setup(bot):
    await bot.add_cog(OwnersOnly(bot))