import asyncio
import logging
from datetime import date, timedelta

import discord
from discord import app_commands
from sqlalchemy.exc import SQLAlchemyError
import httpx

from clients.intervals_client import IntervalsClient
from config.settings import settings
from database.session import SessionFactory, engine, init_db
from services.daily_baseline_service import calculate_daily_baseline
from services.sync_service import sync_activities, sync_wellness


logger = logging.getLogger(__name__)


class PrimeAiBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)
        self.sync_lock = asyncio.Lock()

    async def setup_hook(self):
        await self.tree.sync()

    async def on_ready(self):
        logger.info("Discord bot connected: %s", self.user)


bot = PrimeAiBot()


@bot.tree.command(name="ping", description="Check whether the bot is online.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("PrimeAI online!", ephemeral=True)


@bot.tree.command(
    name="sync",
    description="Save wellness and activity data for the last 30 days and today's baseline.",
)
@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def sync(interaction: discord.Interaction):
    if interaction.channel_id != int(settings.DISCORD_CHANNEL_ID):
        await interaction.response.send_message(
            "This command can only be used in the configured PrimeAi channel.",
            ephemeral=True,
        )
        return

    if bot.sync_lock.locked():
        await interaction.response.send_message(
            "A sync is already in progress.",
            ephemeral=True,
        )
        return

    async with bot.sync_lock:
        await interaction.response.defer(ephemeral=True, thinking=True)

        today = date.today()
        start_date = today - timedelta(days=30)
        client = IntervalsClient()
        wellness_count = None

        try:
            wellness_count = await sync_wellness(
                start_date, today, client, SessionFactory
            )
            await calculate_daily_baseline(today, SessionFactory)
            activities_count = await sync_activities(
                start_date, today, client, SessionFactory
            )
        except (httpx.HTTPError, SQLAlchemyError, OSError, ValueError, KeyError):
            logger.exception("Discord-triggered sync failed")
            message = "Sync failed. See the logs for details."
            if wellness_count is not None:
                message += (
                    f" Wellness data has already been saved for {wellness_count} days."
                    " Activity sync did not complete."
                )
            await interaction.followup.send(message, ephemeral=True)
            return

        await interaction.followup.send(
            f"Sync complete: {start_date} -> {today}\n"
            f"Wellness: {wellness_count} days\n"
            f"Activities: {activities_count}",
            ephemeral=True,
        )


@bot.tree.error
async def command_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError,
):
    if isinstance(error, app_commands.CheckFailure):
        message = "You need server administrator permissions to use this command."
    else:
        logger.error(
            "Discord command failed",
            exc_info=(type(error), error, error.__traceback__),
        )
        message = "The command failed. See the logs for details."

    if interaction.response.is_done():
        await interaction.followup.send(message, ephemeral=True)
    else:
        await interaction.response.send_message(message, ephemeral=True)


async def main():
    try:
        await init_db()
        async with bot:
            await bot.start(settings.DISCORD_TOKEN)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    logging.basicConfig(level=settings.LOG_LEVEL)
    asyncio.run(main())