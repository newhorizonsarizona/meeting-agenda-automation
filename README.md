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
logging onto url 
Followed by that set get thevalue of code from the url, set environment variable and execute ccommand
```
export USER_AUTH_CODE=<CODE FROM URL QUERYSTRING>
python cli.py
```

## Test, package and publish function to Azure 
- To test, package and publish function to Azure, run commands
```
make test
make package 
make login
make publish
```