import discord
from discord.ext import commands
from discord.ui import View, Select

class HelpSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Welcome",emoji="<:1000082828:1387031228724543598>" , description="Autorole, greet, verification, welcome commands", value="welcome"),
            discord.SelectOption(label="Moderation", emoji="<:1000082829:1387034764338401512>" , description="Antinuke, automod, ban, kick, timeout, etc.", value="moderation"),
            discord.SelectOption(label="Utility", emoji="<:1000082827:1387029382807294163>" , description="AFK, avatar, serverinfo, ping, etc.", value="utility"),
            discord.SelectOption(label="Giveaway", emoji="<:giveaways:1387030030835519601>" , description="Gstart, gend, greroll, gdelete commands", value="giveaway"),
            discord.SelectOption(label="Owner Only", emoji="<:cyber_Commands:1386276524222840902>" , description="Premium, IP ban, special commands", value="owner"),
        ]
        super().__init__(placeholder="Select A Category To Get Started ", options=options)

    async def callback(self, interaction: discord.Interaction):
        embeds = {
            "welcome": discord.Embed(
                title=" Welcome `[4]`",
                description="`autorole`\n"
                           "`greet`\n"
                           "`verification`\n"
                           "`welcome`\n",
                color=0x566573
            )
             
            ,
            
            "moderation": discord.Embed(
                title="Moderation `[22]`",
                description="`antinuke'\n"
                           "`automod`\n"
                           "`ban'\n"
                           "`clear`\n"
                           "`hide`\n"
                           "`kick`\n"
                           "`lock'\n"
                           "`nuke`\n"
                           "`punishment'\n"
                           "`role`\n"
                           "`slowmode`\n"
                           "`timeout`\n"
                           "`unban`\n"
                           "`unhide`\n"
                           "`unlock`\n"
                           "`unmute`\n"
                           "`vanityguard`\n"
                           "`whitelist'\n"
                           "`unwhitelist`\n"
                           "`whitelistview`\n"
                           "`unhide`",
                color=0x566573
            ),
            "utility": discord.Embed(
                title="⚙️ Utility Commands",
                description="`afk`\n"
                           "`autoreact`\n"
                           "`autoresponder`\n"
                           "`avatar`\n"
                           "`banner`\n"
                           "`blacklist`\n"
                           "`botinfo`\n"
                           "`commit`\n"
                           "`embed`\n"
                           "`invite`\n"
                           "`inviteinfo`\n"
                           "`leaderboard`\n"
                           "`managerrole`\n"
                           "`membercount`\n"
                           "`ping`\n"
                           "`prefix`\n"
                           "`premium`\n"
                           "`presenceroles`\n"
                           "`profile`\n"
                           "`roleicon`\n"
                           "`rolesetup`\n"
                           "`serverinfo`\n"
                           "`setup`\n"
                           "`starboard`\n"
                           "`statusrole`\n"
                           "`steal`\n"
                           "`stickynick`\n"
                           "'translate`\n"
                           "`userinfo`\n"
                           "`variables`\n"
                           "`ytnotifier`\n"
                           "`introduction`\n"
                           "`support'",
                color=0x566573
            ),
            "giveaway": discord.Embed(
                title="🎉 Giveaway Commands",
                description="**Gstart** - `!gstart <duration> <winners> <prize>` - Start giveaway\n"
                           "**Gend** - `!gend <message_id>` - End giveaway early\n"
                           "**Greroll** - `!greroll <message_id>` - Reroll giveaway\n"
                           "**Gdelete** - `!gdelete <message_id>` - Delete giveaway\n"
                           "**Snowflake** - `!snowflake <id>` - Get snowflake info",
                color=0x566573
            ),
            "owner": discord.Embed(
                title="👑 Owner Only Commands",
                description="**Premium Activate** - `!activate <user>` - Activate premium\n"
                           "**Premium Deactivate** - `!deactivate <user>` - Remove premium\n"
                           "**Premium List** - `!premiumlist` - View premium users\n"
                           "**IP Ban** - `!ipban <user> [reason]` - IP ban a user (Premium)\n"
                           "**IP Unban** - `!ipunban <user_id>` - Remove IP ban (Premium)\n"
                           "**IP Ban List** - `!ipbanlist` - View IP banned users (Premium)\n"
                           "**NP add** - `!np add <user>` - Add user to no prefix (Owner)\n"
                           "**NP remove** - `!np remove <user>` - Remove user from no prefix (Owner)\n"
                           "**Bot Owner** - `!botowner` - Bot owner panel\n"
                           "**Premium Check** - `!premium [user]` - Check premium status\n"
                           "**No Prefix** - Bot owner can use commands without prefix",
                color=0x566573
            )
        }

        await interaction.response.edit_message(embed=embeds[self.values[0]], view=self.view)

class HelpView(View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(HelpSelect())

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help')
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="<a:MF_BlackHelper:1387026040605507675> Help Menu",
            description= "<:1000082740:1387029387270164572>Hey bud! I'm **Astra**, a bot, here to make your "
            "discord experience even better. Need help with "
            "commands? Type `{load_prefix()}` to see what I can do.",
            color=0x566573
        )
        
        embed.set_footer(text="Use the dropdown menu to explore commands!")

        view = HelpView()
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Help(bot))
