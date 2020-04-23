#!/usr/bin/env python3

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

import instaloader
import time
import datetime
import os
import re


def generate_hrefs(names):
    res = ""
    if not names:
        return """
        <p><span style="font-family: Arial, Helvetica, sans-serif;">
        Nobody unfollowed you since the last report.</span></p>
        """
    for name in names: 
        res += """
        <li><span style="font-family: 
        Arial, Helvetica, sans-serif;"><a href="%s">%s</a></span></li>
        """ % (name, name)
    return res


def send_email(toaddr, new_followers, unfollowers):
    msg = MIMEMultipart()
    email_address = "EMAILADDRESS"
    email_password = "EMAILPASSWORD"
    smtp_port = 587
    t_format = '%Y-%m-%d %H-%M-%S'


    msg['From'] = email_address
    msg['To'] = toaddr
    msg['Subject'] = 'Unfollowers %s' % time.strftime(t_format)

    body = """
<p><span style="font-family: Arial, Helvetica, sans-serif;">Hello!</span></p>
<p><span style="font-family: 
        Arial, Helvetica, sans-serif;">For today you have a total of <strong>%s unfollowers&nbsp;</strong>and<strong>&nbsp;%s new followers.</strong></span></p>
<p><span style="font-family: 
        Arial, Helvetica, sans-serif;">Here is the list of people who unfollowed you since the last email:</span></p>
<ol>
        %s
</ol>
<p><span style="font-family: 
        'Arial Black', Gadget, sans-serif;"><br></span></p>
<p><br></p>
""" % (
    len(new_followers),
    len(unfollowers),
    generate_hrefs(unfollowers)
    )

    msg.attach(MIMEText(body, 'html'))

    s = smtplib.SMTP('smtp.gmail.com', smtp_port) #587
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(email_address, email_password)
    text = msg.as_string()
    s.sendmail(email_address, toaddr, text)
    s.quit()


def main():
    insta_client = instaloader.Instaloader()

    credentials = {
        "username": "USERNAME",
        "password": "PASSWORD"
        }

    insta_client.login(credentials["username"], credentials["password"])
    profile=instaloader.Profile.from_username(insta_client.context, credentials["username"])

    follow_list=[]
    t_format = '%Y-%m-%d %H-%M-%S'
    new_filename="InstaFile %s%s" % (time.strftime(t_format),".txt")

    with open(new_filename, "w") as new_file:
        for follower in profile.get_followers():
            new_file.write(follower.username + '\n')

    good_paths = [path for path in os.listdir(os.getcwd()) 
                if re.match("InstaFile.*", path) and path != new_filename]

    if good_paths:
        striped_paths = [path.replace("InstaFile ", '').replace(".txt", '') for path in good_paths]
        time_stamps = [time.mktime(datetime.datetime.strptime(s_path, t_format).timetuple()) for s_path in striped_paths]

        file_dict = dict(zip(time_stamps, good_paths))
        latest = file_dict[max(time_stamps)]

        for time_stamp in file_dict:
            if file_dict[time_stamp] != latest:
                os.remove(file_dict[time_stamp])


        set_f1 = set()
        set_f2 = set()
        with open(latest, "r") as f1, open(new_filename, "r") as f2:
            for line in f1.readlines():
                set_f1.add(line.strip('\n'))
            for line in f2.readlines():
                set_f2.add(line.strip('\n'))

            send_email("TO_ADDRESS", 
                    set_f2 - set_f1,
                    set_f1 - set_f2)


if __name__ == "__main__":
    main()