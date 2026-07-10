# Daily NYS Jobs Emailer

This is a Python script created to pull jobs from the NYS government jobs website every day and email them to the user. The script filters job titles based on specific criteria, which are currently hardcoded.

## Setup Instructions Local
To use the script locally, make sure to run the following commands to set up the environment variables in the current session of your PowerShell:

**Powershell:**
```powershell
$env:SENDER_EMAIL = "sender@gmail.com"
$env:RECIPIENT_EMAIL = "recipient@gmail.com"
$env:PASSWORD = "sender email password"
```

**Bash:**
```bash
export SENDER_EMAIL="sender@gmail.com"
export RECIPIENT_EMAIL="recipient@gmail.com"
export PASSWORD="sender email password"
```

**Command Prompt**
```batch
set SENDER_EMAIL=sender@gmail.com
set RECIPIENT_EMAIL=recipient@gmail.com
set PASSWORD=sender email password
```

After this, it's just installing the requirements and running the script. The **jobs_history.db** database file is used to keep track of the most up to date jobs. It checks any jobs that get posted ahead of the latest.


## Set Up Scheduling
I am using github actions as a scheduler to send me new job postings everyday. All you need to do is fork this repository and set up your git [secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions).

Make sure the SENDER_EMAIL, RECIPIENT_EMAIL and PASSWORD environment variables are in the action secrets for this to work with Github actions.


<img width="491" height="345" alt="image" src="https://github.com/user-attachments/assets/17c5f61e-9699-4661-962e-f2c95d269923" />

### Setting up sender email
Gmail doesn't allow you to programmatically log in to your account to send an email with your traditional email password. You need what is called and Application-specific password.

You first need to goto the security and sign-ins section and set up two factor authentication.
<img width="1120" height="222" alt="image" src="https://github.com/user-attachments/assets/cbee1432-4f94-48b0-b0d9-fc46bae47fea" />

<img width="846" height="187" alt="image" src="https://github.com/user-attachments/assets/29e6195e-63dd-49bc-9b33-21d79bbee2eb" />

<img width="619" height="362" alt="image" src="https://github.com/user-attachments/assets/4569b3a0-fbf8-4b4b-b087-f8e161cf16a2" />

You then generate the app password and that is what you put as the PASSWORD secret.

### Configuring Job Title
To configure, the job title, we can edit the **config.ini** file. I am currently searching for IT Specialist jobs, but it can easily be changed to any other job.

```config
[JobTitles]
keywords = 
    Information Technology Specialist,
    Some Other Job
```
