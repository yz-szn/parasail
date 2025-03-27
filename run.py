import os
import sys
import asyncio
from tools import parasail
from utils.logger import log
from colorama import init, Fore, Style

init(autoreset=True)

def welcome():
    print(
        f"""
        {Fore.GREEN + Style.BRIGHT}
         /$$   /$$ /$$$$$$$$        /$$$$$$$ /$$$$$$$$ /$$$$$$$             
        | $$  | $$|____ /$$/       /$$_____/|____ /$$/| $$__  $$            
        | $$  | $$   /$$$$/       |  $$$$$$    /$$$$/ | $$  \ $$            
        | $$  | $$  /$$__/         \____  $$  /$$__/  | $$  | $$           
        |  $$$$$$$ /$$$$$$$$       /$$$$$$$/ /$$$$$$$$| $$  | $$           
         \____  $$|________/      |_______/ |________/|__/  |__/           
        /$$  | $$ ______________________________________________                                                     
       |  $$$$$$/ ============ Nothing's Impossible !! =========                                       
        \______/
        """
    )

welcome()
print(f"{Fore.CYAN}{'=' * 22}")
print(Fore.CYAN + "#### Parasail BOT ####")
print(f"{Fore.CYAN}{'=' * 22}")

async def main():
    while True:
        print(Fore.YELLOW + "\n[=== PILIH MENU ===]")
        print(Fore.CYAN + "1. Parasail BOT")
        print(Fore.CYAN + "2. Keluar")

        choice = input(Fore.GREEN + "Masukkan pilihan (1-2): ").strip()

        if choice == "1":
            log("Parasail BOT", "Memulai proses ", "INFO")
            parasail.run() 
        elif choice == "2":
            log("Keluar", "Keluar dari program...", "INFO")
            return
        else:
            log("Parasail BOT", "Pilihan tidak valid! Mohon pilih antara 1-2.", "ERROR")

if __name__ == "__main__":
    asyncio.run(main())