import os
import sqlite3
import requests
import configparser
import sys
import xml.etree.ElementTree as ElementTree
import smtplib, ssl
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

DB_FILE = "jobs_history.db"
URL = "https://statejobs.ny.gov/rss/employeerss.cfm"
MAX_HISTORY = 10000

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def init_db():
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS processed_jobs (
                    link TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Failed to initialize database: {e}")
        sys.exit(1)


def prune_database():
    """Keeps only the newest MAX_HISTORY entries"""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM processed_jobs
                WHERE link NOT IN (
                    SELECT link FROM processed_jobs
                    ORDER BY created_at DESC
                    LIMIT ?
                )
            ''', (MAX_HISTORY,))
            deleted_count = cursor.rowcount
            conn.commit()
            if deleted_count > 0:
                logging.info(f"Deleted {deleted_count} old jobs from the database.")
    except sqlite3.Error as e:
        logging.error(f"Failed to prune database: {e}")


def fetch_data_from_website(url):
    """Fetches RSS feed and turns it into an ElementTree"""
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return ElementTree.fromstring(response.text)
    except requests.RequestException as e:
        logging.error(f"Network error while fetching feed: {e}")
        return None
    except ElementTree.ParseError as e:
        logging.error(f"Failed to parse XML feed: {e}")
        return None


def load_keywords():
    """Loads target keywords from config.ini"""
    config = configparser.ConfigParser()
    if not os.path.exists('config.ini'):
        logging.error("config.ini file not found.")
        sys.exit(1)

    try:
        config.read('config.ini')
        keywords_str = config.get('JobTitles', 'keywords')
        return [keyword.strip().lower() for keyword in keywords_str.split(',') if keyword.strip()]
    except (configparser.NoSectionError, configparser.NoOptionError) as e:
        logging.error(f"Configuration error: {e}")
        sys.exit(1)


def process_jobs(root, keywords):
    """Checks the feed against the DB, returning a formatted string of matched new jobs."""
    new_jobs_found = 0
    matched_jobs_text = ""

    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()

            for job in root.findall(".//item"):
                link_elem = job.find('link')
                title_elem = job.find('title')
                desc_elem = job.find('description')
                pub_date_elem = job.find('pubDate')

                if link_elem is None or title_elem is None:
                    continue

                link = link_elem.text.strip()
                title = title_elem.text.strip()

                # Skip jobs already in history
                cursor.execute("SELECT 1 FROM processed_jobs WHERE link = ?", (link,))
                if cursor.fetchone():
                    continue

                # It's a new job, insert it into the DB
                cursor.execute("INSERT INTO processed_jobs (link) VALUES (?)", (link,))
                new_jobs_found += 1

                # Check if it matches our keywords
                if any(keyword in title.lower() for keyword in keywords):
                    desc = desc_elem.text.strip() if desc_elem is not None else "No description"
                    pub_date = pub_date_elem.text.strip() if pub_date_elem is not None else "Unknown Date"

                    matched_jobs_text += f"{title}\n"
                    matched_jobs_text += f"{link}\n"
                    matched_jobs_text += f"{pub_date}\n"
                    matched_jobs_text += f"{desc}\n"
                    matched_jobs_text += "-" * 90 + "\n"

            conn.commit()
            logging.info(f"Discovered {new_jobs_found} completely new jobs in the feed.")
            return matched_jobs_text

    except sqlite3.Error as e:
        logging.error(f"Database error during job processing: {e}")
        return ""


def load_credentials():
    """Safely loads required environment variables."""
    try:
        sender_email = os.environ['SENDER_EMAIL']
        recipient_email = os.environ['RECIPIENT_EMAIL']
        password = os.environ['PASSWORD']

        return sender_email, recipient_email, password
    except KeyError as e:
        missing_var = e.args[0]
        logging.critical(f"Aborting execution: Missing required environment variable '{missing_var}'.")
        sys.exit(1)


def send_notification_email(body_text):
    """Constructs and sends jobs email."""
    sender_email, recipient_env, password = load_credentials()

    if not all([sender_email, recipient_env, password]):
        logging.error("Missing required email environment variables (SENDER_EMAIL, RECIPIENT_EMAIL, PASSWORD).")
        return

    receiver_emails = [email.strip() for email in recipient_env.split(",") if email.strip()]

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = ", ".join(receiver_emails)
    message["Subject"] = f"Job Notification: {datetime.now().date()}"
    message.attach(MIMEText(body_text, "plain", "utf-8"))

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_emails, message.as_string())
        logging.info("Notification email sent successfully.")
    except smtplib.SMTPException as e:
        logging.error(f"Failed to send email: {e}")


if __name__ == "__main__":
    logging.info("Starting job scraper script...")

    init_db()
    prune_database()

    config_keywords = load_keywords()
    element_root = fetch_data_from_website(URL)

    if element_root is None:
        logging.warning("Aborting execution due to feed fetch/parse failure.")
        sys.exit(1)

    matched_jobs_body = process_jobs(element_root, config_keywords)

    if matched_jobs_body:
        logging.info("Matching jobs found. Sending email...")
        send_notification_email(matched_jobs_body)
    else:
        logging.info("No new matching jobs found. Exiting.")