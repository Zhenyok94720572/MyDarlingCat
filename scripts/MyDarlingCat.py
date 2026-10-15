import json
import os
import sys
import datetime
import subprocess

def ensure_console():
    if os.name != "nt":
        return
    if "--console" in sys.argv:
        return
    if getattr(sys, "frozen", False):
        return

    exe = sys.executable.lower()
    is_pythonw = exe.endswith("pythonw.exe")

    if is_pythonw:
        relaunch_with_console()
        os._exit(0)

    try:
        if sys.stdout is None or sys.stdin is None:
            relaunch_with_console()
            os._exit(0)
    except Exception:
        relaunch_with_console()
        os._exit(0)


def relaunch_with_console():
    exe = sys.executable
    python_exe = exe.replace("pythonw.exe", "python.exe")
    if not os.path.exists(python_exe):
        python_exe = "python"

    script = os.path.abspath(sys.argv[0])
    cmd = [python_exe, script, "--console"]

    CREATE_NEW_CONSOLE = 0x00000010
    try:
        subprocess.Popen(cmd, creationflags=CREATE_NEW_CONSOLE, cwd=os.path.dirname(script))
    except Exception:
        pass


ensure_console()


def get_app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(sys.argv[0]))


def get_game_root():
    app_dir = get_app_dir()
    parent = os.path.dirname(app_dir)
    if os.path.isdir(os.path.join(parent, "images")):
        return parent
    if os.path.isdir(os.path.join(app_dir, "images")):
        return app_dir
    return app_dir


def get_desktop_dir():
    home = os.path.expanduser("~")
    candidates = [
        os.path.join(home, "Desktop"),
        os.path.join(home, "Рабочий стол"),
        os.path.join(home, "OneDrive", "Desktop"),
        os.path.join(home, "OneDrive", "Рабочий стол"),
    ]
    for c in candidates:
        if os.path.isdir(c):
            return c
    return home


APP_DIR = get_app_dir()
GAME_ROOT = get_game_root()
DESKTOP_DIR = get_desktop_dir()

PNG_ICON = os.path.join(GAME_ROOT, "images", "ConsoleCat.png")
DATA_DIR = os.path.join(GAME_ROOT, "data")
try:
    os.makedirs(DATA_DIR, exist_ok=True)
except Exception:
    DATA_DIR = GAME_ROOT

ICO_ICON = os.path.join(DATA_DIR, "ConsoleCat.ico")

CONFIG_FILE = os.path.join(DATA_DIR, "config.json")
LOCK_FILE = os.path.join(DATA_DIR, "lock.json")
FORGIVE_FILE = os.path.join(DATA_DIR, "forgiven.json")

if getattr(sys, "frozen", False):
    SCRIPT_FILE = os.path.abspath(sys.executable)
else:
    SCRIPT_FILE = os.path.abspath(sys.argv[0])


def convert_png_to_ico():
    if os.path.exists(ICO_ICON):
        return True
    if not os.path.exists(PNG_ICON):
        return False
    try:
        from PIL import Image
        img = Image.open(PNG_ICON)
        img = img.convert("RGBA")
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        img.save(ICO_ICON, format="ICO", sizes=sizes)
        return True
    except Exception:
        pass

    try:
        ps = (
            "Add-Type -AssemblyName System.Drawing; "
            f"$png = [System.Drawing.Image]::FromFile('{PNG_ICON}'); "
            f"$bmp = New-Object System.Drawing.Bitmap($png, 256, 256); "
            f"$icon = [System.Drawing.Icon]::FromHandle($bmp.GetHicon()); "
            f"$fs = [System.IO.File]::Create('{ICO_ICON}'); "
            "$icon.Save($fs); "
            "$fs.Close()"
        )
        subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command", ps],
            capture_output=True, timeout=20
        )
        return os.path.exists(ICO_ICON)
    except Exception:
        return False


def create_desktop_shortcut():
    shortcut_path = os.path.join(DESKTOP_DIR, "My Darling Cat.lnk")
    if os.path.exists(shortcut_path):
        return

    convert_png_to_ico()

    if getattr(sys, "frozen", False):
        target = SCRIPT_FILE
        workdir = os.path.dirname(SCRIPT_FILE)
        args = ""
    else:
        target = sys.executable
        workdir = os.path.dirname(SCRIPT_FILE)
        args = f'"{SCRIPT_FILE}"'

    if os.path.exists(ICO_ICON):
        icon_loc = ICO_ICON
    else:
        icon_loc = target

    ps = (
        "$W = New-Object -ComObject WScript.Shell; "
        f"$S = $W.CreateShortcut('{shortcut_path}'); "
        f"$S.TargetPath = '{target}'; "
        f"$S.Arguments = '{args}'; "
        f"$S.WorkingDirectory = '{workdir}'; "
        f"$S.IconLocation = '{icon_loc}'; "
        "$S.Save()"
    )
    try:
        subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command", ps],
            capture_output=True, timeout=15
        )
    except Exception:
        pass


create_desktop_shortcut()


TEXTS = {
    "ru": {
        "choose_lang": "Выберите язык / Choose language",
        "lang_ru": "1 - Русский",
        "lang_en": "2 - English",
        "lang_err": "Неверный ввод! Введите 1 или 2.",
        "greet": "Привет! Хочешь забрать кота из приюта?",
        "yes_prompt": "Нажми Enter чтобы согласиться (Да!)...",
        "ask_name": "Как ты назовёшь кота?",
        "name_err": "Введи имя!",
        "ask_sex": "Кто твой кот?",
        "sex_m": "1 - Мальчик",
        "sex_f": "2 - Девочка",
        "sex_err": "Неверный ввод! Введите 1 или 2.",
        "console_feed_m": 'Это твой кот "{}".\nЧтобы его покормить — нажми Enter!',
        "console_feed_f": 'Это твоя кошка "{}".\nЧтобы её покормить — нажми Enter!',
        "fed": "Отлично! Возвращайся завтра!",
        "already_fed": "Ты уже кормил кота! Следующее кормление через {} ч {} мин.",
        "streak": "Дней подряд: {}",
        "streak_new": "🔥 Новый рекорд! Дней подряд: {}",
        "forgot": "КАК НЕ СТЫДНО! ТЫ ЗАБЫЛ ПОКОРМИТЬ КОТА!\nМЫ ЗАБИРАЕМ ЕГО ОБРАТНО!",
        "banned": "В ТЕЧЕНИЕ ЭТОЙ НЕДЕЛИ ТЕБЕ НЕЛЬЗЯ ЗАВОДИТЬ КОТА!",
        "forgiven": "....... Я прощаю тебя",
    },
    "en": {
        "choose_lang": "Выберите язык / Choose language",
        "lang_ru": "1 - Русский",
        "lang_en": "2 - English",
        "lang_err": "Invalid input! Enter 1 or 2.",
        "greet": "Hi! Do you want to take a cat from the shelter?",
        "yes_prompt": "Press Enter to agree (Yes!)...",
        "ask_name": "What will you name the cat?",
        "name_err": "Enter a name!",
        "ask_sex": "Is your cat a boy or a girl?",
        "sex_m": "1 - Boy",
        "sex_f": "2 - Girl",
        "sex_err": "Invalid input! Enter 1 or 2.",
        "console_feed_m": 'This is your cat "{}".\nTo feed him — press Enter!',
        "console_feed_f": 'This is your cat "{}".\nTo feed her — press Enter!',
        "fed": "Great! Come back tomorrow!",
        "already_fed": "You already fed the cat! Next feeding in {} h {} min.",
        "streak": "Days in a row: {}",
        "streak_new": "🔥 New record! Days in a row: {}",
        "forgot": "SHAME ON YOU! YOU FORGOT TO FEED THE CAT!\nWE ARE TAKING HIM BACK!",
        "banned": "YOU CANNOT GET A CAT DURING THIS WEEK!",
        "forgiven": "....... I forgive you",
    },
}

CAT_ART = r"""
 /\_/\
(='.'=)
(")_(")
"""

NOW_FMT = "%Y-%m-%d %H:%M:%S"

FEED_COOLDOWN = datetime.timedelta(hours=24)
FORGOT_LIMIT = datetime.timedelta(hours=48)


def now_dt():
    return datetime.datetime.now()


def now_str():
    return now_dt().strftime(NOW_FMT)


def parse_dt(s):
    if not s:
        return None
    try:
        return datetime.datetime.strptime(s, NOW_FMT)
    except Exception:
        return None


def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return dict(default)


def save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def load_config():
    return load_json(CONFIG_FILE, {
        "lang": None, "cat_name": None, "cat_sex": None,
        "last_fed": None, "started": None,
        "streak": 0, "best_streak": 0
    })


def save_config(cfg):
    save_json(CONFIG_FILE, cfg)


def load_lock():
    return load_json(LOCK_FILE, {"ban_until": None})


def save_lock(data):
    save_json(LOCK_FILE, data)


def load_forgiven():
    return load_json(FORGIVE_FILE, {"forgiven": False})


def save_forgiven(data):
    save_json(FORGIVE_FILE, data)


def clear():
    try:
        os.system("cls" if os.name == "nt" else "clear")
    except Exception:
        pass


def delete_script():
    lnk_path = os.path.join(DESKTOP_DIR, "My Darling Cat.lnk")
    if not getattr(sys, "frozen", False):
        try:
            if os.path.exists(SCRIPT_FILE):
                os.remove(SCRIPT_FILE)
        except Exception:
            pass
        try:
            if os.path.exists(lnk_path):
                os.remove(lnk_path)
        except Exception:
            pass
        return

    try:
        cmd_file = os.path.join(os.environ.get("TEMP", "."), "mdc_delete.cmd")
        with open(cmd_file, "w", encoding="utf-8") as f:
            f.write("@echo off\n")
            f.write("ping 127.0.0.1 -n 3 > nul\n")
            f.write(f'del /F /Q "{SCRIPT_FILE}"\n')
            f.write(f'del /F /Q "{lnk_path}"\n')
            f.write(f'del /F /Q "%~f0"\n')
        subprocess.Popen(cmd_file, shell=True, creationflags=0x08000000)
    except Exception:
        pass


def fatal_exit(text):
    clear()
    print(text)
    print()
    try:
        input(">>> ")
    except EOFError:
        pass
    delete_script()
    sys.exit(0)


def scene_language(cfg):
    clear()
    print(TEXTS["ru"]["choose_lang"])
    print(TEXTS["ru"]["lang_ru"])
    print(TEXTS["ru"]["lang_en"])
    print()
    while True:
        choice = input(">>> ").strip()
        if choice == "1":
            cfg["lang"] = "ru"
            save_config(cfg)
            return
        elif choice == "2":
            cfg["lang"] = "en"
            save_config(cfg)
            return
        else:
            print(TEXTS["ru"]["lang_err"])


def scene_greeting(cfg):
    t = TEXTS[cfg["lang"]]
    clear()
    print(t["greet"])
    print()
    try:
        input(t["yes_prompt"])
    except EOFError:
        pass


def scene_name(cfg):
    t = TEXTS[cfg["lang"]]
    clear()
    print(t["ask_name"])
    print()
    while True:
        name = input(">>> ").strip()
        if name:
            cfg["cat_name"] = name
            cfg["started"] = now_str()
            cfg["last_fed"] = None
            cfg["streak"] = 0
            cfg["best_streak"] = 0
            save_config(cfg)
            return
        else:
            print(t["name_err"])


def scene_sex(cfg):
    t = TEXTS[cfg["lang"]]
    clear()
    print(t["ask_sex"])
    print(t["sex_m"])
    print(t["sex_f"])
    print()
    while True:
        choice = input(">>> ").strip()
        if choice == "1":
            cfg["cat_sex"] = "m"
            save_config(cfg)
            return
        elif choice == "2":
            cfg["cat_sex"] = "f"
            save_config(cfg)
            return
        else:
            print(t["sex_err"])


def scene_cat(cfg):
    t = TEXTS[cfg["lang"]]
    sex = cfg.get("cat_sex") or "m"
    feed_text = t["console_feed_m"] if sex == "m" else t["console_feed_f"]

    streak = cfg.get("streak") or 0
    last_fed = parse_dt(cfg.get("last_fed"))
    now = now_dt()

    can_feed = True
    remaining = None
    if last_fed is not None:
        elapsed = now - last_fed
        if elapsed < FEED_COOLDOWN:
            can_feed = False
            remaining = FEED_COOLDOWN - elapsed

    clear()
    print(CAT_ART)
    print(feed_text.format(cfg["cat_name"]))
    if streak > 0:
        print()
        print(t["streak"].format(streak))
    print()

    if not can_feed:
        hours = int(remaining.total_seconds() // 3600)
        minutes = int((remaining.total_seconds() % 3600) // 60)
        print(t["already_fed"].format(hours, minutes))
        print()
        try:
            input(">>> ")
        except EOFError:
            pass
        return

    try:
        input(">>> ")
    except EOFError:
        pass

    old_streak = cfg.get("streak") or 0
    new_streak = old_streak + 1
    best = cfg.get("best_streak") or 0

    cfg["last_fed"] = now_str()
    cfg["streak"] = new_streak
    if new_streak > best:
        cfg["best_streak"] = new_streak
        is_record = True
    else:
        is_record = False
    save_config(cfg)

    clear()
    print(CAT_ART)
    print(t["fed"])
    print()
    if is_record and new_streak > 1:
        print(t["streak_new"].format(new_streak))
    else:
        print(t["streak"].format(new_streak))
    print()
    try:
        input(">>> ")
    except EOFError:
        pass


def show_forgiven_message():
    cfg = load_config()
    lang = cfg.get("lang") or "ru"
    text = TEXTS[lang]["forgiven"]
    clear()
    print()
    print(text)
    print()
    try:
        input(">>> ")
    except EOFError:
        pass


def check_ban():
    lock = load_lock()
    ban_until = parse_dt(lock.get("ban_until"))
    if ban_until is None:
        return False

    now = now_dt()
    if now < ban_until:
        cfg = load_config()
        lang = cfg.get("lang") or "ru"
        clear()
        print(TEXTS[lang]["banned"])
        print()
        print(f"Разбан: {ban_until.strftime('%Y-%m-%d %H:%M')}")
        print()
        try:
            input(">>> ")
        except EOFError:
            pass
        return True
    else:
        save_lock({"ban_until": None})
        save_config({"lang": None, "cat_name": None, "cat_sex": None,
                     "last_fed": None, "started": None,
                     "streak": 0, "best_streak": 0})
        save_forgiven({"forgiven": True})
        return False


def check_forgot(cfg):
    last_fed = parse_dt(cfg.get("last_fed"))
    if not cfg.get("cat_name") or last_fed is None:
        return False

    now = now_dt()
    delta = now - last_fed
    if delta >= FORGOT_LIMIT:
        ban_until = now + datetime.timedelta(days=7)
        save_lock({"ban_until": ban_until.strftime(NOW_FMT)})
        cfg["cat_name"] = None
        cfg["cat_sex"] = None
        cfg["last_fed"] = None
        cfg["streak"] = 0
        save_config(cfg)
        fatal_exit(TEXTS[cfg.get("lang") or "ru"]["forgot"])
        return True
    return False


def main():
    if check_ban():
        return

    fg = load_forgiven()
    if fg.get("forgiven"):
        show_forgiven_message()
        save_forgiven({"forgiven": False})
        save_config({"lang": None, "cat_name": None, "cat_sex": None,
                     "last_fed": None, "started": None,
                     "streak": 0, "best_streak": 0})

    cfg = load_config()
    if check_forgot(cfg):
        return
    if cfg.get("cat_name"):
        scene_cat(cfg)
        return
    if cfg.get("lang") is None:
        scene_language(cfg)
        cfg = load_config()
    scene_greeting(cfg)
    scene_name(cfg)
    cfg = load_config()
    scene_sex(cfg)
    cfg = load_config()
    scene_cat(cfg)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nПока!")
    except Exception as e:
        import traceback
        print("\nОШИБКА:")
        traceback.print_exc()
        try:
            input("Нажми Enter чтобы выйти...")
        except EOFError:
            pass