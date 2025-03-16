"""Automatic OTP script for Deepmail"""
import sys
import time
import os
from configparser import ConfigParser
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome import service as fs
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from myimap import get_otp_key

parser = argparse.ArgumentParser(
    description='Deepmail Email 2 factor authentication')
parser.add_argument('-i', '--inifile', default="config.ini",
                    help='specify ini file')
parser.add_argument("--headless", action='store_true',
                    help='do not show chrome window')
parser.add_argument('-v', "--verbose", action='store_true',
                    help='verbose mode')
parser.add_argument('-vv', "--moreverbose", action='store_true',
                    help='strong verbose mode')

args = parser.parse_args()
config = ConfigParser()
config.read(os.path.dirname(os.path.abspath(__file__))+'/' + args.inifile)

conf_email = config.get("email", "email")
webmail_url = config.get("email", "webmail_url")
login_id = config.get("email", "login")
login_pass = config.get("email", "password")
exmail_imapserver = config.get("ext_email", "imapserver")
exmail_login_id = config.get("ext_email", "login")
exmail_login_pass = config.get("ext_email", "password")

options = webdriver.ChromeOptions()
options.add_experimental_option("prefs", {
    "download.default_directory": "./",
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "plugins.plugins_disabled": ["Chrome PDF Viewer"],
    "plugins.always_open_pdf_externally": True
})
options.add_argument("--disable-extensions")
options.add_argument("--disable-print-preview")
options.add_argument("--no-sandbox")
if args.headless is True:
    options.add_argument('--headless')

def pinfo(message):
    """デバッグ用表示関数"""
    if args.verbose:
        print("[Info] " + message)

def perr(message,err):
    """エラー用表示関数"""
    print("[Error] " + message)
    if args.moreverbose:
        print(err)

pinfo("Chromeを起動します．")
# ChromeのWebDriverオブジェクトを作成する。
try:
    chrome_service = fs.Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=chrome_service, options=options)
    wait = WebDriverWait(driver=driver, timeout=10)
except Exception as e:
    perr("Chromeが起動しません。",e)
    sys.exit()

pinfo("WebMailにログインします．")
# open web
try:
    driver.get(webmail_url)  # 該当ページを開く → シボレスへ飛ぶ
    wait.until(EC.presence_of_all_elements_located)
    driver.find_element(By.LINK_TEXT, "Webメールシステムへログイン").click()
    wait.until(EC.presence_of_all_elements_located)
    driver.find_element(By.ID, "username").send_keys(login_id)   # ユーザ名
    driver.find_element(By.ID, "password").send_keys(login_pass)  # パスワード
    driver.find_element(By.NAME, "_eventId_proceed").click()    # 進む
except Exception as e:
    perr("シボレスログインできません。",e)
    driver.quit()  # ブラウザーを終了する。
    sys.exit()

pinfo("OTP発行をリクエストします．")
# deepmail
try:
    wait.until(EC.presence_of_element_located((By.ID, "SelOutmail")))
    driver.find_element(By.ID, "SelOutmail").click()   # 外部メール認証
    time.sleep(1) # 1秒待った方が確実
    wait.until(EC.presence_of_element_located((By.ID, "BtnIssueAuthKey")))
    driver.find_element(By.ID, "BtnIssueAuthKey").click() # OTP発行
except Exception as e:
    perr("OTP発行できません。おそらく、既に多要素認証されています。",e)
    driver.quit()  # ブラウザーを終了する。
    sys.exit()

otp_key = ""
count = 0
while otp_key == "" and count < 6:
    pinfo(f"メール取得試行{count + 1}回目…")
    time.sleep(5)
    otp_key = get_otp_key(exmail_imapserver,exmail_login_id,
                            exmail_login_pass,conf_email)
    count += 1

if otp_key == "":
    perr("EmailからOTPを取得できません。メールが届いていないと思われます。","")
    driver.quit()  # ブラウザーを終了する。
    sys.exit()

pinfo(f"OTP key{otp_key}を入力します．")

try:
    wait.until(EC.presence_of_all_elements_located)
    driver.find_element(By.ID, "authkey").send_keys(otp_key)   # 認証コード
    driver.find_element(By.ID, "login").click()   # ログイン
    wait.until(EC.presence_of_all_elements_located)
except Exception as e:
    perr("OTP入力できません。",e)
    driver.quit()  # ブラウザーを終了する。
    sys.exit()

driver.quit()  # ブラウザーを終了する。
print("OTPを取得して入力しました．")
