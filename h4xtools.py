#!/usr/bin/env python3

"""
 Copyright (c) 2022 GNU GENERAL PUBLIC

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <https://www.gnu.org/licenses/>.
 """

import os
import time
from colorama import Fore
import socket
import requests
from utils import email_search, search_username, ig_scrape, whois_lookup, webhook_spammer, ip_scanner, ip_lookup, \
    phonenumber_lookup, websearch, smsbomber, tokenlogger_generator, web_scrape, wifi_finder

if os.name == "nt":
    os.system("cls")
    os.system("title H4X-Tools")
if os.name == "posix":
    os.system("clear")

version = "0.2.9"


# Check if user has internet available
def internet_check():
    try:
        socket.create_connection(("www.google.com", 80))
        print(Fore.GREEN + "\n[*] Internet Connection is Available!")
        return None
    except OSError:
        print(Fore.RED + "\n[*] Warning! Internet Connection is Unavailable!")
        return None


# Checks the version from an external url
def version_check():
    url = "https://raw.githubusercontent.com/V1li/H4X-Tools-ver/master/version.txt"
    # Get the version from the url and return it
    try:
        r = requests.get(url)
        return r.text
    except requests.exceptions.ConnectionError:
        print(Fore.RED + "[*] Error! Couldn't connect to the server!")


# Banner
def print_banner():
    print(Fore.CYAN + f"""
[+]
|
|    //    / /        \\ / /      /__  ___/ //   ) ) //   ) ) / /        //   ) )
|   //___ / //___/ /   \  /         / /    //   / / //   / / / /        ((
|  / ___   /____  /    / /   ____  / /    //   / / //   / / / /           \\
| //    / /    / /    / /\\       / /    //   / / //   / / / /              ) )
|//    / /    / /    / /  \\     / /    ((___/ / ((___/ / / /____/ / ((___ / /  ~~v{version}
|
| by Vili (https://vili.dev)
|
| NOTE! THIS TOOL IS ONLY FOR EDUCATIONAL PURPOSES, DONT USE IT TO DO SOMETHING ILLEGAL!
|
[+]
    """)


# About
def print_about():
    print(f"{Fore.GREEN}H4X-Tools, collection of multiple tools for scraping, OSINT and more.\n")
    print(f"{Fore.GREEN}Completely open source and free to use! Feel free to contribute.\n")
    print(f"{Fore.GREEN}Repo: https://github.com/v1li/h4x-tools\n")
    print(f"{Fore.RED}NOTE! THIS TOOL IS ONLY FOR EDUCATIONAL PURPOSES, DONT USE IT TO DO SOMETHING ILLEGAL!\n")


def print_donate():
    print(f"""{Fore.GREEN}
If you want to support me and my work, you can donate to these addresses: \n
| BCH: bitcoincash:qqk9qkm7j6lc5dzjwsylnh6q3ytp8pp7yunc6tt2nv
| BTC: bitcoin:153JzmhHeeSMGrzNA6ASwKE2zpRwKDNk2Y
| ETH: 153JzmhHeeSMGrzNA6ASwKE2zpRwKDNk2Y
            """)


# Main menu
def print_menu():
    print(Fore.CYAN)
    print("[1] IG Scrape          ||   [2] Web Search")
    print("[3] Phone Lookup       ||   [4] IP Lookup")
    print("[5] Username Search    ||   [6] Email Search")
    print("[7] IP Scanner         ||   [8] Webhook Spammer")
    print("[9] WhoIs              ||   [10] SMS Bomber (US Only!)")
    print("[11] TLogger Generator ||   [12] Web Scrape")
    print("[13] WiFi Finder       ||   [14] About")
    print("[15] Donate            ||   [16] Update")
    print("[17] Exit")
    print("\n")


# Handle for IG scrape
def handle_ig_scrape():
    if os.path.exists(".igscrape"):
        if os.stat(".igscrape/username.txt").st_size == 0 or os.stat(".igscrape/password.txt").st_size == 0:
            print(Fore.RED + "[*] username.txt/password.txt is empty!")
            return

        target = str(input("Enter a Username : \t")).replace(" ", "_")
        ig_scrape.Scrape(target)
        time.sleep(1)
    else:
        os.mkdir(".igscrape")
        print(Fore.YELLOW + "[*] It appears that you are running this tool for the first time!")
        print(
            Fore.YELLOW + "[*] Put your credentials in the file named 'username.txt' and 'password.txt' in the '.igscrape' folder!")
        b = input(Fore.YELLOW + "[*] Or do you want to type your credentials now? (y/n) : ")
        if b == "y":
            c = input("[*] Enter your username : \t")
            d = input("[*] Enter your password : \t")
            with open(".igscrape/username.txt", "w") as f:
                f.write(c)
            with open(".igscrape/password.txt", "w") as f:
                f.write(d)
            print(Fore.GREEN + "[*] Credentials saved!")
            time.sleep(2)
        print(Fore.GREEN + "[*] Done! Now you can run the tool again!")


# Handle for web search.
def handle_web_search():
    query = str(input("Search query : \t"))
    websearch.Search(query)


# Handle for Phone lookup
def handle_phone_lookup():
    no = str(input("Enter a phone-number with country code : \t"))
    phonenumber_lookup.LookUp(no)


# Handle for IP lookup
def handle_ip_lookup():
    ip = str(input("Enter a IP address OR domain : \t"))
    ip_lookup.Lookup(ip)


# Handle for username search
def handle_username_search():
    username = str(input("Enter a Username : \t")).replace(" ", "_")
    search_username.Maigret(username)


# Handle for email search
def handle_email_search():
    email = str(input("Enter a email address : \t"))
    email_search.Holehe(email)


# Handle for IP scanner
def handle_ip_scanner():
    domain = str(input("Enter a domain : \t"))
    ip_scanner.Scan(domain)


# Handle for Discord webhook spammer
def handle_webhook_spammer():
    url = str(input("Enter a webhook url : \t"))
    amount = int(input("Enter a amount of messages : \t"))
    message = str(input("Enter a message : \t"))
    username = str(input("Enter a username : \t"))
    webhook_spammer.Spam(url, amount, message, username)


# Handle for whois lookup
def handle_whois_lookup():
    domain = str(input("Enter a domain : \t"))
    whois_lookup.Lookup(domain)


# Handle for SMS bomber
def handle_sms_bomber():
    number = str(input("Enter mobile number : \t")).strip("+")
    count = int(input("Enter number of Messages : \t"))
    throttle = int(input("Enter time of sleep : \t"))
    smsbomber.Spam(number, count, throttle)


# Handle for Discord token logger generator
def handle_dtlg():
    print(f"{Fore.RED}Note! Tokenlogger only works on Windows machines!")
    webhook_url = input(f"{Fore.GREEN}Enter a webhook url : \t")
    tokenlogger_generator.Create(webhook_url)


# Handle for web scrape
def handle_web_scrape():
    url = str(input(f"Enter a url : \t"))
    web_scrape.Scrape(url)


# Handle for WiFi finder
def handle_wifi_finder():
    print(f"{Fore.GREEN}Scanning for nearby WiFi networks...")
    wifi_finder.Scan()


# Handle for update
def update():
    try:
        os.system("git fetch && git pull")
    except Exception as e:
        print(f"{Fore.RED}", e)


# Create a dictionary to map menu options to corresponding functions
menu_options = {
    "1": handle_ig_scrape,
    "2": handle_web_search,
    "3": handle_phone_lookup,
    "4": handle_ip_lookup,
    "5": handle_username_search,
    "6": handle_email_search,
    "7": handle_ip_scanner,
    "8": handle_webhook_spammer,
    "9": handle_whois_lookup,
    "10": handle_sms_bomber,
    "11": handle_dtlg,
    "12": handle_web_scrape,
    "13": handle_wifi_finder,
    "14": print_about,
    "15": print_donate,
    "16": update
}


# Main
def __main__():
    version_from_url = version_check()
    # Check if the user is using the latest version
    if version.strip() != version_from_url.strip():
        print(Fore.RED + f"[*] Version mismatch! ({version}) ... Should be ({version_from_url})")
        print("Check for updates..! (https://github.com/v1li/h4x-tools)")
        time.sleep(3)
    else:
        print(Fore.GREEN + f"[*] Version matches! ({version})")
        time.sleep(1)

    while True:
        print_banner()
        time.sleep(1)
        print_menu()
        time.sleep(1)
        a = input("[*] Select your option : \t")

        if a in menu_options:
            menu_options[a]()  # Call the corresponding function based on the selected option
            time.sleep(3)  # Sleep so user has time to see results.
        elif a == "17":
            print(Fore.RED + "Exiting...")
            print(Fore.GREEN + "Thanks for using H4X-Tools! Remember to star this on GitHub! \n -Vili")
            time.sleep(1)
            print(Fore.RESET)
            break
        else:
            print(Fore.RED + "Invalid option!")
            time.sleep(2)


if __name__ == "__main__":
    __main__()
