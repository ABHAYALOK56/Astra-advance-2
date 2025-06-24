import discord
from discord.ext import commands
from discord.ui import View, Select

class HelpSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="🏠 Welcome", description="Autorole, greet, verification, welcome commands", value="welcome"),
            discord.SelectOption(label="🛡️ Moderation", description="Antinuke, automod, ban, kick, timeout, etc.", value="moderation"),
            discord.SelectOption(label="⚙️ Utility", description="AFK, avatar, serverinfo, ping, etc.", value="utility"),
            discord.SelectOption(label="🎉 Giveaway", description="Gstart, gend, greroll, gdelete commands", value="giveaway"),
            discord.SelectOption(label="👑 Owner Only", description="Premium, IP ban, special commands", value="owner"),
        ]
        super().__init__(placeholder="Select A Category To Get Started ", options=options)

    async def callback(self, interaction: discord.Interaction):
        embeds = {
            "welcome": discord.Embed(
                title="🏠 Welcome Commands",
                description="**Autorole** - `!autorole <role>` - Set auto role for new members\n"
                           "**Greet** - `!greet <channel>` - Set greeting channel\n"
                           "**Verification** - `!verification <channel>` - Set verification system\n"
                           "**Welcome** - `!welcome <message>` - Set welcome message",
                color=0x00ff00
            ),
            "moderation": discord.Embed(
                title="🛡️ Moderation Commands",
                description="**Antinuke** - `!antinuke <on/off>` - Toggle antinuke protection\n"
                           "**Automod** - `!automod <on/off>` - Toggle automoderation\n"
                           "**Ban** - `!ban <user> [reason]` - Ban a user\n"
                           "**Clear** - `!clear <amount>` - Clear messages\n"
                           "**Hide** - `!hide <channel>` - Hide a channel\n"
                           "**Kick** - `!kick <user> [reason]` - Kick a user\n"
                           "**Lock** - `!lock <channel>` - Lock a channel\n"
                           "**Nuke** - `!nuke <channel>` - Nuke a channel\n"
                           "**Punishment** - `!punishment <user>` - View punishments\n"
                           "**Role** - `!role <user> <role>` - Manage roles\n"
                           "**Slowmode** - `!slowmode <seconds>` - Set slowmode\n"
                           "**Timeout** - `!timeout <user> <duration>` - Timeout user\n"
                           "**Unban** - `!unban <user>` - Unban a user\n"
                           "**Unhide** - `!unhide <channel>` - Unhide a channel\n"
                           "**Unlock** - `!unlock <channel>` - Unlock a channel\n"
                           "**Unmute** - `!unmute <user>` - Unmute a user\n"
                           "**Vanityguard** - `!vanityguard <on/off>` - Toggle vanity guard\n"
                           "**Whitelist** - `!whitelist <user>` - Whitelist user for ping security\n"
                           "**Unwhitelist** - `!unwhitelist <user>` - Remove from ping whitelist\n"
                           "**Whitelist View** - `!whitelistview` - View whitelisted users\n"
                           "**Unhide** - `!unhide [channel]` - Unhide a channel",
                color=0xff0000
            ),
            "utility": discord.Embed(
                title="⚙️ Utility Commands",
                description="**AFK** - `!afk [reason]` - Set AFK status\n"
                           "**Autoreact** - `!autoreact <emoji>` - Set auto reaction\n"
                           "**Autoresponder** - `!autoresponder <trigger> <response>` - Set auto response\n"
                           "**Avatar** - `!avatar [user]` - Get user avatar\n"
                           "**Banner** - `!banner [user]` - Get user banner\n"
                           "**Blacklist** - `!blacklist <user>` - Blacklist a user\n"
                           "**Botinfo** - `!botinfo` - Get bot information\n"
                           "**Commit** - `!commit` - Bot commit info\n"
                           "**Embed** - `!embed <title> <description>` - Create embed\n"
                           "**Invite** - `!invite` - Get bot invite link\n"
                           "**Inviteinfo** - `!inviteinfo <code>` - Get invite info\n"
                           "**Leaderboard** - `!leaderboard` - Show leaderboard\n"
                           "**Managerrole** - `!managerrole <role>` - Set manager role\n"
                           "**Membercount** - `!membercount` - Get member count\n"
                           "**Ping** - `!ping` - Get bot latency\n"
                           "**Prefix** - `!prefix <new_prefix>` - Change bot prefix\n"
                           "**Premium** - `!premium` - Check premium status\n"
                           "**Presenceroles** - `!presenceroles` - Manage presence roles\n"
                           "**Profile** - `!profile [user]` - Get user profile\n"
                           "**Roleicon** - `!roleicon <role> <icon>` - Set role icon\n"
                           "**Rolesetup** - `!rolesetup` - Setup roles\n"
                           "**Serverinfo** - `!serverinfo` - Get server info\n"
                           "**Setup** - `!setup` - Bot setup\n"
                           "**Starboard** - `!starboard <channel>` - Set starboard\n"
                           "**Statusrole** - `!statusrole` - Manage status roles\n"
                           "**Steal** - `!steal <emoji>` - Steal an emoji\n"
                           "**Stickynick** - `!stickynick <user> <nick>` - Set sticky nickname\n"
                           "**Translate** - `!translate <text>` - Translate text\n"
                           "**Userinfo** - `!userinfo [user]` - Get user info\n"
                           "**Variables** - `!variables` - Show variables\n"
                           "**YTNotifier** - `!ytnotifier <channel>` - YouTube notifications\n"
                           "**Introduction** - `!introduction` - Set introduction\n"
                           "**Support** - `!support` - Get support info",
                color=0x0099ff
            ),
            "giveaway": discord.Embed(
                title="🎉 Giveaway Commands",
                description="**Gstart** - `!gstart <duration> <winners> <prize>` - Start giveaway\n"
                           "**Gend** - `!gend <message_id>` - End giveaway early\n"
                           "**Greroll** - `!greroll <message_id>` - Reroll giveaway\n"
                           "**Gdelete** - `!gdelete <message_id>` - Delete giveaway\n"
                           "**Snowflake** - `!snowflake <id>` - Get snowflake info",
                color=0xffff00
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
                color=0x9900ff
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
            description= "<:black_gengar:1386999245042618450>Hey bud! I'm **Astra**, a bot, here to make your"
            "discord experience even better. Need help with "
            "commands? Type .help to see what I can do.",
            color=0x99AAb5
        )
        
        embed.set_footer(text="Use the dropdown menu to explore commands!")

        view = HelpView()
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Help(bot))
