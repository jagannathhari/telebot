from pyrogram.errors import FloodWait
from pyrogram.enums import ChatType
import asyncio
from pyrogram import Client
import config

async def get_all_chats(client):
    chats = []
    try:
        async for dialog in client.get_dialogs():
            chats.append(dialog.chat)
    except Exception as e:
        print(f"An error occurred while getting chats: {e}")
    return chats

def get_users_to_ban():
    while True:
        f = input("Enter file path(which contains users to ban).: ")
        if os.path.isfile(f):
            with open(f) as users:
                return [user.strip() for user in users.readlines()]
        else:
            print("Not a valid path.. please renter the path.")


async def filter_groups(client):
    groups = []
    while True:
        try:
            chats = await get_all_chats(client)
            for chat in chats:
                if chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
                    groups.append((chat.id, chat.title))
            break
        except FloodWait as e:
            wait_time = e.value
            print(f"Rate limit exceeded. Waiting for {wait_time} seconds.")
            await asyncio.sleep(wait_time)
        except Exception as e:
            print(f"An error occurred while filtering groups: {e}")
            break
    return groups

def get_username_from_link(link):
    link = link.strip().replace("t.me/", "")
    link = link.strip().replace("https://","")
    return link


async def main():
    api_id = config.API_ID
    api_hash = config.API_HASH
    phone_number = config.PHONE_NUMBER
    client = Client("session", api_id, api_hash, phone_number=phone_number)

    while True:
        response = input("Enter 1 to ban user, 2 to scrape user: ")
        if response not in ("1","2"):
            print(f"{response} is not a valid option. Choose 1 or 2")
        else:
            break

    async with client:
        groups = await filter_groups(client)
        for idx, group in enumerate(groups, start=1):
            print(idx,group[1])

        link = input("Enter public group link or username or number: ")
        users = None
        if link.isnumeric():
            idx = int(link)
            if idx > len(groups):
                print(f"Enter number between 1 and {len(groups)}")
            else:
                users = client.get_chat_members(groups[idx-1][0])
                username = groups[idx-1][1]
        else:
            username = get_username_from_link(link)
            if response != 1:
                users = client.get_chat_members(username)
            else:
                users = None
    if response == 1:
        users_to_ban = get_users_to_ban()
        for user in users_to_ban:
            await client.ban_chat_member(username, user)
       	    print("Banned user", user)

        if users:
            with open(f"{username}.csv","w",encoding='utf-8', errors='replace') as f:
                print("Full Name","Username","Id",sep=",",file=f)
                async for user_info in users:
                    user = user_info.user
                    username   = user.username
                    first_name = user.first_name or ""
                    last_name  = user.last_name or ""
                    full_name  = f"{first_name} {last_name}"
                    id         = user.id
                    cols = f"{full_name} ,{username},{id}"
                    print(cols,file=f)
                    print("Added: ",cols,end="\r")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
