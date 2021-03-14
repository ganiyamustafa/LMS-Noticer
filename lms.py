import json
import smtplib, ssl
import mechanicalsoup
import numpy as np
import schedule
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from threading import Thread
    # Uncomment to launch a real web browser on the current page.
    # browser.launch_browser()

    # Uncomment to display a summary of the filled-in form
    # browser.get_current_form().print_summary()
server = smtplib.SMTP(host='smtp.gmail.com', port=587)
server.ehlo()
server.starttls()
smtp_server = "smtp.gmail.com"
port = 587  # For starttls
sender_email = "pirus.apl@gmail.com"
password = "pirus123"

# Create a secure SSL context
context = ssl.create_default_context()

# Try to log in to server and send email

class lms():
    base_url = "https://lms.smkn1-cmi.sch.id/"
    login_status = False
    browser = mechanicalsoup.StatefulBrowser()
    browser.open(base_url)

    def save_data(self, title, data):
        with open(title, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_data(self, title):
        with open(title, encoding='utf-8') as f:
            return json.load(f)

    def page(self):
        return self.browser.get_current_page()

    def login(self, username, password):
        if not self.login_status:
            self.browser.follow_link("login/index.php")
            self.browser.select_form('form[id="login"]')
            self.browser["username"] = username
            self.browser["password"] = password
            response = self.browser.submit_selected()
            self.login_status = True

    def get_course(self):
        self.login('181113833', 'MQJENVO1')
        courses_list = []
        self.browser.open(f"{self.base_url}/my/index.php?mynumber=-2")
        for course in self.page().select('.course_list .coursebox .course_title h2'):
            courses = {}
            courses['Title'] = course.text
            courses['Link'] = course.a['href']
            courses_list.append(courses)
            print('get_course_succes')
        self.save_data('XII-RPL-A course.json', courses_list)
        # print(courses_list)
        return courses_list
    
    def get_assignment_data(self, link, title):
        global activity_list, assignments_list, data_list, data
        self.browser.open(link)
        for assignment_li in self.page().select('li.section.main.clearfix'):
            activity = {}
            assignments_list = []
            if 'General' not in assignment_li['aria-label']:
                activity['Header'] = assignment_li['aria-label']
                for assignment in assignment_li.select('div.content li.activity'):
                    assignments = {}
                    if 'label' not in assignment['class']:
                        if 'assign' in assignment['class']: assignments['Type'] = 'submission/assign'
                        if assignment.find('span', class_='accesshide'): assignment.find('span', class_='accesshide').extract()
                        if assignment.find('span', class_='instancename'): assignments['Title'] = assignment.find('span', class_='instancename').text
                        if assignment.a: assignments['Link'] = assignment.a['href']
                        else: assignments['Link'] = None
                        assignments_list.append(assignments)
                activity['Activity List'] = assignments_list
                print(activity['Header'])
                activity_list.append(activity)
            print('get_assignment_succes')
        data['Course'] = title
        data['Activity'] = activity_list
        data_list.append(data)

    def get_assignment(self, courses: list, course_name: str=''):
        global activity_list, assignments_list, data_list, data
        data_list = []
        threads = []
        for course in courses:
            data = {}
            activity_list = []
            assignments_list = []

            if course_name in course['Title']:
                t = Thread(target=self.get_assignment_data, args=(course['Link'],course['Title']))
                threads.append(t)

        for t in threads:
            print('start threading')
            t.start()

        for t in threads:
            print('join threading')
            t.join()

        print(len(data_list))
        print(data_list[0]['Activity'][0]['Header'])
        return data_list

    def get_assign_detail_data(self, activity):
        detail = {}
        try: 
            if activity['Type']: 
                self.browser.open(activity['Link'])
                rows = self.page().find('table', class_='generaltable').find('tbody').select('tr')
                for row in rows:
                    if 'comments' not in row.find('td', class_='cell c0').text:
                        detail[row.find('td', class_='cell c0').text] = row.find('td', class_='c1').text
                activity['detail'] = detail
                print('get_assign_detail_succes')
        except Exception as e: print(e)

    def get_assign_detail(self, course_name: str='', data: list = []):
        threads = []
        for course in data:
            for activity_list in course['Activity']:
                for activity in activity_list['Activity List']:
                    print('append threading')
                    t = Thread(target=self.get_assign_detail_data, args=(activity,))
                    threads.append(t)

        for t in threads:
            print('start threading')
            t.start()

        for t in threads:
            print('join threading')
            t.join()


        return data

    def check_data(self, course_name):
        self.login('181113847', 'PRSYETI1')
        data_, old_data_ = [], []
        data = self.get_assignment(self.load_data('XII-RPL-A course.json'), course_name)
        old_data = self.load_data(f'{course_name}.json')
        old_data_ = [d['Link'] for od in old_data[0]['Activity'] for d in od['Activity List'] if d['Link']]
        data_ = [d['Link'] for d_ in data[0]['Activity'] for d in d_['Activity List'] if d['Link']]
        self.save_data(f'{course_name}.json', data)
        return np.setdiff1d(data_, old_data_) if not data_ == old_data_ else 'not update'

    def login_email(self):
        global server
        server = smtplib.SMTP(smtp_server,port)
        server.ehlo() # Can be omitted
        server.starttls(context=context) # Secure the connection
        server.ehlo() # Can be omitted
        server.login(sender_email, password)

    def send_email(self, subjek, course_name):
        try:
            body_message = html_body = ''
            receiver = ['shaddam.a.h@gmail.com', 
                        'aldyardiansyah628@gmail.com', 
                        'rifkierlangga17@gmail.com', 
                        'dafanurulfauziansyah97@gmail.com', 
                        'shdqillham123@gmail.com', 
                        'jjulianto08@gmail.com', 
                        'munawarhariz@gmail.com', 
                        'ariabagaswara23@gmail.com', 
                        'ganiyamustaga32@gmail.com']
            message = MIMEMultipart("alternative")
            message["Subject"] = subjek
            message["From"] = sender_email
            message["To"] = 'shaddam.a.h@gmail.com, aldyardiansyah628@gmail.com, rifkierlangga17@gmail.com, dafanurulfauziansyah97@gmail.com, shdqillham123@gmail.com, jjulianto08@gmail.com, munawarhariz@gmail.com, ariabagaswara23@gmail.com, ganiyamustaga32@gmail.com'
            self.login_email()
            body = f"{self.check_data(course_name)}"
            # send message
            data = self.load_data(f'{course_name}.json')
            for body_ in body.split("\n"):
                body__ = body_.replace('[', '').replace(']', '').replace(" '", '').replace("'", '')
                body_message += f'\n{body__}'
                try:
                    title = [d['Title'] for d_ in data[0]['Activity'] for d in d_['Activity List'] if d['Link'] and body__ in d['Link']]
                except Exception as e:
                    title = '#'
                    print(e)
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

            # Add HTML/plain-text parts to MIMEMultipart message
            # The email client will try to render the last part first
            message.attach(part1)
            message.attach(part2)
            # ', , rifkierlangga17@gmail.com, dafanurulfauziansyah97@gmail.com, , , , ariabagaswara23@gmail.com'
            for r in receiver: server.sendmail(sender_email, r, message.as_string())
            # server.sendmail(sender_email, 'ganiyamustaga32@gmail.com', message.as_string())
        except Exception as e:
            # Print any error messages to stdout
            print(e)
        finally:
            server.quit()

    def check_indonesia_updated(self):
        self.send_email('Indonesia Course Update', 'Bahasa Indonesia XII (Dra. Hj. Sri Gantini, M.Pd)')

    def check_inggris_updated(self):
        self.send_email('Inggris Course Update', 'Bahasa Inggris XII (Nurhayati Hutabarat, S.Pd)')

    def check_pkn_updated(self):
        self.send_email('PKN Course Update', 'PPKn XII (Tintin Sutrisni)')
    
    def check_pkk_updated(self):
        self.send_email('PKK Shopee Course Update', 'Produk Kreatif Kewirausahaan XII (Sopiah)')

    def check_jepang_updated(self):
        self.send_email('Jepang Course Update', 'Bahasa Jepang XII (Rukti Ananditya Karunia Sari, S.Pd.)')
    
    def check_pabp_updated(self):
        self.send_email('PABP Course Update', 'PABP XII (LUKMAN)')

    def get_PKN_assignment(self, assign_detail: bool=False):
        self.login('181113847', 'PRSYETI1')
        self.save_data('PPKn XII (Tintin Sutrisni).json', self.get_assignment(self.load_data('XII-RPL-A course.json'), 'PPKn XII (Tintin Sutrisni)'))
        if assign_detail: self.save_data('PPKn XII (Tintin Sutrisni).json', self.get_assign_detail(data=self.load_data('PPKn XII (Tintin Sutrisni).json')))
        return self.load_data('PPKn XII (Tintin Sutrisni).json')

    def get_PKK_assignment(self, assign_detail: bool=False):
        self.login('181113847', 'PRSYETI1')
        self.save_data('Produk Kreatif Kewirausahaan XII (Sopiah).json', self.get_assignment(self.load_data('XII-RPL-A course.json'), 'Produk Kreatif Kewirausahaan XII (Sopiah)'))
        if assign_detail: self.save_data('Produk Kreatif Kewirausahaan XII (Sopiah).json', self.get_assign_detail(data=self.load_data('Produk Kreatif Kewirausahaan XII (Sopiah).json')))
        return self.load_data('Produk Kreatif Kewirausahaan XII (Sopiah).json')

    def get_Indonesia_assignment(self, assign_detail: bool=False):
        self.login('181113847', 'PRSYETI1')
        self.save_data('Bahasa Indonesia XII (Dra. Hj. Sri Gantini, M.Pd).json', self.get_assignment(self.load_data('XII-RPL-A course.json'), 'Bahasa Indonesia XII (Dra. Hj. Sri Gantini, M.Pd)'))
        if assign_detail: self.save_data('Bahasa Indonesia XII (Dra. Hj. Sri Gantini, M.Pd).json', self.get_assign_detail(data=self.load_data('Bahasa Indonesia XII (Dra. Hj. Sri Gantini, M.Pd).json')))
        return self.load_data('Bahasa Indonesia XII (Dra. Hj. Sri Gantini, M.Pd).json')

    def get_Inggris_assignment(self, assign_detail: bool=False):
        self.login('181113847', 'PRSYETI1')
        self.save_data('Bahasa Inggris XII (Nurhayati Hutabarat, S.Pd).json', self.get_assignment(self.load_data('XII-RPL-A course.json'), 'Bahasa Inggris XII (Nurhayati Hutabarat, S.Pd)'))
        if assign_detail: self.save_data('Bahasa Inggris XII (Nurhayati Hutabarat, S.Pd).json', self.get_assign_detail(data=self.load_data('Bahasa Inggris XII (Nurhayati Hutabarat, S.Pd).json')))
        return self.load_data('Bahasa Inggris XII (Nurhayati Hutabarat, S.Pd).json')

    def get_Jepang_assignment(self, assign_detail: bool=False):
        self.login('181113847', 'PRSYETI1')
        self.save_data('Bahasa Jepang XII (Rukti Ananditya Karunia Sari, S.Pd.).json', self.get_assignment(self.load_data('XII-RPL-A course.json'), 'Bahasa Jepang XII (Rukti Ananditya Karunia Sari, S.Pd.)'))
        if assign_detail: self.save_data('Bahasa Jepang XII (Rukti Ananditya Karunia Sari, S.Pd.).json', self.get_assign_detail(data=self.load_data('Bahasa Jepang XII (Rukti Ananditya Karunia Sari, S.Pd.).json')))
        return self.load_data('Bahasa Jepang XII (Rukti Ananditya Karunia Sari, S.Pd.).json')
    
    def get_pabp_assignment(self, assign_detail: bool=False):
        self.login('181113847', 'PRSYETI1')
        self.save_data('PABP XII (LUKMAN).json', self.get_assignment(self.load_data('XII-RPL-A course.json'), 'PABP XII (LUKMAN)'))
        if assign_detail: self.save_data('PABP XII (LUKMAN).json', self.get_assign_detail(data=self.load_data('PABP XII (LUKMAN).json')))
        return self.load_data('PABP XII (LUKMAN).json')

    def get_course_data(self, course_name: str=''):
        print('loading')
        return self.get_assign_detail(course_name=course_name)
        print('success')

Lms = lms()

# def job():
#     print('job')

# save_data('lms.json', Lms.get_course_data())
print('Start...')
# run first
Lms.get_course()

#run second
Lms.get_Indonesia_assignment()
Lms.get_Inggris_assignment()
Lms.get_Jepang_assignment()
Lms.get_PKN_assignment()
Lms.get_pabp_assignment()
Lms.get_PKK_assignment()
# schedule.every(3).minutes.do(job)
schedule.every().tuesday.at("08:00").do(Lms.check_indonesia_updated)
schedule.every().tuesday.at("08:30").do(Lms.check_pkn_updated)
schedule.every().tuesday.at("09:30").do(Lms.check_pkk_updated)
schedule.every().wednesday.at("11:00").do(Lms.check_inggris_updated)
schedule.every().friday.at("08:00").do(Lms.check_jepang_updated)
schedule.every().friday.at("08:30").do(Lms.check_pabp_updated)

while True:
    schedule.run_pending()
    time.sleep(1)

# cek update
# Lms.check_jepang_updated()
# Lms.check_inggris_updated()
# Lms.check_indonesia_updated()
# Lms.check_pkn_updated()
# print(np.setdiff1d(n2, n))

# i = 0
# for data in Lms.load_data('Bahasa Inggris XII (Nurhayati Hutabarat, S.Pd).json'):
#     for activity in data['Activity']:
#         for activity_list in activity['Activity List']:
#             try: 
#                 if "Submitted" in activity_list['detail']['Submission status']:
#                     print(activity_list['Title'])
#                     i += 1
#             except: pass

# print(f'Total submitted assignment: {i}')
