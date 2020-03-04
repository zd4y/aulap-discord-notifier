from . import db
from .bot import Bot
from .config import Config


async def get_prefix(bot, msg):
    guild = await db.get(db.Guild, id=msg.guild.id)
    if guild is None:
        guild = db.Guild(id=msg.guild.id)
        db.session.add(guild)
        db.session.commit()
    return guild.prefix


bot = Bot(command_prefix=get_prefix)

bot.load_extension('bot.cogs')

bot.run(Config.DISCORD_TOKEN)
