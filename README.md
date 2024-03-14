# meeting-agenda-automation
Weekly Meeting Agenda Automation

This is the Weekly Meeting Agenda Automation project. 
## Prerequisites 
- There needs to be a planner project with name in format `Jan - Weekly Meeting Signup` created by making a copy of the planner project template `Template - Weekly Meeting Signup`
- The project needs buckets named in the format `yyyyMMdd - Meeting Role` where each date corresponds to Tuesdays in that month.

## Execute Automation Locally 
- To run the automation locally to generate the agenda, from command line execute

```
pip3 install pipenv 
pipenv install -dev
pipenv shell 
python cli.py
```
- To send the notification on Teams, first get the oauth authorization code by
logging onto the [Microsoft Authorization URL](https://login.microsoftonline.com/9add987e-b316-43b4-8750-4007763832b0/oauth2/v2.0/authorize?client_id=68e11217-f842-4df4-8720-75a08c58f491&response_type=code&redirect_uri=https%3A%2F%2Fweeklymeetingagenda.azurewebsites.net%2F&response_mode=query&scope=user.read&state=12345) for the tenant annd client associated to the AgendaAutomation App Registration.  
Followed by that set get the value of code from the url query string, set environment variable and execute command
```
export USER_AUTH_CODE=<CODE FROM URL QUERYSTRING>
python cli.py
```

## Test, package and publish function to Azure 
- To test, package and publish function to Azure, run commands
``emake test
make package 
make logi```