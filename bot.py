import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Constants
LOTTERY_URL = "https://tinyurl.com/muwymx93"
BUTTON_TEXT = "Play lottery"
START_MESSAGE = "Click the button below to play lottery:"
MENU_TITLE = "📋 Command Menu"
MENU_FORMAT = "<code>{command}</code>\n{description}"

# Bot commands configuration
BOT_COMMANDS = [
    BotCommand("start", "Start the bot"),
    BotCommand("play", "Open Lottery"),
    BotCommand("menu", "Show command menu")
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command (simple startup acknowledgement)."""
    try:
        if not update.message:
            logger.warning("Received update without message in start handler")
            return

        await update.message.reply_text(
            "Bot started. Use /play to open Lottery or /menu to see available commands."
        )
        logger.info(f"Start acknowledgement sent to user {update.effective_user.id}")
    except Exception as e:
        logger.error(f"Error in start handler: {e}", exc_info=True)
        if update.message:
            try:
                await update.message.reply_text(
                    "Sorry, an error occurred. Please try again later."
                )
            except Exception:
                logger.error("Failed to send error message to user")


async def play_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /play command (moved from /start)."""
    try:
        if not update.message:
            logger.warning("Received update without message in play handler")
            return

        keyboard = [
            [InlineKeyboardButton(BUTTON_TEXT, url=LOTTERY_URL)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            START_MESSAGE,
            reply_markup=reply_markup
        )
        logger.info(f"Play command executed by user {update.effective_user.id}")
    except Exception as e:
        logger.error(f"Error in play handler: {e}", exc_info=True)
        if update.message:
            try:
                await update.message.reply_text(
                    "Sorry, an error occurred. Please try again later."
                )
            except Exception:
                logger.error("Failed to send error message to user")


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /menu command."""
    try:
        if not update.message:
            logger.warning("Received update without message in menu handler")
            return
        
        # Create inline keyboard buttons for each command
        keyboard = []
        menu_text = MENU_TITLE
        
        for cmd in BOT_COMMANDS:
            # Create clickable button for each command
            keyboard.append([
                InlineKeyboardButton(
                    f"▶ {cmd.command}",
                    callback_data=f"cmd_{cmd.command}"
                )
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            menu_text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
        logger.info(f"Menu command executed by user {update.effective_user.id}")
    except Exception as e:
        logger.error(f"Error in menu handler: {e}", exc_info=True)
        if update.message:
            try:
                await update.message.reply_text(
                    "Sorry, an error occurred while showing the menu. Please try again later."
                )
            except Exception:
                logger.error("Failed to send error message to user")


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callback queries."""
    try:
        query = update.callback_query
        if not query:
            logger.warning("Received update without callback_query")
            return
        
        if not query.data:
            logger.warning("Received callback_query without data")
            await query.answer("Invalid button data")
            return
        
        if not query.message:
            logger.warning("Received callback_query without message")
            await query.answer("Message not found")
            return
        
        await query.answer()
        logger.info(f"Button callback received: {query.data} from user {update.effective_user.id}")
        
        # Handle command button clicks
        if query.data.startswith("cmd_"):
            command_name = query.data.replace("cmd_", "")

            # Execute the corresponding command
            if command_name == "start":
                # Simple start acknowledgement (no heavy processing)
                await query.message.reply_text(
                    "Bot started. Use /play to open Lottery or /menu to see available commands."
                )
                logger.info(f"Start acknowledgement executed via button by user {update.effective_user.id}")

            elif command_name == "play":
                # Execute play command logic (opens lottery button)
                keyboard = [
                    [InlineKeyboardButton(BUTTON_TEXT, url=LOTTERY_URL)]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.message.reply_text(
                    START_MESSAGE,
                    reply_markup=reply_markup
                )
                logger.info(f"Play command executed via button by user {update.effective_user.id}")

            elif command_name == "menu":
                # Re-execute menu command
                keyboard = []
                menu_text = MENU_TITLE

                for cmd in BOT_COMMANDS:
                    keyboard.append([
                        InlineKeyboardButton(
                            f"▶ {cmd.command}",
                            callback_data=f"cmd_{cmd.command}"
                        )
                    ])

                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.message.reply_text(
                    menu_text,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
                logger.info(f"Menu command executed via button by user {update.effective_user.id}")
        
    except Exception as e:
        logger.error(f"Error in button_callback: {e}", exc_info=True)
        if update.callback_query:
            try:
                await update.callback_query.answer(
                    "Sorry, an error occurred. Please try again.",
                    show_alert=True
                )
            except Exception:
                logger.error("Failed to send error answer to user")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the telegram handlers."""
    logger.error(f"Exception while handling an update: {context.error}", exc_info=context.error)
    
    # Try to send error message to user if update is available
    if isinstance(update, Update) and update.message:
        try:
            await update.message.reply_text(
                "Sorry, an unexpected error occurred. Please try again later."
            )
        except Exception:
            logger.error("Failed to send error message to user")


async def post_init(application: Application) -> None:
    """Initialize bot commands after application is built."""
    try:
        # Delete all existing commands first to remove any cached/old commands
        try:
            await application.bot.delete_my_commands()
        except Exception as delete_error:
            logger.warning(f"Could not delete old commands (this is okay if none exist): {delete_error}")
        
        # Set new commands (start, play and menu)
        await application.bot.set_my_commands(BOT_COMMANDS)
        logger.info("Bot commands menu initialized successfully - start, play and menu commands set")
    except Exception as e:
        logger.error(f"Error in post_init: {e}", exc_info=True)
        # Don't fail the bot startup if command setting fails


def main() -> None:
    """Main function to start the bot."""
    # Get token from environment variable or use fallback
    TOKEN = os.getenv("BOT_TOKEN", "8494619697:AAG91Y2BkW-_u__Vob7czhcmQoPrxcBijpM")
    
    if not TOKEN:
        logger.error("Bot token not found! Please set BOT_TOKEN environment variable.")
        return
    
    try:
        application = Application.builder().token(TOKEN).post_init(post_init).build()
        
        # Add command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("play", play_command))
        application.add_handler(CommandHandler("menu", menu_command))
        
        # Add callback query handler for inline button clicks
        application.add_handler(CallbackQueryHandler(button_callback))
        
        # Add error handler
        application.add_error_handler(error_handler)
        
        logger.info("Bot is starting...")
        print("Bot is running...")
        application.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}", exc_info=True)
        print(f"Error starting bot: {e}")


if __name__ == "__main__":
    main()
