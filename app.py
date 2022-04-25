import asyncio
import re
from pyrogram import Client
from pyrogram.errors import FloodWait, BadRequest


api_id = # Enter your api_id as an integer here
api_hash = # Enter your api_hash as a string here

channel_username = input("Enter the channel's username without @ or enter 0 to continue the last session:")


def write(text, file_name):
    file = open(file_name, "a", encoding="UTF-8")
    file.write(str(text))
    file.write("\n")
    file.close()

def done_link(link):
    done_links_file = open("done-links.txt", "a")
    done_links_file.write(link + "\n")
    done_links_file.close()
    

def get_links(channel_id):
    links = []
    with Client("my_account", api_id, api_hash) as app:
        for message in app.iter_history(channel_id):
            text = message.text or message.caption

            usernames = re.findall("\B@\w+", str((text)))
            urls = re.findall("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", str(text))
            
            links.extend(usernames)
            links.extend(urls)
            
    links = list(dict.fromkeys(links))
    
    # convert t.me/channel to @channel
    new_links = []
    for link in links:
        if ("+" not in link) and (link.count("/") != 4 ) and (link.count("@") == 0) and (len(link.split("/")) >= 4):
            link = "@" + link.split("/")[3]
        new_links.append(link)
    
    return new_links
      

def get_admins(group_id):
    print("Getting admins for: " + group_id)
    async def main():
        async with Client("my_account", api_id, api_hash) as app:     
            try:
                chat = await app.get_chat(group_id)
            except BadRequest:
                done_link(group_id)
                print(group_id + " link was expired.")
                return
            if chat.type == "supergroup" or chat.type == "group":
                if not hasattr(chat, "id"):
                    try:
                        await app.join_chat(group_id)
                    except FloodWait as e:
                        print("FloodWait for: " + str(e.x) + " secnods")
                        await asyncio.sleep(e.x)
                        
                    try:
                        chat = await app.get_chat(group_id)
                    except FloodWait as e:
                        print("FloodWait for: " + str(e.x) + " secnods")
                        await asyncio.sleep(e.x)
                        
                    try:
                        admins = await app.get_chat_members(chat.id, filter="administrators")
                    except FloodWait as e:
                        print("FloodWait for: " + str(e.x) + " secnods")
                        await asyncio.sleep(e.x)
                    
                    try:
                        await app.leave_chat(chat.id)
                    except FloodWait as e:
                        print("FloodWait for: " + str(e.x) + " secnods")
                        await asyncio.sleep(e.x)
                        
                    for admin in admins:
                        admin_username = admin.user.username
                        if admin_username is not None and not admin_username.lower().endswith("bot"):
                            write(admin.user.username, "admins.txt")
                    done_link(group_id)
                    
                else:
                    try:
                        admins = await app.get_chat_members(chat.id, filter="administrators")
                    except FloodWait as e:
                        print("FloodWait for: " + str(e.x) + " secnods")
                        await asyncio.sleep(e.x)
                    for admin in admins:
                        admin_username = admin.user.username
                        if admin_username is not None and not admin_username.lower().endswith("bot"):
                            write(admin.user.username, "admins.txt")
                    done_link(group_id)
                    print("Recieved usernames for: " + group_id)
            else:
                done_link(group_id)
                print(group_id + " wasn't a group/supergroup." )
                        
                
                
    asyncio.run(main())

if channel_username == "0":
    with open("links.txt", "r", encoding="UTF-8") as f:
        previous_links = f.readlines()
    with open("done-links.txt", "r", encoding="UTF-8") as f:
        done_links = f.readlines()
        
    links = []
    for link in previous_links:
        if link not in done_links:
            links.append(link)
    
    f = open("links.txt", "w")
    f.close()
    f = open("done-links.txt", "w")
    f.close()
    
    # add them to a file
    for link in links:
        write(link, "links.txt")
            
else:    
    # Clear the content
    f = open("admins.txt", "w")
    f.close()
    f = open("links.txt", "w")
    f.close()
    f = open("done-links.txt", "w")
    f.close()
    # Get links    
    print("+Getting links of the channel.")
    links = get_links(channel_username)
    
    # add them to a file
    for link in links:
        write(link, "links.txt")
    print("+Recieved the channel's links.")

for link in links:
    get_admins(link)
   
