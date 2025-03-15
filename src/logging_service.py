import datetime

from discord import TextChannel
from discord.abc import GuildChannel


async def record_exchange(bot, incoming: str, outgoing: str):
    secure_channel = bot.get_channel(1349783726761967678)

    if not isinstance(secure_channel, GuildChannel) or not isinstance(
        secure_channel, TextChannel
    ):
        return

    timestamp = datetime.datetime.now()

    await secure_channel.send(
        f"📅 {timestamp.strftime('%Y-%m-%d %H:%M:%S')} (<t:{int(timestamp.timestamp())}:R>)\n\n"
        f"Target:\n{incoming}\n"
        f"Agent:\n{outgoing}"
    )
