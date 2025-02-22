# KigaRoo Mood Mailer

This Python script retrieves mood information from **KigaRoo** and sends an email report with the data.

## Features

- **Automated Login:** Uses credentials from a `.env` file to log into KigaRoo.
- **Data Extraction:** Parses mood details (date, mood levels, remarks) from the webpage.
- **Email Notification:** Sends the extracted information via email using SMTP.

## Setup

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/kigaroo-mood-mailer.git
   cd kigaroo-mood-mailer
   ```

2. **Install Dependencies:**

    [Install](https://docs.astral.sh/uv/getting-started/installation/) `uv` first.

   ```bash
   uv venv --python 3.11
   uv sync
   ```

3. **Configure Environment Variables:**

    Create a `.env` file in the project root with your configuration:

   ```python
   SMTP_SERVER=smtp.example.com
   SMTP_PORT=587
   SMTP_USERNAME=your_smtp_username
   SMTP_PASSWORD=your_smtp_password
   EMAIL_FROM=sender@example.com
   EMAIL_TO=recipient@example.com
   EMAIL_CC=cc1@example.com, cc2@example.com  # Optional

   USERNAME=your_kigaroo_username
   PASSWORD=your_kigaroo_password
   CHILD_ID=your_child_id

   # keep these values
   LOGIN_URL=https://app.kigaroo.de/login
   LOGIN_ACTION=https://app.kigaroo.de/login_check
   BACKEND_URL=https://app.kigaroo.de/backend

   DEBUG=0
   ```

   You'll find the child id in the URL of the mood page: `https://app.kigaroo.de/backend/child/{CHILD_ID}/show`.

## Usage

Run the script with:

```bash
source bin/activate

python get_mood_script.py
```

You can schedule this script to run daily or weekly with a [cron job](https://askubuntu.com/questions/2368/how-do-i-set-up-a-cron-job).

## License

This project is licensed under the MIT License.
