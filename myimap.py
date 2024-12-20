"""Automatic OTP script"""
import datetime
import re
import locale
import imaplib
import email
from email.header import decode_header, make_header
from dateutil import parser as dp

def get_otp_key(exmail_imapserver,exmail_login_id, exmail_login_pass, kit_email):
    """Get OTP key from ipecified imap server"""
    locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')

    imapbody = str("(RFC822)")
    # iCloudはRFC822を指定してもBODYが取れない．
    if re.search(r"\.me\.com$",exmail_imapserver):
        imapbody = str("(BODY[])")

#    print(imapbody)

    imap = imaplib.IMAP4_SSL(exmail_imapserver)
    imap.login(exmail_login_id, exmail_login_pass)

    # Select folder named Google
    imap.select('Inbox')

    typ, data = imap.search(None, 'ALL')

    d = data[0].split()
    fetch_num = 5  # 取得したいメッセージの数
    if (len(d)-fetch_num) < 0:
        fetch_num = len(d)
    msg_list = []
    for num in d[len(d)-fetch_num::]:
        typ, data1 = imap.fetch(num, imapbody)
        try:
            msg = email.message_from_bytes(data1[0][1])
            msg_list.append(msg)
        except AttributeError:
            pass
    imap.close()
    imap.logout()

    dnow = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=9)))

    otp_key = ""

    for msg in reversed(msg_list):
        from_addr = str(make_header(decode_header(msg["From"])))
        subject = str(make_header(decode_header(msg["Subject"])))
        mail_date = str(make_header(decode_header(msg["Date"])))
        dmail = dp.parse(mail_date)
    #    print((dnow - dmail).seconds)
        if (dnow - dmail).seconds < 180 and \
                re.search(f"{kit_email}",from_addr) and \
                re.search("OTP",subject):
    #        print(from_addr)
    #        print(mail_date)
    #        print(subject)
            if msg.is_multipart() is False:
                payload = msg.get_payload(decode=True)
                charset = msg.get_content_charset()
                if charset is not None:
                    payload = payload.decode(charset, "ignore")
    #            print(payload)
    #            print()
                s = re.search(r": \d\d\d\d\d\d",payload)
                otp_key = s.group()[2:]
            else:
                for part in msg.walk():
                    payload = part.get_payload(decode=True)
                    if payload is None:
                        continue
                    charset = part.get_content_charset()
                    if charset is not None:
                        payload = payload.decode(charset, "ignore")
    #                print(payload)
    #                print()
                    s = re.search(r": \d\d\d\d\d\d",payload)
                    otp_key = s.group()[2:]
            if otp_key != "":
                break
    # print(otpKey)
    return otp_key
