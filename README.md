# Daily NYS Jobs Emailer

This is a Python script created to pull jobs from the NYS government jobs website every day and email them to the user. The script filters job titles based on specific criteria, which are currently hardcoded.

### Setup Instructions Local

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

After this, it's just installing the requirements and running the script. The **jobs.xml** file is used to keep track of the most up to date jobs. It checks any jobs that get posted ahead of the latest.


### Set Up Scheduling

I am using github actions as a scheduler to send me new job postings everyday. All you need to do is fork this repository and set up your git [secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions).

Make sure the SENDER_EMAIL, RECIPIENT_EMAIL and PASSWORD environment variables are in the action secrets for this to work with Github actions.
<img width="491" height="345" alt="image" src="https://github.com/user-attachments/assets/17c5f61e-9699-4661-962e-f2c95d269923" />

### Configuring Job Title

To configure, the job title, we can edit the **config.ini** file. I am currently searching for IT Specialist jobs, but it can easily be changed to any other job.

```config
[JobTitles]
keywords = 
    Information Technology Specialist,
    Some Other Job
```
