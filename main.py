import pandas as pd
import smtplib, ssl, time, random, os, csv
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from dotenv import load_dotenv
load_dotenv()

# === Config ===
contacts_file = "contacts.xlsx"
subjects_file = "subject_lines.txt"
log_file = "sent_log.csv"
resume_link = "https://drive.google.com/file/d/1t1_dPyJhAqNL0vvda9lzzcyqUYXjIIl2/view?usp=sharing"
linkedin = "https://www.linkedin.com/in/sahilt02"
github = "https://www.github.com/soulsahil"
sender_email = os.getenv("EMAIL")
password = os.getenv("EMAIL_PASSWORD")


smtp_server = "my.space.email"
port = 465

# === Load data ===
df = pd.read_excel(contacts_file)
with open(subjects_file, "r") as f:
    subject_lines = [line.strip() for line in f if line.strip()]

# Load already sent emails
sent_emails = set()
if os.path.exists(log_file):
    with open(log_file, "r") as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header
        for row in reader:
            if row:
                sent_emails.add(row[0])  # email is first column

context = ssl.create_default_context()

with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    server.login(sender_email, password)

    sent_count = 0
    for index, row in df.iterrows():
        name = row['Name']
        recipient_email = row['Email']
        company = row['Company']

        # Skip if already sent
        if recipient_email in sent_emails:
            continue

        # Pick random subject
        subject = random.choice(subject_lines).replace("{name}", name).replace("{Company}", company)

        # Plain text body
        text_body = f"""
Hi {name},

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

        # HTML body
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
</head>

<body style="font-family:Arial,Helvetica,sans-serif;font-size:15px;color:#222;line-height:1.6;">

<p>Hi {name},</p>

<p>
Most <b>{title}</b>s I talk to are running 4–6 different tools between finding a lead and sending the email.
</p>

<p>
Apollo → Export → Enrich → CRM → Sequencer.
</p>

<p>
And someone on the team usually ends up being the glue between all of them.
</p>

<p>
We're building <b>Scout</b> to remove that completely.
</p>

<p>
One workspace where a team of AI agents handles research, enrichment and outreach while carrying context through every step, while you only approve the decisions that matter.
</p>

<p>
Would you be open to a quick 15-minute chat?
</p>

<p>
Or just reply with <b>"send it"</b> and I'll send over a 60-second demo.
</p>

<p>
Cheers,<br><br>

<b>Darshan</b><br>

<a href="https://runscout.app">runscout.app</a>

</p>

</body>
</html>
"""

        msg = MIMEMultipart("alternative")
        msg["From"] = formataddr(("Sahil Tiwari", sender_email))
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        try:
            server.sendmail(sender_email, recipient_email, msg.as_string())
            print(f"✅ Sent to {recipient_email} with subject: {subject}")

            # Append to log
            with open(log_file, "a", newline="") as f:
                writer = csv.writer(f)
                if os.stat(log_file).st_size == 0:
                    writer.writerow(["Email", "Subject", "Timestamp"])
                writer.writerow([recipient_email, subject, datetime.now().isoformat()])

            sent_count += 1
        except Exception as e:
            print(f"❌ Failed for {recipient_email}: {e}")

        # limit to 100 per run
        if sent_count >= 100:
            break

        # wait before next email
        delay = random.randint(45, 120)
        time.sleep(delay)