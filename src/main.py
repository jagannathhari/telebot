import os
import sys


# import logging
# logging.basicConfig(level=logging.INFO)

API_HASH = os.getenv("API_HASH", "")
API_ID = os.getenv("API_ID", "")

from pyrogram import Client, filters

from database import database as db

app = Client("my_account", api_id=API_ID, api_hash=API_HASH)
BOT_NAME = "test_member_scraper_bot"


def get_property(obj, property):
    return getattr(obj, property, "None")


@app.on_message(filters.left_chat_member)
def handle_group(client, message):
    print("member left")
    # members = app.get_chat_members(chat.id)
    # for member in members:
    #     print(member)


@app.on_message(filters.new_chat_members)
def new_member(client, message):
    print(message)
    user_exits = db.user_exists_by_id(db.session, message.from_user.id)
    for added_member in message.new_chat_members:
        user_name = get_property(added_member,"username")
        if  user_name == BOT_NAME and user_exits:
            user = db.get_user_by_id(db.session,message.from_user.id)
            group = db.Group(
                group_id=message.chat.id,
                group_name=message.chat.title,
                total_members=message.chat.members_count,
            )
            db.session.add(group)
            db.session.commit()
            print("sucesfully added group")
            break


@app.on_message(filters.new_chat_title)
def name_changed(client, message):
    print("group name changesd")


@app.on_message(filters.private)
async def handle_message(client, message):
    text = message.text
    print(message.from_user.id)
    if text == "/register":
        if db.user_exists_by_id(db.session, message.from_user.id):
            await message.reply("Already registered")
        else:
            user = db.User(
                user_id=message.from_user.id,
                user_name=get_property(message, "username"),
            )
            db.session.add(user)
            db.session.commit()
            await message.reply("Registered Successfully.")

    elif text == "/groups":
        groups = db.get_group(db.session,message.from_user.id)
        print(groups)
        if groups:
            await message.reply(str(groups))
    elif text == "/add":
        # await app.add_chat_members(-4587976444,6367326070)
        tokens = text.split()
        if len(tokens) == 3:
            try:
                group1 = int(tokens[1])
                group2 = int(tokens[2])
                members = app.get_chat_members(group1)
                for member in members:
                    await app.add_chat_members(group1,member)
            except:
                await message.reply("Error")
        else:
            await message.reply("/add group1_id group2_id")



app.run()
