# Weekly Meeting Agenda Automation
This is the Weekly Meeting Agenda Automation project. 
## Prerequisites 
- There needs to be a planner template `Template - Weekly Meeting Signup`
- The project needs buckets named in the format `YYYYMMDD Meeting Roles` where each task associated to speaking and functionary roles in the weekly meeting is located.

## Format and code lint
- To format and test code
```
make format
make test-python
```

## Execute Automation Locally 
### Create Agenda
To run the automation locally to generate the agenda, from command line execute

```
pip3 install pipenv 
pipenv install --dev
pipenv shell 
export CLIENT_SECRET=<CLIENT SECRET FROM AZURE APP REGISTRATION>
./nhtm_automation.sh agenda create-weekly-meeting-agenda
```
### Send Agenda Notification on Teams
To send the notification on Teams, first get the oauth authorization code by
logging onto the [Microsoft Authorization URL](https://login.microsoftonline.com/9add987e-b316-43b4-8750-4007763832b0/oauth2/v2.0/authorize?client_id=68e11217-f842-4df4-8720-75a08c58f491&response_type=code&redirect_uri=https%3A%2F%2Fweeklymeetingagenda.azurewebsites.net%2F&response_mode=query&scope=user.read&state=12345) for the tenant annd client associated to the AgendaAutomation App Registration.  
Followed by that get the value of `code` from the url query string, set environment variable and execute command
```
pip3 install pipenv 
pipenv install --dev
pipenv shell 
export CLIENT_SECRET=<CLIENT SECRET FROM AZURE APP REGISTRATION>
export USER_AUTH_CODE=<CODE FROM URL QUERYSTRING>
./nhtm_automation.sh agenda notify-on-teams
```
### Create next months Weekly Meeting Signup Plan
To create the plan for next month. Add tasks from `YYYYMMDD Meeting Roles` bucket in the `Template - Weekly Meeting Signup` plan into corresponding buckets for next month. 
```
pip3 install pipenv 
pipenv install --dev
pipenv shell 
export CLIENT_SECRET=<CLIENT SECRET FROM AZURE APP REGISTRATION>
./nhtm_automation.sh planner create-weekly-meeting-plan
./nhtm_automation.sh planner create-weekly-meeting-plan --month Jun
```
### Delete last months Weekly Meeting Signup Plan
To delete the plan for last month. 
```
pip3 install pipenv 
pipenv install --dev
pipenv shell 
export CLIENT_SECRET=<CLIENT SECRET FROM AZURE APP REGISTRATION>
./nhtm_automation.sh planner delete-weekly-meeting-plan 
./nhtm_automation.sh planner delete-weekly-meeting-plan --month Apr
```

## Test, package and publish pthon binaries
- To test, package and publish python binaries
```
#todo
```