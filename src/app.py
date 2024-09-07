from pyrogram.errors import FloodWait
from pyrogram.enums import ChatType
import asyncio
import logging
from pyrogram import Client
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_all_chats(client):
    chats = []
    try:
        async for dialog in client.get_dialogs():
            chats.append(dialog.chat)
    except Exception as e:
        print(f"An error occurred while getting chats: {e}")
    return chats


async def filter_groups(client):
    groups = []
    while True:
        try:
            chats = await get_all_chats(client)
            for chat in chats:
                if chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
                    if chat.permissions.can_invite_users:
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


async def transfer_user(client, src, dest):
    try:
        members = []
        async for member in client.get_chat_members(src):
            members.append(member)

            # Process in batches
            if len(members) >= config.BATCH_SIZE:
                await _process_batch(client, dest, members)
                members = []

        # Process any remaining members
        if members:
            await _process_batch(client, dest, members)

    except Exception as e:
        logger.error(f"An error occurred while transferring users: {e}")


async def _process_batch(client, dest, members):
    try:
        for member in members:
            try:
                await client.add_chat_members(dest, member.user.id)

                user_name = member.user.username or "Unknown"
                first_name = member.user.first_name or ""
                last_name = member.user.last_name or ""
                logger.info(f"Added user: {user_name}, Name: {first_name + last_name}")

            except FloodWait as e:
                logger.warning(f"Rate limit exceeded. Waiting for {e.value} seconds.")
                await asyncio.sleep(e.value)  # Wait for the rate limit to reset
            except Exception as e:
                logger.error(f"Failed to add user {member.user.id}: {e}")

    except Exception as e:
        logger.error(f"An error occurred while processing the batch: {e}")
    else:
        await asyncio.sleep(
            config.RATE_LIMIT_DELAY
        )
        logger.info(f"Wating {config.RATE_LIMIT_DELAY} second.")


def get_username_from_link(link):
    link = link.strip().replace("t.me/", "")
    return link


async def main():
    api_id = config.API_ID
    api_hash = config.API_HASH
    phone_number = config.PHONE_NUMBER
    client = Client("session", api_id, api_hash, phone_number=phone_number)

    async with client:
        groups = await filter_groups(client)
        link = input("Enter public group link or username: ")
        for idx, group in enumerate(groups, start=1):
            print(f"{idx}. {group[1]}")

        while True:
            destination = input("Select group you want to add: ")
            if not destination.isnumeric():
                print(f"Please enter a number between 1 and {len(groups)}")
            else:
                destination = int(destination)
                if destination > 0 and destination <= len(groups):
                    src = get_username_from_link(link)
                    to = groups[destination-1][0]
                    await transfer_user(client, src,to)
                    break
                else:
                    print(f"Please enter a number between 1 and {len(groups)}")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())