import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from config import TELEGRAM_BOT_TOKEN
import database as db
from analyzer import analyze_user_input
from tts_manager import generate_tts
from media_fetcher import fetch_video_clips, fetch_background_music
from video_editor import render_video

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message."""
    await update.message.reply_text(
        "🎬 Welcome to the Video Generator Bot!\n"
        "Send me any topic or idea, and I'll create a custom video for you.\n"
        "You can also chat normally or ask to modify the last script."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_msg = update.message.text
    logger.info(f"[INFO] User {user_id}: {user_msg[:50]}")

    # 1. Retrieve conversation history from DB
    history = db.get_conversation_history(user_id)
    
    # 2. Analyze with DeepSeek
    await update.message.reply_text("🧠 Analyzing your request...")
    analysis = analyze_user_input(user_id, user_msg, history)
    
    # 3. Append user message to DB
    db.append_to_history(user_id, "user", user_msg)
    
    if analysis["intent"] == "chat":
        # Plain chat response
        db.append_to_history(user_id, "assistant", analysis["reply"])
        await update.message.reply_text(analysis["reply"])
        return
    
    elif analysis["intent"] == "modify":
        # For simplicity, just inform the user that modification is not fully implemented
        # (In a full implementation you would update the last script state)
        await update.message.reply_text(
            "⚠️ Modification of existing videos is not yet implemented.\n"
            "Please describe your new video request from scratch."
        )
        # Still store assistant's reply
        db.append_to_history(user_id, "assistant", "Modification not implemented yet.")
        return
    
    elif analysis["intent"] == "video":
        script = analysis["script"]
        duration = analysis["duration_seconds"]
        keywords = analysis["keywords"]
        music_mood = analysis.get("music_mood", "upbeat")
        
        # 4. Generate voiceover (with fallback)
        await update.message.reply_text("🎙️ Generating voiceover...")
        try:
            voiceover_path = await generate_tts(script)
        except Exception as e:
            logger.error(f"[ERROR] Voiceover generation failed: {e}")
            await update.message.reply_text("❌ Voiceover generation failed. Please try again later.")
            return
        
        # 5. Fetch video clips
        await update.message.reply_text("🎬 Fetching video clips from Pixabay...")
        video_paths = await fetch_video_clips(keywords)
        if not video_paths:
            await update.message.reply_text("⚠️ No video clips found. Using a fallback clip.")
            # You could add a default fallback clip here
        
        # 6. Fetch background music
        await update.message.reply_text("🎵 Fetching background music...")
        music_path = await fetch_background_music(keywords, music_mood)
        
        # 7. Render final video
        await update.message.reply_text("🖥️ Rendering video (this may take a minute)...")
        output_video = await render_video(video_paths, voiceover_path, music_path, duration)
        
        # 8. Send video to user
        await update.message.reply_video(
            video=open(output_video, "rb"),
            caption="🎥 Here is your generated video!",
            supports_streaming=True
        )
        
        # 9. Cleanup temporary files (optional but good)
        import os
        for path in [voiceover_path, music_path, output_video] + video_paths:
            try:
                os.unlink(path)
            except:
                pass
        
        # 10. Store assistant's response in history
        db.append_to_history(user_id, "assistant", f"Generated video based on: {script[:100]}...")
        logger.info(f"[INFO] User {user_id}: Video generation completed.")
        return

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors and notify user."""
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text("An internal error occurred. Please try again later.")

def main():
    db.init_db()
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    
    logger.info("Bot started. Polling...")
    app.run_polling()

if __name__ == "__main__":
    main()