#!/usr/bin/python3
import os
from o365.agenda_notifier import AgendaNotifier

agenda_notifier: AgendaNotifier = AgendaNotifier()
user_auth_code: str = os.environ.get('USER_AUTH_CODE')
if user_auth_code is not None and len(user_auth_code.strip()) > 0:
    agenda_notifier.send()
    exit(0)

agenda_notifier.create()
