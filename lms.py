import mechanicalsoup
from json_handler import save_data, load_data
from threading import Thread
import numpy as np
import os

class LMS():
    base_url = "https://lms.smkn1-cmi.sch.id/"
    browser = mechanicalsoup.StatefulBrowser()
    browser.open(base_url)
    username = ""
    password = ""
    course_list = 'Course Data/XII RPL A/Course List.json'

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def login(self):
        if not self.is_logged():
            self.browser.follow_link("login/index.php")
            self.browser.select_form('form[id="login"]')
            self.browser["username"] = self.username
            self.browser["password"] = self.password
            self.browser.submit_selected()

    def is_logged(self):
        test_link = 'https://lms.smkn1-cmi.sch.id/my/'
        self.browser.open(test_link)
        result = self.browser.url == test_link
        self.browser.open(self.base_url)
        return result

    def page(self):
        return self.browser.get_current_page()

    def get_courses(self):
        self.login()
        courses_list = []
        self.browser.open(f"{self.base_url}/my/index.php?mynumber=-2")

        for course in self.page().select('.course_list .coursebox .course_title h2'):
            courses = {}
            courses['Title'] = course.text
            courses['Link'] = course.a['href']
            courses_list.append(courses)
        save_data('Course Data/XII RPL A/', 'Course List.json', courses_list)

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
                
                activity_list.append(activity)

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
            t.start()

        for t in threads:
            t.join()

        return data_list

    def course_updated(self, course:str):
        self.login()

        if not os.path.isfile(f'Course Data/XII RPL A/{course}.json'):
            print(f'Creating Course Data/XII RPL A/{course}.json...')
            self.get_course_detail(course)

        old_data = load_data(f'Course Data/XII RPL A/{course}.json')
        data = self.get_assignment(load_data(self.course_list), course)
        data_copied = data.copy()

        title = [d['Title'] for d_ in data[0]['Activity'] for d in d_['Activity List'] if d['Link']]
        data = [d['Link'] for d_ in data[0]['Activity'] for d in d_['Activity List'] if d['Link']]

        old_title = [d['Title'] for od in old_data[0]['Activity'] for d in od['Activity List'] if d['Link']]
        old_data = [d['Link'] for od in old_data[0]['Activity'] for d in od['Activity List'] if d['Link']]

        diff = np.setdiff1d(data, old_data)
        
        save_data('Course Data/XII RPL A/', f'{course}.json', data_copied)

        return diff if diff.size > 0 else []

    def get_course_detail(self, course:str):
        self.login()
        save_data('Course Data/XII RPL A/', f'{course}.json', self.get_assignment(load_data(self.course_list), course))
        return load_data(f'Course Data/XII RPL A/{course}.json')

# lms = LMS('181113847', 'PRSYETI1')
# for course in ['PPKn XII (Tintin Sutrisni)', 'Produk Kreatif Kewirausahaan XII (Sopiah)', 'Bahasa Indonesia XII (Dra. Hj. Sri Gantini, M.Pd)', 'Bahasa Inggris XII (Nurhayati Hutabarat, S.Pd)', 'Bahasa Jepang XII (Rukti Ananditya Karunia Sari, S.Pd.)', 'PABP XII (LUKMAN)']:
#     print(course)
#     lms.get_course_detail(course)