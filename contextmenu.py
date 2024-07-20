import discord
from discord.ext import commands
import requests
from discord_webhook import DiscordWebhook
import os
import requests
from urllib.parse import urlparse
import os

# Get environment variables
bot_token = os.getenv('DISCORD_TOKEN')
webhook_url1 = os.getenv('WEBHOOK_URL1')
webhook_url2 = os.getenv('WEBHOOK_URL2')


WEBHOOK_URLS = [
    webhook_url1,  # Replace with your first webhook URL
    webhook_url2  # Replace with your second webhook URL
]

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = discord.app_commands.CommandTree(self)

    async def on_ready(self):
        await self.tree.sync()
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

client = MyClient()

def extract_filename(url):
    parsed_url = urlparse(url)
    path = parsed_url.path
    filename = os.path.basename(path)  # Extract filename from path
    return filename

@client.tree.context_menu(name="Send to Jeet")
async def send_to_webhooks(interaction: discord.Interaction, message: discord.Message):
    await interaction.response.defer(thinking=True, ephemeral=True)
    # Get message content
    message_content = message.content

    # Get message attachments (images)
    attachments = message.attachments
    attachment_urls = [attachment.url for attachment in attachments]

    # Construct the payload for the webhook
    payload = {
        "content": f"{message_content}"
    }

    # Iterate over each webhook URL and send the message
    for webhook_url in WEBHOOK_URLS:
        webhook = DiscordWebhook(url=webhook_url, username="Jeet Journal", content=message_content)

        if attachment_urls:
            for url in attachment_urls:
                response = requests.get(url)
                if response.status_code == 200:
                    # Extract filename from URL
                    filename = extract_filename(url)
                    webhook.add_file(file=response.content, filename=filename)
                else:
                    print(f"Failed to fetch image from {url}")

        response = webhook.execute()

    # Respond to the user who triggered the command
    await interaction.followup.send("Message sent to webhooks successfully!", ephemeral=True)
    

@client.event
async def on_ready():
    # Sync the command tree
    await client.tree.sync()
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')
    for guild in client.guilds:
        print(f'Connected to guild: {guild.name} (ID: {guild.id})')

# Run the bot
client.run(bot_token)


