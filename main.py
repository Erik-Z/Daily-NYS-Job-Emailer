import os
import requests
import configparser
import xml.etree.ElementTree as ET
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


def fetch_data_from_website(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return None


def create_xml_file(data, output_file):
    root = ET.fromstring(data)
    tree = ET.ElementTree(root)
    tree.write(output_file)


def load_xml_file(input_file):
    tree = ET.parse(input_file)
    root = tree.getroot()
    return root


if __name__ == "__main__":
    url = "https://statejobs.ny.gov/rss/employeerss.cfm"
    xml_file = "jobs.xml"
    
    root = load_xml_file(xml_file)

    if root.findall(".//item"):
        website_data = fetch_data_from_website(url)
        if website_data == None: 
            print("No website data")
            exit()
        create_xml_file(website_data, xml_file)
        print(f"XML file '{xml_file}' updated successfully.")

    latest_current_job = root.findall(".//item/link")[1].text
    root = load_xml_file(xml_file)

    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = os.getenv('SENDER_EMAIL')
    receiver_email = os.getenv('RECIPIENT_EMAIL')
    password = os.getenv('PASSWORD')
    
    message = MIMEMultipart() 
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = f"Subject: Job Notification: {datetime.now().date()}\n"
    message_body = ""
    
    context = ssl.create_default_context()

    config = configparser.ConfigParser()
    config.read('config.ini')
    job_title_keywords = [keyword.strip() for keyword in config.get('JobTitles', 'keywords').split(',')]

    for job in root.findall(".//item"):
        if job.find('link').text == latest_current_job: break
        job_title = job[0].text
        if any(keyword in job_title for keyword in job_title_keywords):       
            message_body += f"{job.find('title').text}\n"
            message_body += f"{job.find('link').text}\n"
            message_body += f"{job.find('pubDate').text}\n"
            message_body += f"{job.find('description').text}\n"
            message_body += "------------------------------------------------------------------------------------------\n"

    message.attach(MIMEText(message_body, "plain", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())