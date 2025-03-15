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
    timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    timestamp_unix = int(timestamp.timestamp())

    message = (
        f"## 🔄 Exchange Log Entry\n\n"
        f"**📅 Date & Time:**  {timestamp_str} (<t:{timestamp_unix}:R>)\n\n"
        f"---  **Details**  ---\n\n"
        f"🎯 **Target:**\n```\n{incoming}\n```\n"
        f"👤 **Agent:**\n```\n{outgoing}\n```\n"
        f"---"
    )

    await secure_channel.send(message)
