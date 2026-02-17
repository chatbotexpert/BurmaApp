import asyncio
from telethon import TelegramClient

api_id = 32729516
api_hash = 'b9cbc7204ce06cb5d678580309dca6c9'

async def main():
    print("Initializing Telegram Client...")
    client = TelegramClient('telegram_session', api_id, api_hash)
    
    print("Attempting to connect...")
    await client.connect()
    
    if not await client.is_user_authorized():
        print("Authentication required.")
        phone = input("Enter your phone number (with country code, e.g. +1234567890): ")
        await client.send_code_request(phone)
        
        try:
            code = input("Enter the code you received: ")
            await client.sign_in(phone, code)
        except Exception as e:
            print(f"Error signing in: {e}")
            password = input("If you have 2FA enabled, enter your password (otherwise press enter): ")
            if password:
                await client.sign_in(password=password)
    
    print("Successfully authorized!")
    print("Session file 'telegram_session.session' has been created.")
    print("You can now run the scraper.")
    
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
