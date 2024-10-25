# 工繊Email用 二要素認証 スクリプト
# Two factor authentication for KIT e-mail system

工繊Emailの二要素認証を1コマンドで実行するPythonスクリプトです．
外部メール認証を使いますので，DEEP Mail上でメール認証を有効にしておいてください．

# インストール

```
$ pipenv install
```
Google Chromeをインストールしておく．

# 設定

config.ini.sampleをconfig.iniにコピーして記入する．

[kit]セクションには，本学のemail関連の情報を記入する．
[ext_email]セクションには，外部メールサービスの情報を記入する．
(外部メールではapp passwordを発行するところが多いので，それを記入)
login, passwordを生で書くので管理には気をつけて．

```config.ini
[kit]
webmail_url= https://webmail.cis.kit.ac.jp
email      = hoge@kit.ac.jp
login      = hoge
password   = somedifficultpassword

[ext_email]
imapserver = imap server of your external email service
imapport   = 993
login      = your login ID of your external email service
password   = your login password of your external email service
```

# 実行

```
$ pipenv run login
```

Chromeが開き，Webメールにログインして，OTP入力待ちになる．
スクリプトは外部メールサーバーに接続し，OTPが送信されてくるのを待つ．
実行から3分以内に所定の形式で書かれたメールが届いたら，
そこに書かれたOTPを取得し，自動で入力を終えてChromeを終了する．

以後14時間，実行した計算機からimapサーバにアクセスできます．

```
usage: autootp.py [-h] [-i INIFILE] [--headless]

KIT Email 2 factor authentication

optional arguments:
  -h, --help            show this help message and exit
  -i INIFILE, --inifile INIFILE
                        specify ini file
  --headless            do not show chrome window
```