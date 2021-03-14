import datetime
import os
from mailer import Email
from mailing_list import MailingList
import schedule
from lms import LMS
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from json_handler import load_data
from apscheduler.schedulers.blocking import BlockingScheduler
import time

def generate_email_body(lms:LMS, email_sender:str, email_receiver:str, course_name):
    try:
        body_message = html_body = ''
        message = MIMEMultipart("alternative")
        message["Subject"] = f'{course_name} Baru Saja Memposting Tugas Baru'
        message["From"] = email_sender
        message["To"] = email_receiver

        body = lms.course_updated(course_name)
        data = load_data(f'Course Data/XII RPL A/{course_name}.json')
        for body_ in body.split("\n"):
            body__ = body_.replace('[', '').replace(']', '').replace(" '", '').replace("'", '')
            body_message += f'\n{body__}'
            try:
                title = [d['Title'] for d_ in data[0]['Activity'] for d in d_['Activity List'] if d['Link'] and body__ in d['Link']]
            except Exception as e:
                title = '#'

            html_body += f'<li><a href="{body__}">{title}</a></li>'
        html = f"""
            <html>
            <body>
                <ul>
                    {html_body}
                </ul>
            </body>
            </html>
        """            
        part1 = MIMEText(body_message, "plain")
        part2 = MIMEText(html, "html")
        message.attach(part1)
        message.attach(part2)
        return message
    except Exception as e:
        return None

def check_if_update(lms:LMS, email:Email, ml:MailingList, course:str, day:str):
    if lms.course_updated(course):
        for receiver in ml.get_list():
            message = generate_email_body(lms, email.get_user(), receiver, course)
            email.server.sendmail(email.get_user(), receiver, message.as_string())
    else:
        print(f'{day} pukul {datetime.datetime.now().hour} {course} belum ada update')

if __name__ == "__main__":
    print('BOT STARTING\n')

    email = Email('pirus.apl@gmail.com', 'pirus123')
    lms = LMS('181113847', 'PRSYETI1')
    ml = MailingList()
    login_email = False

    while not login_email:
        if email.login():
            login_email = True
            print(f'Email login succes, logged in as {email.get_user()}\n')
        else:
            print('Email login failed, retrying...\n')

    if not os.path.isfile('Course Data/XII RPL A/Course List.json'):
        lms.get_course()

    sched = BlockingScheduler()
    sched.add_job(lambda:check_if_update(lms, email, ml, 'PPKn XII (Tintin Sutrisni)', 'Selasa'), 'cron', day_of_week='tue', hour='0-15')
    sched.add_job(lambda:check_if_update(lms, email, ml, 'Produk Kreatif Kewirausahaan XII (Sopiah)', 'Selasa'), 'cron', day_of_week='tue', hour='0-15')
    sched.add_job(lambda:check_if_update(lms, email, ml, 'Bahasa Indonesia XII (Dra. Hj. Sri Gantini, M.Pd)', 'Selasa'), 'cron', day_of_week='tue', hour='0-15')
    sched.add_job(lambda:check_if_update(lms, email, ml, 'Bahasa Inggris XII (Nurhayati Hutabarat, S.Pd)', 'Rabu'), 'cron', day_of_week='wed', hour='0-15')
    sched.add_job(lambda:check_if_update(lms, email, ml, 'Bahasa Jepang XII (Rukti Ananditya Karunia Sari, S.Pd.)', 'Jumat'), 'cron', day_of_week='fri', hour='0-15')
    sched.add_job(lambda:check_if_update(lms, email, ml, 'PABP XII (LUKMAN)', 'Jumat'), 'cron', day_of_week='fri', hour='0-15')
    sched.start()