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
To send the notification on Teams, visit [the notification page](https://weeklymeetingagenda.azurewebsites.net/api/notify?code=3rNLQKGkzXi3kfC4fpgp0QK0ENoET6x-wfFpyEpHBFtlAzFuKXD3Cg%3D%3D&name=Officer)  associated to the NHTMAutomation App Registration.  
If the app is down, get the `code` from the url query string, set environment variable and execute command
```
pip3 install pipenv 
pipenv install --dev
pipenv shell 
export CLIENT_SECRET=<CLIENT SECRET FROM AZURE APP REGISTRATION>
export TEAMS_WEBHOOK_URL=<THE TEAMS CHANNEL WEBHOOK URL>
./nhtm_automation.sh agenda notify-on-teams
```
### Send Signup Reminder on Teams
To send the notification on Teams, visit [the notification page](https://weeklymeetingagenda.azurewebsites.net/api/notify?code=3rNLQKGkzXi3kfC4fpgp0QK0ENoET6x-wfFpyEpHBFtlAzFuKXD3Cg%3D%3D&name=Officer)  associated to the NHTMAutomation App Registration.  
If the app is down, get the `code` from the url query string, set environment variable and execute command
```
pip3 install pipenv 
pipenv install --dev
pipenv shell 
export CLIENT_SECRET=<CLIENT SECRET FROM AZURE APP REGISTRATION>
export TEAMS_WEBHOOK_URL=<THE TEAMS CHANNEL WEBHOOK URL>
./nhtm_automation.sh agenda signup-reminder-on-teams
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

### Sync Weekly Meeting Signup tasks for next week with tasks in bucket for next week
To sync the signup tasks with tasks in bucket for next week. 
```
pip3 install pipenv 
pipenv install --dev
pipenv shell 
export CLIENT_SECRET=<CLIENT SECRET FROM AZURE APP REGISTRATION>
./nhtm_automation.sh planner sync-signup-with-plan 
./nhtm_automation.sh planner sync-signup-with-plan --month Apr
./nhtm_automation.sh planner sync-signup-with-plan --month Jan --year 2025
```

## Test, package and publish pthon binaries
- To test, package and publish python binaries
```
#todo
```
