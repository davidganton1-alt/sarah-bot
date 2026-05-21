import telebot
import re
import requests
import json
import base64
import os
import random
import difflib
import time

try:
    from prompts import *
except ImportError:
    from bot_prompts import *
    print("WARNING: This will use a prompt template. Create your own prompts.py file.")

try:
    from config import *
except ImportError:
    from bot_config import *

TG_CHANNEL_ID = 777000
adm = ADMIN_ID
last_media_group = -1

bot = telebot.TeleBot(TOKEN_BOT)

FALLBACK_MODELS = [
    "nvidia/nemotron-3-super-120b-a12b:free",
    "google/gemma-4-26b-a4b-it:free",
    "deepseek/deepseek-v4-flash:free",
    "qwen/qwen3-coder:free",
]

def analyze_image(image_data):
    print("Image recognition...")
    base64_image = base64.b64encode(image_data).decode('utf-8')
    image_data_url = f"data:image/jpeg;base64,{base64_image}"
    for n in range(MAX_TRY):
        if n == 0:
            model = MODEL_IM
        else:
            model = MODEL_IM2
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}"},
            data=json.dumps({
                "model": model,
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_im},
                        {"type": "image_url", "image_url": {"url": image_data_url}}
                    ]
                }]
            })
        )
        print("Recognition completed.")
        if response.status_code == 200:
            answer = response.json()["choices"][0]["message"]["content"]
            if answer and answer.strip():
                return answer
            print("Empty answer, try again...")
        else:
            print(f"Error: {response.status_code}, try again...")
    error = response.status_code if response.status_code != 200 else "Empty answer"
    bot.send_message(adm, f"Error while analyzing the photo: {error}")
    return None

def get_answer(context, text):
    print("Sending request...")
    prompt = prompt_main + context
    for model in FALLBACK_MODELS:
        print(f"Trying model: {model}")
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}"},
            data=json.dumps({"model": model, "messages": [{"role": "system", "content": prompt}, {"role": "user", "content": text}]})
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            answer = response.json()["choices"][0]["message"]["content"]
            if answer and answer.strip():
                return answer
            print("Empty answer, trying next...")
        elif response.status_code == 429:
            print(f"{model} rate limited, next...")
            time.sleep(2)
            continue
        else:
            print(f"{model} error: {response.status_code}")
            continue
    bot.send_message(adm, "All models busy. Try again later.")
    return False

def remove_duplicate_text(text, similarity_threshold=0.9):
    lines = text.strip().split('\n')
    if len(lines) <= 1:
        return text
    half = len(lines) // 2
    first_half = lines[:half]
    second_half = lines[half:]
    similarity = difflib.SequenceMatcher(None, first_half, second_half).ratio()
    if similarity >= similarity_threshold:
        return '\n'.join(first_half)
    else:
        return text

def can_answer(message, text):
    if PHRASE_BLOCKLIST and text is not None and any(phrase in text for phrase in PHRASE_BLOCKLIST):
        return False
    if message.chat.type == 'private':
        if not WHITELIST_PRIVATE or message.from_user.id in WHITELIST:
            return True
        else:
            return False
    elif not WHITELIST_CHAT or message.chat.id in WHITE_CHATS:
        if random.random() < CHANCE_COMMENTS and message.from_user.id == TG_CHANNEL_ID:
            return True
        elif random.random() < CHANCE_REPLY and message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id:
            return True
        elif random.random() < CHANCE_CHAT and message.from_user.id != TG_CHANNEL_ID:
            return True
        else:
            return False
    else:
        return False

@bot.message_handler(content_types=['text', 'photo'])
def echo_message(message):
    global last_media_group
    if message.content_type == "text":
        text = message.text
    elif message.caption is not None:
        text = message.caption
    else:
        text = ""
    can_answ = can_answer(message, text)
    if can_answ:
        if message.content_type == "photo":
            if not REPLY_ALL_PHOTO and last_media_group == message.media_group_id:
                return
            elif message.media_group_id is not None:
                last_media_group = message.media_group_id
            file_info = bot.get_file(message.photo[-1].file_id)
            file = bot.download_file(file_info.file_path)
            result = analyze_image(file)
            if result is None and ADMIN_DESCRIP_IM:
                send = bot.send_photo(adm, message.photo[-1].file_id, "Enter a description of the image:")
                bot.register_next_step_handler(send, get_im_descript, message, text)
                return
            if result is not None:
                text = f"{text}\n\nAttached image: [{result}]"
        if not text or text.strip() == "":
            bot.reply_to(message, "An empty request was sent.")
        else:
            send_answer(message, text)
    elif can_answ is None:
        return
    elif not NO_WHITELIST_M.strip() == "" and message.chat.type == 'private':
        bot.reply_to(message, NO_WHITELIST_M)

def get_im_descript(message, mes, text):
    text = f"{text}\n\nAttached image: [{message.text}]"
    send_answer(mes, text)

def send_answer(message, text):
    if message.from_user.id == TG_CHANNEL_ID:
        extra_prompt = prompt_comment
    elif message.chat.type == 'private':
        extra_prompt = prompt_private
    elif message.from_user.id in SPECIAL_IDS:
        extra_prompt = prompt_special
    else:
        extra_prompt = prompt_chat
    answer = get_answer(extra_prompt, text)
    if answer:
        answer = re.sub(r'<think>.*?</think>', '', answer, flags=re.DOTALL)
        answer = remove_duplicate_text(answer)
        print("Message sends.")
        bot.reply_to(message, answer)

bot.infinity_polling(none_stop=True)
