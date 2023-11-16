import os
import requests
import xml.etree.ElementTree as ET
from dateutil import parser
from datetime import datetime, timedelta
from pytz import timezone
import smtplib, ssl

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


def get_most_recent_friday():
    tz = timezone("US/Eastern")
    current_date = datetime.now(tz=tz).date()
    days_to_subtract = (current_date.weekday() - 4) % 7  # Calculate days to the most recent Friday
    most_recent_friday = current_date - timedelta(days=days_to_subtract)
    return most_recent_friday


def is_update_needed(pub_date_str):
    tz = timezone("US/Eastern")
    current_date = datetime.now(tz=tz).date()
    pub_date = parser.parse(pub_date_str, tzinfos={"EST": -5*3600}).date()
    return pub_date < current_date


if __name__ == "__main__":
    url = "https://statejobs.ny.gov/rss/employeerss.cfm"
    xml_file = "jobs.xml"
    
    root = load_xml_file(xml_file)

    if root.findall(".//item"):
        latest_pub_date = root.findall(".//item/pubDate")[1].text
        if is_update_needed(latest_pub_date):
            website_data = fetch_data_from_website(url)
            if website_data == None: 
                print("No website data")
                exit()
            create_xml_file(website_data, xml_file)
            print(f"XML file '{xml_file}' updated successfully.")
        else:
            print(f"No update needed. Using existing XML file.")
    else:
        website_data = fetch_data_from_website(url)
        if website_data:
            create_xml_file(website_data, xml_file)
            print(f"XML file '{xml_file}' created successfully.")

    latest_pub_date = root.findall(".//item/pubDate")[1].text
    pub_date = parser.parse(latest_pub_date, tzinfos={"EST": -5*3600}).date()
    root = load_xml_file(xml_file)

    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = os.getenv('SENDER_EMAIL')
    receiver_email = os.getenv('RECIPIENT_EMAIL')
    password = os.getenv('PASSWORD')
    message = f"Subject: Job Notification: {datetime.now().date()}\n" 
    context = ssl.create_default_context()

    for job in root.findall(".//item"):
        if "Information Technology Specialist" not in job[0].text: continue
        if parser.parse(job.find("pubDate").text, tzinfos={"EST": -5*3600}).date() <= pub_date: continue
        message += f"{job.find('title').text}\n"
        message += f"{job.find('link').text}\n"
        message += f"{job.find('pubDate').text}\n"
        message += f"{job.find('description').text}\n"
        message += "------------------------------------------------------------------------------------------\n"

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)