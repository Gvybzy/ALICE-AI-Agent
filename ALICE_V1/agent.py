import subprocess
import os
import datetime
import time
import shutil
import json
import string
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET


USERNAME = os.getlogin()

# ============================================================
# APP DICTIONARY
# ============================================================
APPS = {
    # Browsers
    "edge": "msedge",

    # Windows built-in
    "notepad": "notepad",
    "calculator": "calc",
    "calc": "calc",
    "cmd": "cmd",
    "command prompt": "cmd",
    "powershell": "powershell",
    "explorer": "explorer",
    "file explorer": "explorer",
    "task manager": "taskmgr",
    "paint": "mspaint",
    "snipping tool": "snippingtool",
    "ss": "snippingtool",
    "control panel": "control",
    "control": "control",
    "settings": "ms-settings:",
    "setting": "ms-settings:",

    # Websites
    "youtube": "start https://youtube.com",
    "yt": "start https://youtube.com",
    "github": "start https://github.com",
    "gmail": "start https://gmail.com",
    "claude": "start https://claude.ai",
    "deepseek": "start https://chat.deepseek.com",
    "maps": "start https://google.com/maps",
    "gdrive": "start https://drive.google.com",
    "facebook": "start https://facebook.com",
    "fb": "start https://facebook.com",
}

# Everyday apps (Discord, Steam, VS Code, Brave, Office, etc.) are NOT
# hardcoded here since install paths differ per machine/user. Add your own
# with the in-app "add" command, e.g.:
#   add discord C:\Users\YourName\AppData\Local\Discord\app-X.X.X\Discord.exe
#   add steam "C:\Program Files (x86)\Steam\Steam.exe"
#   add vs code C:\Users\YourName\AppData\Local\Programs\Microsoft VS Code\Code.exe
# These get saved to saved_apps.json and reloaded automatically next run.

SEARCH_PATHS = [
    r"C:\Program Files",
    r"C:\Program Files (x86)",
    r"C:\Users\{}\AppData\Local".format(os.getlogin()),
    r"C:\Users\{}\AppData\Local\Programs".format(os.getlogin()),
    r"C:\Users\{}\AppData\Roaming".format(os.getlogin()),
]

# Folder this script lives in - works no matter where you clone/place it.
AGENT_FOLDER = os.path.dirname(os.path.abspath(__file__))
SAVED_APPS_FILE = os.path.join(AGENT_FOLDER, "saved_apps.json")


# ============================================================
# SAVE / LOAD ADDED APPS
# ============================================================
def load_saved_apps():
    if os.path.exists(SAVED_APPS_FILE):
        with open(SAVED_APPS_FILE, "r") as f:
            saved = json.load(f)
            APPS.update(saved)


def save_app(name, path):
    saved = {}
    if os.path.exists(SAVED_APPS_FILE):
        with open(SAVED_APPS_FILE, "r") as f:
            saved = json.load(f)
    saved[name] = path
    with open(SAVED_APPS_FILE, "w") as f:
        json.dump(saved, f, indent=2)


# ============================================================
# TEXT TO SPEECH
# ============================================================
def speak(text):
    try:
        safe_text = text.replace('"', "'")
        ps_cmd = f'''Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.SelectVoice("Microsoft Zira Desktop"); $s.Speak("{safe_text}")'''
        subprocess.Popen(
            ["powershell", "-Command", ps_cmd],
            shell=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except:
        pass


# ============================================================
# NEWS
# ============================================================
def get_news(country="US"):
    """Get top 5 news headlines from Google News RSS."""
    try:
        if country == "PH":
            url = "https://news.google.com/rss?hl=en-PH&gl=PH&ceid=PH:en"
        else:
            url = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
            
        with urllib.request.urlopen(url, timeout=10) as response:
            data = response.read()
        
        root = ET.fromstring(data)
        items = root.findall(".//item")[:5]
        
        headlines = []
        for item in items:
            title = item.find("title").text if item.find("title") is not None else "No title"
            source = item.find("source").text if item.find("source") is not None else ""
            headlines.append((title, source))
        
        return headlines
    except:
        return None

def get_location():
    """Get user's country from IP address."""
    try:
        url = "http://ip-api.com/json/"
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read())
            return data.get("countryCode", "US")
    except:
        return "US"


# ============================================================
# WEATHER
# ============================================================
def get_weather(location):
    """Get current weather for a location using wttr.in (no API key required)."""
    try:
        quoted = urllib.parse.quote(location)
        url = f"https://wttr.in/{quoted}?format=j1"
        req = urllib.request.Request(url, headers={"User-Agent": "curl/7.64.1"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())

        current = data["current_condition"][0]
        area = data["nearest_area"][0]

        place = area["areaName"][0]["value"]
        region = area["region"][0]["value"]
        country = area["country"][0]["value"]
        location_str = ", ".join(p for p in [place, region, country] if p)

        return {
            "location": location_str or location,
            "description": current["weatherDesc"][0]["value"],
            "temp_c": current["temp_C"],
            "temp_f": current["temp_F"],
            "feels_c": current["FeelsLikeC"],
            "feels_f": current["FeelsLikeF"],
            "humidity": current["humidity"],
            "wind_kmph": current["windspeedKmph"],
        }
    except Exception:
        return None

# ============================================================
# CORE FUNCTIONS
# ============================================================
def listen():
    ps_script = os.path.join(AGENT_FOLDER, "listen.ps1")
    result = subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-File", ps_script],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()


def center(text):
    terminal_width = shutil.get_terminal_size().columns
    return text.center(terminal_width)


def separator():
    print(center("-" * 30))
    print()


def print_banner():
    print()
    print(center(r"  _____          ____               ____             _____              ______   "))
    print(center(r"  ___|\    \        |    |             |    |        ___|\    \         ___|\     \  "))
    print(center(r" /    /\    \       |    |             |    |       /    /\    \       |     \     \ "))
    print(center(r"|    |  |    |      |    |             |    |      |    |  |    |      |     ,_____/|"))
    print(center(r"|    |__|    |      |    |  ____       |    |      |    |  |____|      |     \--'\_|/"))
    print(center(r"|    .--.    |      |    | |    |      |    |      |    |   ____       |     /___/|  "))
    print(center(r"|    |  |    |      |    | |    |      |    |      |    |  |    |      |     \____|\ "))
    print(center(r"|____|  |____|      |____|/____/|      |____|      |\ ___\/    /|      |____ '     /|"))
    print(center(r"|    |  |    |      |    |     ||      |    |      | |   /____/ |      |    /_____/ |"))
    print(center(r"|____|  |____|      |____|_____|/      |____|       \|___|    | /      |____|     | /"))
    print(center(r"  \(      )/          \(    )/           \(           \( |____|/         \( |_____|/ "))
    print(center(r"   '      '            '    '             '            '   )/             '    )/    "))
    print(center(r"                                                           '                   '     "))
    print()


def print_home_screen(greeting):
    print_banner()
    print(center("=" * 40))
    print(center(f"{greeting}, Doctor"))
    print(center("=" * 40))
    print(center("Type a command, 'voice', or 'help'"))
    print(center("─" * 30))
    print()


def open_app(app_name):
    app_name_lower = app_name.lower().strip()
    command = APPS.get(app_name_lower)

    if "\\" in app_name or app_name.endswith(".exe"):
        display_name = os.path.basename(app_name).replace(".exe", "")
        try_open(app_name)
        print(center(f"Opened: {display_name}"))
        speak(f"Opening {display_name}")
        separator()
        return

    if command:
        try_open(command)
        print(center(f"Opened: {app_name}"))
        speak(f"Opening {app_name}")
        separator()
        return

    print(center(f"Sorry, I don't know '{app_name}'."))
    print(center("Type 'help' to see what I can open."))
    separator()


def try_open(command):
    try:
        if command.startswith("start "):
            os.system(command)
        elif command.startswith("ms-"):
            os.system(f"start {command}")
        elif command.startswith('"') and " --" in command:
            os.system(f'start "" {command}')
        else:
            try:
                subprocess.Popen([command], shell=False)
            except:
                os.system(f'start "" "{command}"')
        return True
    except Exception as e:
        print(center(f"Couldn't open that: {e}"))
        return False


def launch(args):
    try:
        subprocess.Popen(args, shell=False)
        return True
    except Exception as e:
        print(center(f"Couldn't open that: {e}"))
        return False


def launch_configured(name):
    """Launch an app from APPS by name (for use in modes). Prints a hint
    to 'add' it first if it hasn't been configured on this machine yet."""
    command = APPS.get(name)
    if not command:
        print(center(f"'{name}' isn't set up. Add it with: add {name} [path to .exe]"))
        return False
    return try_open(command)


def search_for_app(keyword):
    keyword = keyword.lower()
    for folder in SEARCH_PATHS:
        if not os.path.exists(folder):
            continue
        for root, dirs, files in os.walk(folder):
            depth = os.path.relpath(root, folder).count(os.sep)
            if depth > 2:
                continue
            for file in files:
                if keyword in file.lower() and file.endswith('.exe'):
                    return os.path.join(root, file)
    return None


def search_for_folder(keyword):
    keyword = keyword.lower()
    drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]
    
    for drive in drives:
        for dirpath, dirnames, filenames in os.walk(drive):
            depth = os.path.relpath(dirpath, drive).count(os.sep)
            if depth > 3:
                continue
            for dirname in dirnames:
                if keyword in dirname.lower():
                    return os.path.join(dirpath, dirname)
    return None


def handle_add(user_input):
    parts = user_input.split(" ", 2)
    if len(parts) < 3:
        print(center("Format: add [name] [full path]"))
        separator()
        return
    name = parts[1].lower()
    path = parts[2].strip('"')
    if os.path.exists(path):
        APPS[name] = path
        save_app(name, path)
        print(center(f"Added: '{name}' (saved)"))
        speak(f"Added {name}")
    else:
        print(center(f"Path doesn't exist: {path}"))
    separator()


def handle_search(user_input):
    keyword = user_input.replace("search ", "", 1).strip()
    if not keyword:
        print(center("Format: search [keyword]"))
        separator()
        return
    
    if keyword.lower() in APPS:
        print(center(f"Found: '{keyword}' is ready to open"))
        separator()
        return
    
    print(center(f"Searching for '{keyword}'..."))
    found = search_for_app(keyword)
    if found:
        print(center(f"Found: '{keyword}' is on your system"))
        print(center(f"Type 'add {keyword}' to save it"))
    else:
        print(center(f"Not found. Type 'add {keyword} [path]' to add it manually."))
    separator()


def show_help():
    os.system('cls')
    print_banner()
    print()
    print(center("-" * 30))
    print(center("MODES"))
    print(center("-" * 30))
    print(center("school"))
    print(center("v"))
    print(center("Open school portals"))
    print()
    print()
    print(center("study"))
    print(center("v"))
    print(center("VS Code + Brave + YouTube"))
    print()
    print()
    print(center("gaming"))
    print(center("v"))
    print(center("Steam"))
    print()
    print()
    print(center("chill"))
    print(center("v"))
    print(center("Facebook + YouTube"))
    print()
    print()
    print(center("coding"))
    print(center("v"))
    print(center("VS Code + Claude + DeepSeek + YouTube"))
    print()
    print()
    print(center("-" * 30))
    print(center("APPS & WEBSITES"))
    print(center("-" * 30))
    apps = sorted(set(APPS.keys()))
    COL_WIDTH = 16
    COLS = 3
    row = ""
    count = 0
    for app in apps:
        row += f"{app:<{COL_WIDTH}}"
        count += 1
        if count % COLS == 0:
            print(center(row))
            row = ""
    if row:
        row = row.ljust(COL_WIDTH * COLS)
        print(center(row))
    print()
    print()
    print(center("-" * 30))
    print(center("COMMANDS"))
    print(center("-" * 30))
    print(center("[name]"))
    print(center("v"))
    print(center("Open app or website"))
    print()
    print()
    print(center("help"))
    print(center("v"))
    print(center("Show this menu"))
    print()
    print()
    print(center("search [app]"))
    print(center("v"))
    print(center("Find an app on your system"))
    print()
    print()
    print(center("folder [name]"))
    print(center("v"))
    print(center("Search and open a folder"))
    print()
    print()
    print(center("add [name] [path]"))
    print(center("v"))
    print(center("Add a new app (auto-saved)"))
    print()
    print()
    print(center("news"))
    print(center("v"))
    print(center("International headlines"))
    print()
    print()
    print(center("local news"))
    print(center("v"))
    print(center("Philippine headlines"))
    print()
    print()
    print(center("weather [location]"))
    print(center("v"))
    print(center("Current weather for a location"))
    print()
    print()
    print(center("exit"))
    print(center("v"))
    print(center("Close the agent"))
    print()
    print()
    print(center("-" * 30))
    print(center("SYSTEM"))
    print(center("-" * 30))
    print(center("lock"))
    print(center("v"))
    print(center("Lock screen"))
    print()
    print()
    print(center("sleep"))
    print(center("v"))
    print(center("Put laptop to sleep"))
    print()
    print()
    print(center("shutdown"))
    print(center("v"))
    print(center("Shutdown in 10 seconds"))
    print()
    print()
    print(center("restart"))
    print(center("v"))
    print(center("Restart in 10 seconds"))    
    print(center("-" * 30))
    print()
    print()


def main():
    load_saved_apps()
    
    hour = datetime.datetime.now().hour
    if hour < 12:
        greeting = "Good morning"
    elif hour < 18:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    print_home_screen(greeting)
    #Edit your name next to greeting if you want
    speak(f"{greeting}. What should we do today?")

    while True:
        user_input = input("                                                         ").strip()
        print(center("─" * 30))

        if not user_input:
            continue

        command = user_input.lower()

        if command in ["exit", "quit", "bye"]:
            print(center("Closing in 3..."))
            speak("Closing in 3")
            time.sleep(2)
            print(center("2..."))
            speak("2")
            time.sleep(1)
            print(center("1..."))
            speak("1")
            time.sleep(1)
            os._exit(0)

        if command in ["help", "commands"]:
            show_help()
            continue

        if command == "voice":
            print(center("Listening... (speak now)"))
            speak("I'm listening")
            spoken = listen()
            if spoken:
                print(center(f"You said: {spoken}"))
                user_input = spoken
                command = spoken.lower()
            else:
                print(center("Sorry, didn't catch that."))
                speak("Sorry, I didn't catch that")
                separator()
                continue

        if command in ["alice", "who are you", "who are you?", "what are you", "what are you?", "what can you do", "what can you do?", "about"]:
            print()
            print(center("=" * 50))
            print(center("ALICE"))
            print(center("Your Personal AI Agent"))
            print(center("=" * 50))
            print()
            print(center("I can open your apps, websites,"))
            print(center("and launch work modes with one word."))
            print()
            print(center("Type 'help' to see everything I can do."))
            print(center("Type a name like 'discord' or 'youtube'"))
            print(center("Or try a mode: study, gaming, chill, school"))
            print()
            print(center("=" * 50))
            print()
            speak("I am ALICE, your personal AI agent")
            continue

        if command in ["clear", "clr"]:
            os.system('cls')
            print_home_screen(greeting)
            continue

        if command == "school":
            print(center("Starting school mode..."))
            # Add your own school portal URLs here, e.g.:
            # os.system("start https://portal.yourschool.edu")
            # os.system("start https://lms.yourschool.edu")
            print(center("School mode isn't configured yet."))
            print(center("Edit the 'school' section in the code to add your portal URLs."))
            speak("School mode isn't configured yet")
            separator()
            continue

        if command == "study":
            print(center("Starting study mode..."))
            launch_configured("vs code")
            launch_configured("brave")
            os.system("start https://youtube.com")
            print(center("Study mode activated"))
            speak("Study mode activated")
            separator()
            continue

        if command == "coding":
            print(center("Starting coding mode..."))
            launch_configured("vs code")
            launch_configured("brave")
            os.system("start https://chat.deepseek.com")
            os.system("start https://claude.ai")
            os.system("start https://youtube.com")
            print(center("Coding mode activated"))
            speak("Coding mode activated")
            separator()
            continue

        if command == "gaming":
            print(center("Starting gaming mode..."))
            launch_configured("steam")
            print(center("Gaming mode activated"))
            speak("Gaming mode activated")
            separator()
            continue

        if command == "chill":
            print(center("Starting chill mode..."))
            try_open(APPS.get("facebook", "start https://facebook.com"))
            os.system("start https://youtube.com")
            print(center("Chill mode activated"))
            speak("Chill mode activated.")
            separator()
            continue

        if command == "lock":
            os.system("rundll32.exe user32.dll,LockWorkStation")
            print(center("Screen locked"))
            speak("Screen locked")
            separator()
            continue

        if command == "sleep":
            print(center("Going to sleep..."))
            speak("Going to sleep")
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            separator()
            continue

        if command == "shutdown":
            print(center("Shutting down in 10 seconds..."))
            print(center("Type 'cancel' to stop"))
            speak("Shutting down in 10 seconds")
            os.system("shutdown /s /t 10")
            separator()
            continue

        if command == "restart":
            print(center("Restarting in 10 seconds..."))
            print(center("Type 'cancel' to stop"))
            speak("Restarting in 10 seconds")
            os.system("shutdown /r /t 10")
            separator()
            continue

        if command == "cancel":
            os.system("shutdown /a")
            print(center("Cancelled"))
            speak("Cancelled")
            separator()
            continue

              # --- LOCAL NEWS FIRST ---
        if command in ["local news", "ph news", "philippines news", "my news"]:
            country = get_location()
            print(center(f"Fetching news for your location..."))
            headlines = get_news(country)
            if headlines:
                print()
                print(center("=" * 50))
                print(center("LOCAL HEADLINES"))
                print(center("=" * 50))
                print()
                for i, (title, source) in enumerate(headlines, 1):
                    clean_title = title.split(" - ")[0].strip()
                    print(center(f"{i}. {clean_title}"))
                    if source:
                        print(center(f"   Source: {source}"))
                    print()
                print(center("=" * 50))
                speak("Here are your local headlines.")
            else:
                print(center("Couldn't fetch news. Check your internet."))
                speak("Couldn't fetch news. Check your internet.")
            separator()
            continue

        # --- INTERNATIONAL NEWS ---
        if command == "news" or command == "headlines":
            print(center("Fetching latest news..."))
            headlines = get_news("US")
            if headlines:
                print()
                print(center("=" * 50))
                print(center("LATEST HEADLINES"))
                print(center("=" * 50))
                print()
                for i, (title, source) in enumerate(headlines, 1):
                    clean_title = title.split(" - ")[0].strip()
                    print(center(f"{i}. {clean_title}"))
                    if source:
                        print(center(f"   Source: {source}"))
                    print()
                print(center("=" * 50))
                speak("Here are the latest headlines.")
            else:
                print(center("Couldn't fetch news. Check your internet."))
                speak("Couldn't fetch news. Check your internet.")
            separator()
            continue

        # --- WEATHER ---
        if command == "weather":
            print(center("Format: weather [location]"))
            print(center("Example: weather manila"))
            separator()
            continue

        if command.startswith("weather "):
            location = user_input[len("weather "):].strip()
            if not location:
                print(center("Format: weather [location]"))
                separator()
                continue
            print(center(f"Checking weather for '{location}'..."))
            weather = get_weather(location)
            if weather:
                print()
                print(center("=" * 50))
                print(center(f"WEATHER - {weather['location']}"))
                print(center("=" * 50))
                print()
                print(center(f"{weather['description']}"))
                print(center(f"{weather['temp_c']} C / {weather['temp_f']} F"))
                print(center(f"Feels like {weather['feels_c']} C / {weather['feels_f']} F"))
                print(center(f"Humidity: {weather['humidity']}%"))
                print(center(f"Wind: {weather['wind_kmph']} km/h"))
                print()
                print(center("=" * 50))
                speak(f"It's currently {weather['description']} and {weather['temp_c']} degrees Celsius in {weather['location']}")
            else:
                print(center(f"Couldn't fetch weather for '{location}'. Check the spelling or your internet."))
                speak("Couldn't fetch the weather. Check your internet.")
            separator()
            continue

        if command.startswith("search "):
            handle_search(user_input)
            continue

        if command.startswith("add "):
            handle_add(user_input)
            continue

        if command.startswith("folder "):
            keyword = user_input[len("folder "):].strip()
            if not keyword:
                print(center("Format: folder [name]"))
                separator()
                continue
            print(center(f"Searching for folder '{keyword}'..."))
            found = search_for_folder(keyword)
            if found:
                os.system(f'start "" "{found}"')
                print(center(f"Opened folder: {keyword}"))
                speak(f"Opening folder {keyword}")
            else:
                print(center(f"Couldn't find a folder matching '{keyword}'."))
            separator()
            continue

        if user_input.lower().startswith("open "):
            app_name = user_input[5:]
        else:
            app_name = user_input

        app_name_lower = app_name.lower().strip()
        if app_name_lower in APPS or "\\" in app_name or app_name.endswith(".exe"):
            open_app(app_name)
        else:
            found = search_for_folder(app_name)
            if found:
                os.system(f'start "" "{found}"')
                print(center(f"Opened folder: {app_name}"))
                speak(f"Opening folder {app_name}")
            else:
                print(center(f"Sorry, I don't know '{app_name}'."))
                print(center("Type 'help' to see what I can open."))
            separator()


if __name__ == "__main__":
    main()