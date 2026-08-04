import pandas as pd
import smtplib, ssl, time, random, os, csv, imaplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from dotenv import load_dotenv

load_dotenv()

contacts_file = "contacts.xlsx"
subjects_file = "subject_lines.txt"
log_file = "sent_log.csv"

sender_email = os.getenv("EMAIL")
password = os.getenv("EMAIL_PASSWORD")

smtp_server = "mail.spacemail.com"
smtp_port = 465

imap_server = "mail.spacemail.com"
imap_port = 993

df = pd.read_excel(contacts_file)

with open(subjects_file, "r", encoding="utf-8") as f:
    subject_lines = [line.strip() for line in f if line.strip()]

sent_emails = set()
if os.path.exists(log_file):
    with open(log_file, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if row:
                sent_emails.add(row[0])

context = ssl.create_default_context()

smtp = smtplib.SMTP_SSL(smtp_server, smtp_port, context=context)
smtp.login(sender_email, password)

imap = imaplib.IMAP4_SSL(imap_server, imap_port)
imap.login(sender_email, password)

status, mailboxes = imap.list()

print("Folders:")
for mailbox in mailboxes:
    print(mailbox.decode())

sent_folder = "Sent"

sent_count = 0

try:
    for _, row in df.iterrows():
        name = row["Name"]
        title = row["Job title"]
        company = row["Company"]
        recipient_email = 'tiwarisahil14@gmail.com'

        if recipient_email in sent_emails:
            continue

        subject = random.choice(subject_lines).replace("{name}", name).replace("{Company}", company)

        text_body = f"""Hi {name},

Noticed {company} has been growing recently, so I figured I'd reach out.

Most {title}s I talk to are running 4–6 different tools between finding a lead and sending the email.

Apollo → Export → Enrich → CRM → Sequencer.

Someone on the team usually ends up being the glue between all of them.

We're building Scout to remove that completely.

One workspace where AI agents handle research, enrichment and outreach while carrying context through every step, while you only approve the decisions that matter.

Would you be open to a quick 15-minute chat?

Or simply reply "send it" and I'll send over a 60-second demo.

Cheers,

Darshan
https://runscout.app
"""

        html_body = f"""<!DOCTYPE html>
<html><body style="font-family:Arial,Helvetica,sans-serif;font-size:15px;color:#222;line-height:1.6;">
<p>Hi {name},</p>
<p>Noticed <b>{company}</b> has been growing recently, so I figured I'd reach out.</p>
<p>Most <b>{title}</b>s I talk to are running 4–6 different tools between finding a lead and sending the email.</p>
<p>Apollo → Export → Enrich → CRM → Sequencer.</p>
<p>Someone on the team usually ends up being the glue between all of them.</p>
<p>We're building <b>Scout</b> to remove that completely.</p>
<p>One workspace where AI agents handle research, enrichment and outreach while carrying context through every step, while you only approve the decisions that matter.</p>
<p>Would you be open to a quick 15-minute chat?</p>
<p>Or just reply with <b>"send it"</b> and I'll send over a 60-second demo.</p>
<p>Cheers,<br><br><b>Darshan</b><br><a href="https://runscout.app">runscout.app</a></p>
</body></html>"""

        msg = MIMEMultipart("alternative")
        msg["From"] = formataddr(("Darshan", sender_email))
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(text_body, "plain", "utf-8"))
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        try:
            raw_message = msg.as_string()

            smtp.sendmail(
                sender_email,
                recipient_email,
                raw_message
            )
            print(f"✅ Sent to {recipient_email}")

            result = imap.append(
                "Sent",
                None,
                imaplib.Time2Internaldate(time.time()),
                msg.as_bytes()
            )

            print("Append Result:", result)

            # Append to log
            with open(log_file, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if os.stat(log_file).st_size == 0:
                    writer.writerow(["Email", "Subject", "Timestamp"])
                writer.writerow([recipient_email, subject, datetime.now().isoformat()])

            sent_count += 1

        except Exception as e:
            print(f"Failed for {recipient_email}: {e}")

        if sent_count >= 100:
            break

        time.sleep(random.randint(45, 120))

finally:
    smtp.quit()
    imap.logout()
