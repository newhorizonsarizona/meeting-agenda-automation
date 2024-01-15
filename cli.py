
#!/usr/bin/python3
import os
from o365.agenda_notifier import AgendaNotifier

agenda_notifier: AgendaNotifier = AgendaNotifier()
if os.environ.get('SEND_ONLY') is not None:
    agenda_notifier.send()
    exit(0)

agenda_notifier.create_and_send()
