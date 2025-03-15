from collections import deque
from random import randint
from time import sleep

from discord.client import Client
from google import genai
from pydantic import BaseModel

import config
import logging_service
import prompt_manager


class Reply(BaseModel):
    reply: str
    is_bot_being_talked_to_percent: int


class EspionageBot(Client):
    def __init__(self, gemini_api_key, discord_token):
        super().__init__()
        self.gemini_api_key = gemini_api_key
        self.discord_token = discord_token
        self.ai_client = None
        self.message_history = {
            "intercepted": deque(maxlen=30),
            "transmitted": deque(maxlen=30),
        }

    async def on_ready(self):
        self.ai_client = genai.Client(api_key=self.gemini_api_key)
        print(f"Agent deployed as {self.user.name} (ID: {self.user.id})")

    async def on_message(self, message):
        if (
            message.author.id == self.user.id
            or message.channel.id != 1308136461215858780
        ):
            return

        author_name = message.author.display_name
        formatted_message = f"{author_name}: {message.content}"

        operation_prompt = prompt_manager.create_prompt(
            ",".join(self.message_history["transmitted"]),
            ",".join(self.message_history["intercepted"]),
            formatted_message,
        )

        try:
            intel_response = self.ai_client.models.generate_content(
                model="gemini-1.5-pro",
                contents=operation_prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": list[Reply],
                },
            )

            if not intel_response:
                return

            parsed_response = intel_response.parsed

            if isinstance(parsed_response, list) and parsed_response:
                reply_obj = parsed_response[0]
                if reply_obj.is_bot_being_talked_to_percent < 75:
                    return
                reply_text = reply_obj.reply
            else:
                return

            sleep(randint(10, 60))
            await message.channel.typing()
            sleep(randint(3, 8))
            await message.channel.send(reply_text)
            await logging_service.record_exchange(self, message.content, reply_text)

            self.message_history["intercepted"].append(formatted_message)
            self.message_history["transmitted"].append(f"You: {reply_text}")
        except Exception as e:
            print(f"Operation failure: {e}")

    def deploy(self):
        super().run(self.discord_token)


def main():
    gemini_api_key, discord_token = config.load_credentials()
    agent = EspionageBot(gemini_api_key, discord_token)
    agent.deploy()


if __name__ == "__main__":
    main()
