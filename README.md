# Daily NYS Jobs Emailer

This is a Python script created to pull jobs from the NYS government jobs website every day and email them to the user. The script filters job titles based on specific criteria, which are currently hardcoded.

### Setup Instructions Local

To use the script locally, make sure to run the following commands to set up the environment variables in the current session of your PowerShell:

**Powershell:**
```powershell
$env:SENDER_EMAIL = "email@gmail.com"
$env:RECIPIENT_EMAIL = "email@gmail.com"
$env:PASSWORD = "email app password"
```

**Bash:**
```bash
export SENDER_EMAIL="email@gmail.com"
export RECIPIENT_EMAIL="email@gmail.com"
export PASSWORD="email app password"
```

**Command Prompt**
```batch
set SENDER_EMAIL=email@gmail.com
set RECIPIENT_EMAIL=email@gmail.com
set PASSWORD=email app password
```

After this, it's just installing the requirements and running the script. The **jobs.xml** file is used to keep track of the most up to date jobs. It checks any jobs that get posted ahead of the latest.


### Set Up Scheduling

I am using github actions as a scheduler to send me new job postings everyday. All you need to do is fork this repository and set up your git [secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions).