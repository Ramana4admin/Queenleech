from logging import FileHandler, StreamHandler, INFO, basicConfig, error as log_error, info as log_info
from os import path as ospath, environ, remove
from subprocess import run as srun, call as scall
from requests import get as rget
from dotenv import load_dotenv, dotenv_values
from pymongo import MongoClient

# ---------------- LOG CLEAN ---------------- #
if ospath.exists('log.txt'):
    with open('log.txt', 'r+') as f:
        f.truncate(0)

if ospath.exists('rlog.txt'):
    remove('rlog.txt')

basicConfig(
    format="[%(asctime)s] [%(levelname)s] - %(message)s",
    datefmt="%d-%b-%y %I:%M:%S %p",
    handlers=[FileHandler('log.txt'), StreamHandler()],
    level=INFO
)

# ---------------- LOAD ENV ---------------- #
load_dotenv('config.env', override=True)

# ---------------- SAFETY CHECK ---------------- #
try:
    if bool(environ.get('_____REMOVE_THIS_LINE_____')):
        log_error('Read README.md properly! Exiting.')
        exit()
except:
    pass

# ---------------- BOT TOKEN ---------------- #
BOT_TOKEN = environ.get('BOT_TOKEN', '')
if not BOT_TOKEN:
    log_error("BOT_TOKEN missing! Exiting.")
    exit(1)

bot_id = BOT_TOKEN.split(':', 1)[0]

# ---------------- DATABASE ---------------- #
DATABASE_URL = environ.get('DATABASE_URL')
if DATABASE_URL:
    conn = MongoClient(DATABASE_URL)
    db = conn.kpsmlx

    old_config = db.settings.deployConfig.find_one({'_id': bot_id})
    config_dict = db.settings.config.find_one({'_id': bot_id})

    if old_config:
        del old_config['_id']

    if (
        (old_config == dict(dotenv_values('config.env')) or old_config is None)
        and config_dict
    ):
        environ['UPSTREAM_REPO'] = config_dict.get('UPSTREAM_REPO')
        environ['UPSTREAM_BRANCH'] = config_dict.get('UPSTREAM_BRANCH')
        environ['UPGRADE_PACKAGES'] = config_dict.get('UPDATE_PACKAGES', 'False')

    conn.close()

# ---------------- PACKAGE INSTALL (FIXED) ---------------- #
UPGRADE_PACKAGES = environ.get('UPGRADE_PACKAGES', 'False')

if UPGRADE_PACKAGES.lower() == 'true':
    log_info("Installing required packages (SAFE MODE)...")
    scall(
        "pip install --no-cache-dir "
        "pyrogram==2.0.106 "
        "tgcrypto "
        "python-dotenv "
        "yt-dlp==2023.10.07 "
        "pyrofork==2.2.11",
        shell=True
    )

# ---------------- UPSTREAM ---------------- #
UPSTREAM_REPO = environ.get('UPSTREAM_REPO') or "https://github.com/Tamilupdates/KPSML-X"
UPSTREAM_BRANCH = environ.get('UPSTREAM_BRANCH') or "kpsmlx"

# ---------------- GIT UPDATE ---------------- #
if UPSTREAM_REPO:
    if ospath.exists('.git'):
        srun(["rm", "-rf", ".git"])

    update = srun(
        f"""
        git init -q &&
        git config --global user.email kpstorrent@gmail.com &&
        git config --global user.name kpsbots &&
        git add . &&
        git commit -sm update -q &&
        git remote add origin {UPSTREAM_REPO} &&
        git fetch origin -q &&
        git reset --hard origin/{UPSTREAM_BRANCH} -q
        """,
        shell=True
    )

    repo = UPSTREAM_REPO.split('/')
    UPSTREAM_REPO = f"https://github.com/{repo[-2]}/{repo[-1]}"

    if update.returncode == 0:
        log_info("Successfully updated with latest commits ✅")
    else:
        log_error("Update failed! Check repo / branch.")

    log_info(f"UPSTREAM_REPO: {UPSTREAM_REPO} | UPSTREAM_BRANCH: {UPSTREAM_BRANCH}")
