
import discord
from discord.ext import commands
import json
import os

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_file = "welcome_config.json"
        self.load_config()

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {}

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    @commands.command(name='autorole')
    @commands.has_permissions(administrator=True)
    async def autorole(self, ctx, role: discord.Role = None):
        if role is None:
            embed = discord.Embed(title="❌ Error", description="Please specify a role!", color=0xff0000)
            await ctx.send(embed=embed)
            return
        
        guild_id = str(ctx.guild.id)
        if guild_id not in self.config:
            self.config[guild_id] = {}
        
        self.config[guild_id]['autorole'] = role.id
        self.save_config()
        
        embed = discord.Embed(
            title="✅ Autorole Set",
            description=f"Autorole has been set to {role.mention}",
            color=0x00ff00
        )
        await ctx.send(embed=embed)

    @commands.command(name='greet')
    async def greet(self, ctx):
        # Check if user is bot owner or has administrator permission
        if ctx.author.id != 1049708274032853003 and not ctx.author.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Permission Denied", 
                description="You need **Administrator** permission to use this command!", 
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        channel = ctx.channel
        
        guild_id = str(ctx.guild.id)
        if guild_id not in self.config:
            self.config[guild_id] = {}
        
        self.config[guild_id]['greet_channel'] = channel.id
        self.save_config()
        
        embed = discord.Embed(
            title="✅ Greet Channel Set",
            description=f"Greet channel has been set to this channel",
            color=0x00ff00
        )
        await ctx.send(embed=embed)

    @commands.command(name='verification')
    async def verification(self, ctx, channel: discord.TextChannel = None):
        # Check if user is bot owner or has administrator permission
        if ctx.author.id != 1049708274032853003 and not ctx.author.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Permission Denied", 
                description="You need **Administrator** permission to use this command!", 
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        if channel is None:
            embed = discord.Embed(title="❌ Error", description="Please specify a channel!", color=0xff0000)
            await ctx.send(embed=embed)
            return
        
        guild_id = str(ctx.guild.id)
        if guild_id not in self.config:
            self.config[guild_id] = {}
        
        self.config[guild_id]['verification_channel'] = channel.id
        self.save_config()
        
        embed = discord.Embed(
            title="✅ Verification Channel Set",
            description=f"Verification channel has been set to {channel.mention}",
            color=0x00ff00
        )
        await ctx.send(embed=embed)

    @commands.command(name='welcome')
    @commands.has_permissions(administrator=True)
    async def welcome_message(self, ctx, *, message: str = None):
        if message is None:
            embed = discord.Embed(title="❌ Error", description="Please provide a welcome message!", color=0xff0000)
            await ctx.send(embed=embed)
            return
        
        guild_id = str(ctx.guild.id)
        if guild_id not in self.config:
            self.config[guild_id] = {}
        
        self.config[guild_id]['welcome_message'] = message
        self.save_config()
        
        embed = discord.Embed(
            title="✅ Welcome Message Set",
            description=f"Welcome message has been set to: {message}",
            color=0x00ff00
        )
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = str(member.guild.id)
        if guild_id not in self.config:
            return
        
        # Autorole
        if 'autorole' in self.config[guild_id]:
            role_id = self.config[guild_id]['autorole']
            role = member.guild.get_role(role_id)
            if role:
                try:
                    await member.add_roles(role)
                except:
                    pass
        
        # Welcome message
        if 'greet_channel' in self.config[guild_id]:
            channel_id = self.config[guild_id]['greet_channel']
            channel = member.guild.get_channel(channel_id)
            if channel:
                message = self.config[guild_id].get('welcome_message', f'Welcome {member.mention} to {member.guild.name}!')
                message = message.replace('{user}', member.mention).replace('{server}', member.guild.name)
                
                embed = discord.Embed(
                    title="👋 Welcome!",
                    description=message,
                    color=0x00ff00
                )
                embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
                await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
