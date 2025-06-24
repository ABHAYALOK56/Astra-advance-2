
import discord
from discord.ext import commands
import asyncio
import random
import json
import os
from datetime import datetime, timedelta

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.giveaways_file = "giveaways.json"
        self.load_giveaways()

    def load_giveaways(self):
        if os.path.exists(self.giveaways_file):
            with open(self.giveaways_file, 'r') as f:
                self.giveaways = json.load(f)
        else:
            self.giveaways = {}

    def save_giveaways(self):
        with open(self.giveaways_file, 'w') as f:
            json.dump(self.giveaways, f, indent=4)

    def parse_time(self, time_str):
        """Parse time string like '1h', '30m', '2d' etc."""
        time_units = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
        try:
            if time_str[-1] in time_units:
                return int(time_str[:-1]) * time_units[time_str[-1]]
            else:
                return int(time_str) * 60  # Default to minutes
        except:
            return 3600  # Default 1 hour

    @commands.command(name='gstart')
    @commands.has_permissions(manage_guild=True)
    async def gstart(self, ctx, duration: str = "1h", winners: int = 1, *, prize: str = "Amazing Prize"):
        duration_seconds = self.parse_time(duration)
        end_time = datetime.now() + timedelta(seconds=duration_seconds)
        
        embed = discord.Embed(
            title="🎉 GIVEAWAY 🎉",
            description=f"**Prize:** {prize}\n**Winners:** {winners}\n**Ends:** <t:{int(end_time.timestamp())}:R>",
            color=0x00ff00
        )
        embed.add_field(name="How to Enter:", value="React with 🎉 to enter!", inline=False)
        embed.set_footer(text=f"Hosted by {ctx.author.display_name}")
        
        message = await ctx.send(embed=embed)
        await message.add_reaction("🎉")
        
        self.giveaways[str(message.id)] = {
            'channel_id': ctx.channel.id,
            'prize': prize,
            'winners': winners,
            'end_time': end_time.timestamp(),
            'host_id': ctx.author.id
        }
        self.save_giveaways()
        
        # Schedule the giveaway end
        await asyncio.sleep(duration_seconds)
        await self.end_giveaway(message.id)

    @commands.command(name='gend')
    @commands.has_permissions(manage_guild=True)
    async def gend(self, ctx, message_id: int):
        await self.end_giveaway(message_id)

    @commands.command(name='greroll')
    @commands.has_permissions(manage_guild=True)
    async def greroll(self, ctx, message_id: int):
        message_id_str = str(message_id)
        
        if message_id_str not in self.giveaways:
            embed = discord.Embed(title="❌ Error", description="Giveaway not found!", color=0xff0000)
            await ctx.send(embed=embed)
            return
        
        giveaway = self.giveaways[message_id_str]
        channel = self.bot.get_channel(giveaway['channel_id'])
        
        try:
            message = await channel.fetch_message(message_id)
            reaction = discord.utils.get(message.reactions, emoji="🎉")
            
            if reaction:
                users = [user async for user in reaction.users() if not user.bot]
                
                if len(users) < giveaway['winners']:
                    embed = discord.Embed(
                        title="❌ Not Enough Participants",
                        description="Not enough people entered the giveaway!",
                        color=0xff0000
                    )
                    await ctx.send(embed=embed)
                    return
                
                winners = random.sample(users, giveaway['winners'])
                winner_mentions = [winner.mention for winner in winners]
                
                embed = discord.Embed(
                    title="🎉 Giveaway Rerolled!",
                    description=f"**New Winner(s):** {', '.join(winner_mentions)}\n**Prize:** {giveaway['prize']}",
                    color=0x00ff00
                )
                await ctx.send(embed=embed)
                
        except Exception as e:
            embed = discord.Embed(title="❌ Error", description=f"Failed to reroll giveaway: {str(e)}", color=0xff0000)
            await ctx.send(embed=embed)

    @commands.command(name='gdelete')
    @commands.has_permissions(manage_guild=True)
    async def gdelete(self, ctx, message_id: int):
        message_id_str = str(message_id)
        
        if message_id_str in self.giveaways:
            del self.giveaways[message_id_str]
            self.save_giveaways()
            
            embed = discord.Embed(
                title="✅ Giveaway Deleted",
                description="Giveaway has been deleted from the database",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="❌ Error", description="Giveaway not found!", color=0xff0000)
            await ctx.send(embed=embed)

    @commands.command(name='snowflake')
    async def snowflake(self, ctx, snowflake_id: int):
        try:
            timestamp = ((snowflake_id >> 22) + 1420070400000) / 1000
            created_at = datetime.fromtimestamp(timestamp)
            
            embed = discord.Embed(
                title="❄️ Snowflake Information",
                color=0x00ff00
            )
            embed.add_field(name="ID", value=snowflake_id, inline=False)
            embed.add_field(name="Created At", value=created_at.strftime("%B %d, %Y at %H:%M:%S UTC"), inline=False)
            embed.add_field(name="Timestamp", value=f"<t:{int(timestamp)}:F>", inline=False)
            
            await ctx.send(embed=embed)
        except:
            embed = discord.Embed(title="❌ Error", description="Invalid snowflake ID!", color=0xff0000)
            await ctx.send(embed=embed)

    async def end_giveaway(self, message_id):
        message_id_str = str(message_id)
        
        if message_id_str not in self.giveaways:
            return
        
        giveaway = self.giveaways[message_id_str]
        channel = self.bot.get_channel(giveaway['channel_id'])
        
        try:
            message = await channel.fetch_message(message_id)
            reaction = discord.utils.get(message.reactions, emoji="🎉")
            
            if reaction:
                users = [user async for user in reaction.users() if not user.bot]
                
                if len(users) < giveaway['winners']:
                    embed = discord.Embed(
                        title="❌ Giveaway Ended",
                        description=f"Not enough people entered the giveaway!\n**Prize:** {giveaway['prize']}",
                        color=0xff0000
                    )
                    await channel.send(embed=embed)
                else:
                    winners = random.sample(users, giveaway['winners'])
                    winner_mentions = [winner.mention for winner in winners]
                    
                    embed = discord.Embed(
                        title="🎉 Giveaway Ended!",
                        description=f"**Winner(s):** {', '.join(winner_mentions)}\n**Prize:** {giveaway['prize']}",
                        color=0x00ff00
                    )
                    await channel.send(embed=embed)
                    
                    # Update original message
                    original_embed = discord.Embed(
                        title="🎉 GIVEAWAY ENDED 🎉",
                        description=f"**Prize:** {giveaway['prize']}\n**Winner(s):** {', '.join(winner_mentions)}",
                        color=0xff0000
                    )
                    await message.edit(embed=original_embed)
            
            # Remove from active giveaways
            del self.giveaways[message_id_str]
            self.save_giveaways()
            
        except Exception as e:
            print(f"Error ending giveaway: {e}")

async def setup(bot):
    await bot.add_cog(Giveaway(bot))
