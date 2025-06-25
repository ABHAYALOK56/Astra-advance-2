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
                description="`antinuke`\n"
                           "`automod`\n"
                           "`ban`\n"
                           "`clear`\n"
                           "`hide`\n"
                           "`kick`\n"
                           "`lock`\n"
                           "`nuke`\n"
                           "`punishment`\n"
                           "`role`\n"
                           "`slowmode`\n"
                           "`timeout`\n"
                           "`unban`\n"
                           "`unhide`\n"
                           "`unlock`\n"
                           "`unmute`\n"
                           "`vanityguard`\n"
                           "`whitelist`\n"
                           "`unwhitelist`\n"
                           "`whitelistview`\n"
                           "`unhide`",
                color=0x566573
            ),
            "utility": discord.Embed(
                title="Utility `[34]",
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
                           "`translate`\n"
                           "`userinfo`\n"
                           "`variables`\n"
                           "`ytnotifier`\n"
                           "`introduction`\n"
                           "`support`",
                color=0x566573
            ),
            "giveaway": discord.Embed(
                title="Giveaway `[5]`",
                description="`gstart`\n"
                           "`gend`\n"
                           "`greroll\n"
                           "`gdelete`\n"
                           "`snowfake`",
                color=0x566573
            ),
            "owner": discord.Embed(
                title="Premium command`[10]`",
                description="`activate`\n"
                           "`deactivate`\n"
                           "`premiumlist`\n"
                           "`ipban`\n"
                           "`ipunban`\n"
                           "`ipbanlist`\n"
                           "`no prefix add`\n"
                           "`!no prefix remove`\n"
                           "`botowner`\n"
                           "`premium`\n"
                           ,
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
