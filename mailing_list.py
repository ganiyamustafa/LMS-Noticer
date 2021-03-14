import os

class MailingList():
    file =  'mailing_list.txt'

    def list_file(self, read=False):
        if not read:
            if not os.path.isfile(self.file):
                return open(self.file, "x")
            else:
                return open(self.file, "a")
        else:
            return open(self.file, "r")

    def get_list(self):
        with self.list_file(read=True) as f:
            list_email = [line.strip("\n") for line in f]
        f.close()
        return list_email

    def validate_email(self, new_mail:str):
        if new_mail.endswith('@gmail.com'):
            return new_mail

    def check_exist(self, email:str):
        with self.list_file(read=True) as f:
            list_email = [line.strip("\n") for line in f]
        f.close()
        if email in list_email: return True

    def add(self, new_mail:str):
        if self.validate_email(new_mail):
            with self.list_file() as f:
                if not self.check_exist(new_mail):
                    f.write(new_mail+"\n")
            f.close()

    def remove(self, del_email:str):
        with open(self.file, "r") as file_input:
            with open("temp.txt", "w") as output: 
                for line in file_input:
                    if line.strip("\n") != del_email:
                        output.write(line)
        file_input.close()
        output.close()
        os.replace("temp.txt", self.file)