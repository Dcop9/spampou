from pyrogram import Client, filters
from pyrogram.types import *
from pymongo import MongoClient
import random
import json
from os import remove
import img2pdf
from metaapi import META
import requests
import aiohttp
import asyncio

import os
import re

SUDOS = "5086015489"

SUDO = [int(i) for i in SUDOS.split()]
if 5086015489 not in SUDO:
    SUDO.append(5086015489)



API_ID = "1885739"
API_HASH = "6bd646032e21791c0913cd75a88dd0b7"
BOT_TOKEN = "5491713652:6292612694:AAGRCGBsVAbcINihylv6EtwAOJyZrMSNbZk"
LOG_ID = -1001736119322
MONGO_URL = "mongodb+srv://elianaapi:pranav8935@cluster0.gf5ky.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"

bot = Client(
    "Db" ,
    api_id=int("1885739"),
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)


async def get_file_id_from_message(message):
    file_id = None
    if message.document:
        if int(message.document.file_size) > 3145728:
            return
        mime_type = message.document.mime_type
        if mime_type not in ("image/png", "image/jpeg"):
            return
        file_id = message.document.file_id

    if message.sticker:
        if message.sticker.is_animated:
            if not message.sticker.thumbs:
                return
            file_id = message.sticker.thumbs[0].file_id
        else:
            file_id = message.sticker.file_id

    if message.photo:
        file_id = message.photo.file_id

    if message.animation:
        if not message.animation.thumbs:
            return
        file_id = message.animation.thumbs[0].file_id

    if message.video:
        if not message.video.thumbs:
            return
        file_id = message.video.thumbs[0].file_id
    return file_id

@bot.on_message(filters.command("start"))
async def start(client, message):
        buttons = [[InlineKeyboardButton("Add Me To Your Group", url="https://t.me/SpamProtectbot?startgroup=new"),
                    InlineKeyboardButton("Support", url="https://t.me/spamprotectsupport"),
                    InlineKeyboardButton("Channel", url="https://t.me/spamprotectupdate")
                    ]]
        Photo = "https://telegra.ph/file/eb38edbe0d0bc3fd2b8a9.jpg"
        await message.reply_photo(Photo, caption="Hi, I am SpamProtectBot", reply_markup=InlineKeyboardMarkup(buttons))


@bot.on_message(filters.command("help"))
async def help(client, message):
    await message.reply_text("**Owner Command**\n /addjudge - Promote Judge User\n /rmjudge -  Demote Judge User\n\n**Judge Command**\n /falsepositive Spam | Nsfw [Number Of False Positive]\n\n**Civilian Command**\n /info - Information User")


def is_admin(group_id: int, user_id: int):
    try:
        user_data = bot.get_chat_member(group_id, user_id)
        if user_data.status == 'administrator' or user_data.status == 'creator':
            return True
        else:
            return False
    except:
        return False


def call_back_filter(data):
    return filters.create(lambda flt, _, query: flt.data in query.data,
                          data=data)


@bot.on_callback_query(call_back_filter("kick"))
def kick_callback(_, query):
    user = query.data.split(":")[2]
    if is_admin(query.message.chat.id,
                query.from_user.id) and query.data.split(":")[1] == "kick":
        bot.ban_chat_member(query.message.chat.id, user)
        bot.unban_chat_member(query.message.chat.id, user)
        query.answer('Kicked!')
        query.message.edit(
            f'Kick User [{user}](tg://user?id={user})\n Admin User [{query.from_user.id}](tg://user?id={query.from_user.id})',
            parse_mode='markdown')
    else:
        message.reply('You are not admin!')


@bot.on_callback_query(call_back_filter("ban"))
def ban_callback(_, query):
    user = query.data.split(":")[2]
    if is_admin(query.message.chat.id,
                query.from_user.id) and query.data.split(":")[1] == "ban":
        bot.ban_chat_member(query.message.chat.id, user)
        query.answer('Banned')
        query.message.edit(
            f'Banned User [{user}](tg://user?id={user})\n Admin User [{query.from_user.id}](tg://user?id={query.from_user.id})',
            parse_mode='markdown')
    else:
        message.reply('You are not admin!')


@bot.on_message(filters.new_chat_members)
async def alert(client, message):
    leveldb = MongoClient(MONGO_URL)    
    sudo = leveldb["SpamDN"]["Sudo"]  
    spam = leveldb["SpamDN"]["Spam"]  
    is_level = spam.find_one({"user_id": message.from_user.id})
    is_sudo = sudo.find_one({"user_id": message.from_user.id})
    if is_sudo:
        await message.reply_text(f"Name - {message.from_user.first_name}\n Status - Judge")    
    if not is_sudo:
        if is_level:
            rate = is_level["trust_rate"] 
            rate2 = is_level["nsfw_trust_rate"]
            count = is_level["nsfw_count"]
            rate3 = is_level["spam_trust_rate"]
            count2 = is_level["spam_count"]
            if not rate >= 25:   
                await message.reply_text(f"#ALERT\n**This User Is Criminal**\n**User:** [{message.from_user.first_name}](tg://user?id={message.from_user.id})\n**User Trust Rate:** `{rate}%`\n**Nsfw Trust Rate:** `{rate2}%`\n**Spam Trust Rate:** `{rate3}%`\n**Nsfw Count:** `{count}`\n**Spam Count:** `{count2}`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Ban", callback_data=f"ban:ban:{user}"), InlineKeyboardButton("Kick", callback_data=f"kick:kick:{user}"), InlineKeyboardButton("Mute", callback_data=f"mute:mute:{user}")]]))    
                     

@bot.on_message(filters.command("info"))
async def info(client, message):
    if not message.reply_to_message:
        leveldb = MongoClient(MONGO_URL)    
        sudo = leveldb["SpamDN"]["Sudo"]  
        spam = leveldb["SpamDN"]["Spam"]  
        is_level = spam.find_one({"user_id": message.from_user.id})
        is_sudo = sudo.find_one({"user_id": message.from_user.id})
        if is_sudo:
            await message.reply_text(f"Name - {message.from_user.first_name}\n Status - Judge")    
        if not is_sudo:
            if is_level:
                rate = is_level["trust_rate"] 
                rate2 = is_level["nsfw_trust_rate"]
                count = is_level["nsfw_count"]
                rate3 = is_level["spam_trust_rate"]
                count2 = is_level["spam_count"]
                if rate >= 25:      
                    await message.reply_text(f"**Status** `Civilian`\n**User:** [{message.from_user.first_name}](tg://user?id={message.from_user.id})\n**User Trust Rate:** `{rate}%`\n**Nsfw Trust Rate:** `{rate2}%`\n**Spam Trust Rate:** `{rate3}%`\n**Nsfw Count:** `{count}`\n**Spam Count:** `{count2}`")
                if not rate >= 25:
                    await message.reply_text(f"**Status** `Criminal`\n**User:** [{message.from_user.first_name}](tg://user?id={message.from_user.id})\n**User Trust Rate:** `{rate}%`\n**Nsfw Trust Rate:** `{rate2}%`\n**Spam Trust Rate:** `{rate3}%`\n**Nsfw Count:** `{count}`\n**Spam Count:** `{count2}`")
            if not is_level:
                await message.reply_text(f"**Status** `Civilian`\n**User:** [{message.from_user.first_name}](tg://user?id={message.from_user.id})\n**User Trust Rate:** `100%`\n**Nsfw Trust Rate:** `100%`\n**Spam Trust Rate:** `100%`\n**Nsfw Count:** `0`\n**Spam Count:** `0`")
    if message.reply_to_message:
        leveldb = MongoClient(MONGO_URL)    
        sudo = leveldb["SpamDN"]["Sudo"]  
        spam = leveldb["SpamDN"]["Spam"]  
        is_level = spam.find_one({"user_id": message.reply_to_message.from_user.id})
        is_sudo = sudo.find_one({"user_id": message.reply_to_message.from_user.id})
        if is_sudo:
            await message.reply_text(f"Name - {message.reply_to_message.from_user.first_name}\n Status - Judge")    
        if not is_sudo:
            if is_level:
                rate = is_level["trust_rate"] 
                rate2 = is_level["nsfw_trust_rate"]
                count = is_level["nsfw_count"]
                rate3 = is_level["spam_trust_rate"]
                count2 = is_level["spam_count"]
                if rate >= 25:      
                    await message.reply_text(f"**Status** `Civilian`\n**User:** [{message.reply_to_message.from_user.first_name}](tg://user?id={message.reply_to_message.from_user.id})\n**User Trust Rate:** `{rate}%`\n**Nsfw Trust Rate:** `{rate2}%`\n**Spam Trust Rate:** `{rate3}%`\n**Nsfw Count:** `{count}`\n**Spam Count:** `{count2}`")
                if not rate >= 25:
                    await message.reply_text(f"**Status** `Criminal`\n**User:** [{message.reply_to_message.from_user.first_name}](tg://user?id={message.reply_to_message.from_user.id})\n**User Trust Rate:** `{rate}%`\n**Nsfw Trust Rate:** `{rate2}%`\n**Spam Trust Rate:** `{rate3}%`\n**Nsfw Count:** `{count}`\n**Spam Count:** `{count2}`")
            if not is_level:
                await message.reply_text(f"**Status** `Civilian`\n**User:** [{message.reply_to_message.from_user.first_name}](tg://user?id={message.reply_to_message.from_user.id})\n**User Trust Rate:** `100%`\n**Nsfw Trust Rate:** `100%`\n**Spam Trust Rate:** `100%`\n**Nsfw Count:** `0`\n**Spam Count:** `0`")
              

@bot.on_message(filters.command("whois"))
async def whois(client, message):
    if not message.reply_to_message:
        leveldb = MongoClient(MONGO_URL)    
        sudo = leveldb["SpamDN"]["Sudo"]  
        spam = leveldb["SpamDN"]["Spam"]  
        is_level = spam.find_one({"user_id": message.from_user.id})
        is_sudo = sudo.find_one({"user_id": message.from_user.id})
        if is_sudo:
            await message.reply_text(f"Name - {message.from_user.first_name}\n Status - Judge")    
        if not is_sudo:
            if is_level:
                rate = is_level["trust_rate"] 
                rate2 = is_level["nsfw_trust_rate"]
                count = is_level["nsfw_count"]
                rate3 = is_level["spam_trust_rate"]
                count2 = is_level["spam_count"]
                if rate >= 25:      
                    await message.reply_text(f"**Status** `Civilian`\n**User:** [{message.from_user.first_name}](tg://user?id={message.from_user.id})\n**User Trust Rate:** `{rate}%`\n**Nsfw Trust Rate:** `{rate2}%`\n**Spam Trust Rate:** `{rate3}%`\n**Nsfw Count:** `{count}`\n**Spam Count:** `{count2}`")
                if not rate >= 25:
                    await message.reply_text(f"**Status** `Criminal`\n**User:** [{message.from_user.first_name}](tg://user?id={message.from_user.id})\n**User Trust Rate:** `{rate}%`\n**Nsfw Trust Rate:** `{rate2}%`\n**Spam Trust Rate:** `{rate3}%`\n**Nsfw Count:** `{count}`\n**Spam Count:** `{count2}`")
            if not is_level:
                await message.reply_text(f"**Status** `Civilian`\n**User:** [{message.from_user.first_name}](tg://user?id={message.from_user.id})\n**User Trust Rate:** `100%`\n**Nsfw Trust Rate:** `100%`\n**Spam Trust Rate:** `100%`\n**Nsfw Count:** `0`\n**Spam Count:** `0`")
    if message.reply_to_message:
        leveldb = MongoClient(MONGO_URL)    
        sudo = leveldb["SpamDN"]["Sudo"]  
        spam = leveldb["SpamDN"]["Spam"]  
        is_level = spam.find_one({"user_id": message.reply_to_message.from_user.id})
        is_sudo = sudo.find_one({"user_id": message.reply_to_message.from_user.id})
        if is_sudo:
            await message.reply_text(f"Name - {message.reply_to_message.from_user.first_name}\n Status - Judge")    
        if not is_sudo:
            if is_level:
                rate = is_level["trust_rate"] 
                rate2 = is_level["nsfw_trust_rate"]
                count = is_level["nsfw_count"]
                rate3 = is_level["spam_trust_rate"]
                count2 = is_level["spam_count"]
                if rate >= 25:      
                    await message.reply_text(f"**Status** `Civilian`\n**User:** [{message.reply_to_message.from_user.first_name}](tg://user?id={message.reply_to_message.from_user.id})\n**User Trust Rate:** `{rate}%`\n**Nsfw Trust Rate:** `{rate2}%`\n**Spam Trust Rate:** `{rate3}%`\n**Nsfw Count:** `{count}`\n**Spam Count:** `{count2}`")
                if not rate >= 25:
                    await message.reply_text(f"**Status** `Criminal`\n**User:** [{message.reply_to_message.from_user.first_name}](tg://user?id={message.reply_to_message.from_user.id})\n**User Trust Rate:** `{rate}%`\n**Nsfw Trust Rate:** `{rate2}%`\n**Spam Trust Rate:** `{rate3}%`\n**Nsfw Count:** `{count}`\n**Spam Count:** `{count2}`")
            if not is_level:
                await message.reply_text(f"**Status** `Civilian`\n**User:** [{message.reply_to_message.from_user.first_name}](tg://user?id={message.reply_to_message.from_user.id})\n**User Trust Rate:** `100%`\n**Nsfw Trust Rate:** `100%`\n**Spam Trust Rate:** `100%`\n**Nsfw Count:** `0`\n**Spam Count:** `0`")
              
              

            
                
       
            


@bot.on_message(filters.command("addjudge") & filters.user(SUDO))
async def kkbnmg(client, message):
    leveldb = MongoClient(MONGO_URL)    
    sudo = leveldb["SpamDN"]["Sudo"]  
    spam = leveldb["SpamDN"]["Spam"]  
    if message.reply_to_message:
        is_sudo = sudo.find_one({"user_id": message.reply_to_message.from_user.id})
        if not is_sudo: 
            spam.delete_one({"user_id": message.reply_to_message.from_user.id})
            sudo.insert_one({"user_id": message.reply_to_message.from_user.id})
            await message.reply_text(f"This judge user is promoted")
            await bot.send_message(LOG_ID, f"""**New Judge**\n**User:** [{message.reply_to_message.from_user.id}](tg://user?id={message.reply_to_message.from_user.id})""")               
        if is_sudo:
            await message.reply_text(f"This User Is Already Judge")    
            
@bot.on_message(filters.command("rmjudge") & filters.user(SUDO))
async def kkbnmg(client, message):
    leveldb = MongoClient(MONGO_URL)    
    sudo = leveldb["SpamDN"]["Sudo"]  
    if message.reply_to_message:
        is_sudo = sudo.find_one({"user_id": message.reply_to_message.from_user.id})
        if not is_sudo: 
            await message.reply_text(f"This User Is Not Judge")
        if is_sudo:
            await bot.send_message(LOG_ID, f"""**Remove Judge**\n**User:** [{message.reply_to_message.from_user.id}](tg://user?id={message.reply_to_message.from_user.id})""")
            sudo.delete_one({"user_id": message.reply_to_message.from_user.id})
            await message.reply_text(f"This Judge User Is Demoted")    
            


@bot.on_message(filters.command("falsepositive nsfw"))
async def false(client, message):
    msg = message.command[1]    
    hey = int(msg)
    if message.reply_to_message:
        leveldb = MongoClient(MONGO_URL)    
        sudo = leveldb["SpamDN"]["Sudo"]
        toggle = leveldb["SpamDN"]["Spam"]
        is_level = toggle.find_one({"user_id": message.reply_to_message.from_user.id})
        is_sudo = sudo.find_one({"user_id": message.from_user.id})            
        if not is_sudo:
            await message.reply_text(f"**You Are Not Judge**")            
        if is_sudo:
            if not is_level:
                await message.reply_text(f"**Not Found User**")
            if is_level:
                lol = 1 * hey
                rate = is_level["trust_rate"] + lol
                rate2 = is_level["nsfw_trust_rate"] + lol
                count = is_level["nsfw_count"] - hey
                await message.reply_text(f"**False Positive Done**")
                await bot.send_message(LOG_ID, f"""**Judge Name:** [{message.from_user.first_name}](tg://user?id={message.reply_to_message.from_user.id})\n**User Name:** [{message.reply_to_message.from_user.first_name}](tg://user?id={message.reply_to_message.from_user.id})\n**Mode:** Nsfw""")               
                toggle.update_one({"user_id": message.reply_to_message.from_user.id}, {"$set": {"trust_rate": rate, "nsfw_trust_rate": rate2, "nsfw_count": count}})
        
    

@bot.on_message(filters.command("falsepositive spam"))
async def false(client, message):
    msg = message.command[1]   
    hey = int(msg)
    if message.reply_to_message:
        leveldb = MongoClient(MONGO_URL)    
        sudo = leveldb["SpamDN"]["Sudo"]
        toggle = leveldb["SpamDN"]["Spam"]
        is_level = toggle.find_one({"user_id": message.reply_to_message.from_user.id})
        is_sudo = sudo.find_one({"user_id": message.from_user.id})
        if not is_sudo:
            await message.reply_text(f"**You Are Not Judge**")            
        if is_sudo:
            if not is_level:
                await message.reply_text(f"**Not Found User**")
            if is_level:
                lol = 0.2 * hey
                rate = is_level["trust_rate"] + lol
                rate2 = is_level["spam_trust_rate"] + lol
                count = is_level["spam_count"] - hey
                await message.reply_text(f"**False Positive Done**")
                await bot.send_message(LOG_ID, f"""**Judge Name:** [{message.from_user.first_name}](tg://user?id={message.reply_to_message.from_user.id})\n**User Name:** [{message.reply_to_message.from_user.first_name}](tg://user?id={message.reply_to_message.from_user.id})\n**Mode:** Spam""")                              
                toggle.update_one({"user_id": message.reply_to_message.from_user.id}, {"$set": {"trust_rate": rate, "spam_trust_rate": rate2, "spam_count": count}})
       

@bot.on_message(
    (filters.document
     | filters.photo
     | filters.sticker
     | filters.animation
     | filters.video)
    & ~filters.private,
    group=8,
)
async def detect_nsfw(_, message):
    file_id = await get_file_id_from_message(message)
    leveldb = MongoClient(MONGO_URL)    
    sudo = leveldb["SpamDN"]["Sudo"]
    toggle = leveldb["SpamDN"]["Spam"]
    is_level = toggle.find_one({"user_id": message.from_user.id})
    is_sudo = toggle.find_one({"user_id": message.from_user.id})
    if not is_sudo:
        if not is_level:    
            if not file_id:
                return
            file = await bot.download_media(file_id)
            try:
                results = requests.post(f"https://api.safone.tech/nsfw", files={'image': open(file, 'rb')}).json()
            except Exception:
                return        
            n = results['data']['is_nsfw']
            nsfw = f"{n}"
            remove(file)
            if nsfw == "True":                         
                toggle.insert_one({"user_id": message.from_user.id, "trust_rate": 99, "nsfw_trust_rate": 99, "nsfw_count": 1, "spam_trust_rate": 100, "spam_count": 0, "massadder_trust_rate": 100, "massadder_count": 0})
                hey = await bot.send_message(LOG_ID, f"""**Is Nsfw:** `{nsfw}`\n**User:** [{message.from_user.id}](tg://user?id={message.from_user.id})\n**Message Link:** {message.link}\n**User Trust Rate:** `99%`\n**User Nsfw Trust Rate:** `99%`\n**Nsfw Count:** `1`""")
                n = await message.reply_text(f"**Nsfw Detected**\n Result Link - {hey.link}")
                await asyncio.sleep(5)
                await n.delete()
        if is_level:
            if not file_id:
                return
            file = await bot.download_media(file_id)
            try:
                results = requests.post(f"https://api.safone.tech/nsfw", files={'image': open(file, 'rb')}).json()
            except Exception:
                return        
            n = results['data']['is_nsfw']            
            nsfw = f"{n}"
            remove(file)
            if nsfw == "True":                                  
                rate = is_level["trust_rate"] - 1
                rate2 = is_level["nsfw_trust_rate"] - 1
                count = is_level["nsfw_count"] + 1                       
                hey = await bot.send_message(LOG_ID, f"""**Is Nsfw:** `{nsfw}`\n**User:** [{message.from_user.id}](tg://user?id={message.from_user.id})\n**Message Link:** {message.link}\n**User Trust Rate:** `{rate}%`\n**User Nsfw Trust Rate:** `{rate2}%`\n**Nsfw Count:** `{count}`""")
                n = await message.reply_text(f"**Nsfw Detected**\n Result Link - {hey.link}")     
                toggle.update_one({"user_id": message.from_user.id}, {"$set": {"trust_rate": rate, "nsfw_trust_rate": rate2, "nsfw_count": count}})
                await asyncio.sleep(5)
                await n.delete()   
                

@bot.on_message(
    (filters.caption
     | filters.text)
    & ~filters.private,
    group=30,
)
async def detect_spam(_, message):
    leveldb = MongoClient(MONGO_URL)    
    sudo = leveldb["SpamDN"]["Sudo"]
    toggle = leveldb["SpamDN"]["Spam"]
    is_level = toggle.find_one({"user_id": message.from_user.id})
    is_sudo = sudo.find_one({"user_id": message.from_user.id})
    if not message.text == "/start@SpamProtectBot":
        K = "Hey"
        if not message.text == "/help@SpamProtectBot":  
            K = "Hey"
            if not message.text == "/info@SpamProtectBot":
                Why = "k"
                if not message.text == "/whois@SpamProtectBot":
                    lol = "k"
                    if message.text or message.caption:
                        if not is_sudo:
                            if not is_level:
                                text = message.text or message.caption
                                if not text:
                                    return                   
                                resp = requests.post(f"https://api.safone.tech/spam", json={'text': message.text}).json()       
                                if resp['data']['is_spam']:        
                                    n = resp['data']['is_spam']             
                                    spam = f"{n}"             
                                    if spam == "True":                      
                                        toggle.insert_one({"user_id": message.from_user.id, "trust_rate": 99.8, "nsfw_trust_rate": 100, "nsfw_count": 0, "spam_trust_rate": 99.8, "spam_count": 1, "massadder_trust_rate": 100, "massadder_count": 0})
                                        hey = await bot.send_message(LOG_ID, f"""**Is Spam:** `{spam}`\n**User:** [{message.from_user.id}](tg://user?id={message.from_user.id})\n**Message Text**: `{message.text}`\n**Message Link:** {message.link}\n**User Trust Rate:** `99.8%`\n**User Spam Trust Rate:** `99.8%`\n**Nsfw Spam:** `1`""")
                                        n = await message.reply_text(f"**Spam Detected**\n Result Link - {hey.link}")
                                        await asyncio.sleep(12)
                                        await n.delete()
                            if is_level:
                                text = message.text or message.caption
                                if not text:
                                    return
                                resp = requests.post(f"https://api.safone.tech/spam", json={'text': message.text}).json()      
                                if resp['data']['is_spam']:
                                    n = resp['data']['is_spam']        
                                    spam = f"{n}"             
                                    if spam == "True":       
                                        rate = is_level["trust_rate"] - 0.2
                                        rate2 = is_level["spam_trust_rate"] - 0.2
                                        count = is_level["spam_count"] + 1      
                                        hey = await bot.send_message(LOG_ID, f"""**Is Spam:** `{spam}`\n**User:** [{message.from_user.id}](tg://user?id={message.from_user.id})\n**Message Text**: `{message.text}`\n**Message Link:** {message.link}\n**User Trust Rate:** `{rate}%`\n**User Spam Trust Rate:** `{rate2}%`\n**Spam Count:** `{count}`""")               
                                        n = await message.reply_text(f"**Spam Detected**\n Result Link - {hey.link}")       
                                        toggle.update_one({"user_id": message.from_user.id}, {"$set": {"trust_rate": rate, "spam_trust_rate": rate2, "spam_count": count}})
                                        await asyncio.sleep(12)
                                        await n.delete()     
                     
bot.run()
