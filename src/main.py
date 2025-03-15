from collections import deque
from random import randint
from time import sleep

import discord
from discord.client import Client
from google import genai

import config
import logging_service
import prompt_manager


class EspionageBot(Client):
    def __init__(self, gemini_api_key, discord_token):
        super().__init__()
        self.gemini_api_key = gemini_api_key
        self.discord_token = discord_token
        self.ai_client = None
        self.message_history = {}

    async def on_ready(self):
        self.ai_client = genai.Client(api_key=self.gemini_api_key)
        print(f"Agent deployed as {self.user.name} (ID: {self.user.id})")

    async def on_message(self, message):
        if message.author.id == self.user.id or not isinstance(
            message.channel, discord.DMChannel
        ):
            return

        user_id = message.author.id

        if user_id not in self.message_history:
            self.message_history[user_id] = {
                "intercepted": deque(maxlen=10),
                "transmitted": deque(maxlen=10),
            }

        agent_history = self.message_history[user_id]

        operation_prompt = prompt_manager.create_prompt(
            ",".join(agent_history["transmitted"]),
            ",".join(agent_history["intercepted"]),
            message.content,
        )

        print(operation_prompt)

        try:
            async with message.channel.typing():
                intel_response = self.ai_client.models.generate_content(
                    model="gemini-2.0-flash", contents=operation_prompt
                )

                if not intel_response.text:
                    return

                await logging_service.record_exchange(
                    self, message.content, intel_response.text
                )

                sleep(randint(1, 3))

            sleep(randint(2, 5))

            await message.channel.send(intel_response.text)

            agent_history["intercepted"].append(message.content)
            agent_history["transmitted"].append(intel_response.text)

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
