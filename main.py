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

smtp_server = "smtp.gmail.com"
port = 587

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

with smtplib.SMTP(smtp_server, port) as server:
    server.starttls(context=context)
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

I recently applied to some Software Engineer roles at {company} and wanted to reach out because I am genuinely interested in joining the team. My background is in backend development and automation, currently at Accenture, and previously as a founding engineer building RabbitMQ-based async workflows and AWS services to improve operational efficiency and production reliability.

The role seems very aligned with the kind of work I enjoy doing, so I’d love to be considered if my profile looks relevant. Would you be open to meeting up? I can, of course, work around your schedule.

Thanks for your time.

Best regards,  
Sahil Tiwari  
LinkedIn: {linkedin} 
Resume: {resume_link}
"""

        # HTML body
        html_body = f"""
<html>
  <body>
    <p>Hi {name},</p>

    <p>I recently applied to the Software Engineer role at {company} and wanted to reach out because I am genuinely interested in joining the team. <br/><br/>My background is in backend development and automation, currently at Accenture, and previously as a founding engineer building RabbitMQ-based async workflows and AWS services to improve operational efficiency and production reliability.<br/><br/>

The role feels strongly aligned with the kind of work I enjoy doing, so I’d really appreciate being considered if my profile looks relevant. Happy to share more details if helpful.

<br/><br/>Thanks for your time.</p>

    <p style="color:#000000; margin:0;">
Regards,<br/>
Sahil Tiwari<br/>
LinkedIn: <a href="https://www.linkedin.com/in/sahilt02" target="_blank">https://www.linkedin.com/in/sahilt02</a><br/>
Resume: <a href="https://drive.google.com/file/d/1t1_dPyJhAqNL0vvda9lzzcyqUYXjIIl2/view?usp=sharing" target="_blank">
https://drive.google.com/file/d/1t1_dPyJhAqNL0vvda9lzzcyqUYXjIIl2/view?usp=sharing
</a>
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
        time.sleep(random.randint(30, 60))