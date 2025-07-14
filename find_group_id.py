import os
import asyncio
from pyrogram import Client
from dotenv import load_dotenv
import sys

load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

async def find_group_id(group_name):
    """Versión simplificada que solo busca y retorna el ID del grupo"""
    async with Client("my_account", api_id=api_id, api_hash=api_hash) as app:
        async for dialog in app.get_dialogs():
            chat = dialog.chat
            chat_name = chat.title or chat.first_name or chat.last_name or ""
            
            if group_name.lower() in chat_name.lower():
                print(f"\n✅ Encontrado: {chat_name}")
                print(f"📌 ID: {chat.id}")
                return chat.id
    
    print(f"\n❌ No se encontró el grupo '{group_name}'")
    return None

async def main():
    if len(sys.argv) > 1:
        # Si se pasa el nombre como argumento
        group_name = " ".join(sys.argv[1:])
    else:
        # Si no, pedirlo interactivamente
        group_name = input("Nombre del grupo: ").strip()
    
    if not group_name:
        print("❌ Debes proporcionar un nombre de grupo")
        return
    
    group_id = await find_group_id(group_name)
    
    if group_id:
        print(f"\nPuedes usar este ID en tu script: {group_id}")

if __name__ == "__main__":
    asyncio.run(main())
