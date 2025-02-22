import os
import smtplib
from email.message import EmailMessage
from typing import Dict

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()


def send_email(mood_info: Dict[str, str]) -> None:
    """Sends an email with mood information.

    Args:
        mood_info (Dict[str, str]): A dictionary containing mood-related data,
        including date and remarks.
    """

    # load smtp settings from .env
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    email_from = os.getenv("EMAIL_FROM")
    email_to = os.getenv("EMAIL_TO")

    # get CC addresses
    email_cc_raw = os.getenv("EMAIL_CC", "")
    email_cc = [addr.strip() for addr in email_cc_raw.split(",") if addr.strip()]

    # create email content
    subject = f"BLC Stimmungsbarometer | {mood_info['Datum']}"
    body_lines = []
    for key, value in mood_info.items():
        if key == "Datum":
            continue
        if key == "Bemerkung":
            body_lines.append(f"\n\n{key}: {value}")
        else:
            body_lines.append(f"{key}: {value}")
    body = "\n".join(body_lines)

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = email_from
    msg["To"] = email_to
    if email_cc:
        msg["Cc"] = ", ".join(email_cc)

    msg.set_content(body)

    recipients = [email_to] + email_cc

    try:
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg, from_addr=email_from, to_addrs=recipients)
        server.quit()
    except Exception as e:
        if os.getenv("DEBUG", "0") != "0":
            print("Error during sending email:", e)


def get_mood_info(page_content: str) -> Dict[str, str]:
    """Extracts mood information from the provided HTML page content.

    Args:
        page_content (str): The HTML content of the page to parse.

    Returns:
        Dict[str, str]: A dictionary containing extracted mood data,
        including date, mood levels, and remarks.
    """
    soup = BeautifulSoup(page_content, "html.parser")
    profile_part = soup.find("kgr-profile-part", {"heading": "Stimmungsbarometer"})
    if not profile_part:
        print("'kgr-profile-part' not found in HTML.")
        return

    # extract current date from page
    note = profile_part.get("note", "")
    date = note.strip("()")

    # extract mood and text field
    template = profile_part.find("template", {"slot": "content"})
    mood_info = {}
    text_field = ""
    if template:
        content_soup = BeautifulSoup(template.decode_contents(), "html.parser")
        dl = content_soup.find("dl", class_="kgr-definitionList")
        if dl:
            dt_elements = dl.find_all("dt")
            dd_elements = dl.find_all("dd")
            for dt, dd in zip(dt_elements, dd_elements):
                label = dt.get_text(strip=True).replace(":", "")
                mood_picker = dd.find("kgr-child-mood-picker")
                if mood_picker:
                    value = mood_picker.get("value")
                    mood_info[label] = value
        p_tag = content_soup.find("p")
        if p_tag:
            text_field = p_tag.get_text(strip=True)

    if os.getenv("DEBUG", "0") != "0":
        print("Datum:", date)
        print("Daten:", mood_info)
        print("Bemerkung:", text_field)

    mood_info["Datum"] = date
    mood_info["Bemerkung"] = text_field

    return mood_info


def get_page_content() -> str:
    """Retrieves the mood information page content after logging in.

    Returns:
        str: The HTML content of the target page containing mood information.
    """
    USERNAME = os.getenv("USERNAME")
    PASSWORD = os.getenv("PASSWORD")
    CHILD_ID = os.getenv("CHILD_ID")
    DEBUG = os.getenv("DEBUG", "0")
    LOGIN_URL = os.getenv("LOGIN_URL", "https://app.kigaroo.de/login")
    LOGIN_ACTION = os.getenv("LOGIN_ACTION", "https://app.kigaroo.de/login_check")
    BACKEND_URL = os.getenv("BACKEND_URL", "https://app.kigaroo.de/backend")

    if not USERNAME or not PASSWORD or not CHILD_ID:
        print("Please define USERNAME, PASSWORD and CHILD_ID in the .env file.")
        return

    session = requests.Session()
    session.get(LOGIN_URL)

    # login with username and password from .env
    payload = {"_username": USERNAME, "_password": PASSWORD}
    login_response = session.post(LOGIN_ACTION, data=payload)
    if login_response.status_code != 200 and DEBUG != "0":
        print("Error during login:", login_response.status_code)
        return

    backend_response = session.get(BACKEND_URL)
    if backend_response.status_code != 200 and DEBUG != "0":
        print("Login seems to have failed.")
        return

    # load target page with mood information
    target_url = f"{BACKEND_URL}/child/{CHILD_ID}/show"
    target_response = session.get(target_url)
    if target_response.status_code != 200 and DEBUG != "0":
        print("Error during fetching the target page:", target_response.status_code)
        return

    return target_response.text


def main():
    page_content = get_page_content()

    mood_info = get_mood_info(page_content)

    send_email(mood_info)


if __name__ == "__main__":
    main()
