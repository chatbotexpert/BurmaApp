import asyncio
import os
import socks
from telethon import TelegramClient

api_id = 32729516
api_hash = 'b9cbc7204ce06cb5d678580309dca6c9'

async def connect_with_retry(client, max_retries=5):
    """Attempts to connect the client with retries."""
    for attempt in range(1, max_retries + 1):
        try:
            print(f"Attempting to connect (Attempt {attempt}/{max_retries})...")
            await client.connect()
            print("Connected successfully!")
            return True
        except (ConnectionError, asyncio.IncompleteReadError) as e:
            print(f"Connection attempt {attempt} failed: {e}")
            if attempt < max_retries:
                wait_time = attempt * 2
                print(f"Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
            else:
                print("Max retries reached. Connection failed.")
    return False

async def main():
    print("=== Telegram Setup & Troubleshooting ===")
    
    # Optional Proxy Configuration
    proxy = None
    use_proxy = input("Do you want to use a proxy? (y/n): ").lower() == 'y'
    if use_proxy:
        print("Enter proxy details (SOCKS5):")
        addr = input("  Address (e.g., 127.0.0.1): ")
        port = int(input("  Port (e.g., 1080): "))
        proxy = (socks.SOCKS5, addr, port)

    print("\nInitializing Telegram Client...")
    client = TelegramClient('telegram_session', api_id, api_hash, proxy=proxy)
    
    if not await connect_with_retry(client):
        print("\n[!] Could not establish connection to Telegram.")
        print("Possible causes:")
        print("1. Telegram is blocked in your region (try using a SOCKS5 proxy).")
        print("2. Your internet connection is unstable.")
        print("3. API_ID or API_HASH are restricted.")
        return

    try:
        if not await client.is_user_authorized():
            print("\nAuthentication required.")
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
        
        print("\nSuccessfully authorized!")
        print("Session file 'telegram_session.session' has been created.")
        print("You can now run the scraper.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
