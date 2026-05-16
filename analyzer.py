import json
from openai import OpenAI
from config import DEEPSEEK_API_KEY, DEEPSEEK_API_BASE

# Initialize DeepSeek client (OpenAI compatible)
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_API_BASE
)

SYSTEM_PROMPT = """You are an AI assistant for a video generation bot. The user may ask for a video, give a general chat, or request changes.
If the user wants a video, respond with a JSON object containing:
{
  "intent": "video",
  "script": "The voiceover script text...",
  "duration_seconds": 30,
  "keywords": ["keyword1", "keyword2", "keyword3"],
  "music_mood": "upbeat/calm/epic/etc."
}
If the user is just chatting or giving a follow‑up command (like "change the script to be more funny"), respond with a plain text answer and no JSON.
If the user wants to modify a previous video (e.g. "make the script shorter"), set intent: "modify" and include the modification request in a "modification" field.
Always respect the conversation history. Use English for keywords, but the script may be in the user's preferred language (Urdu/Hindi/English)."""

def analyze_user_input(user_id: int, user_message: str, conversation_history: list) -> dict:
    """
    Send the user's message plus conversation history to DeepSeek.
    Returns a parsed result:
        For video intent: {"intent": "video", "script": "...", "duration_seconds": int, "keywords": [...], "music_mood": "..."}
        For modify intent: {"intent": "modify", "modification": "..."}
        For chat: {"intent": "chat", "reply": "..."}
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(conversation_history)  # previous user/assistant turns
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        temperature=0.7,
        max_tokens=800
    )
    reply = response.choices[0].message.content.strip()

    # Try to parse JSON if it looks like a structured response
    if reply.startswith("{") and reply.endswith("}"):
        try:
            data = json.loads(reply)
            if "intent" in data:
                return data
        except json.JSONDecodeError:
            pass

    # Otherwise treat as plain chat
    return {"intent": "chat", "reply": reply}