import urllib
from o365.agenda_excel import AgendaExcel
from o365.util.date_util import DateUtil
from o365.weekly_meeting_planner import WeeklyMeetingPlanner


class WeeklyMeetingMessage:
    """This class is used for storing the weekly meeting message"""

    _subject: str = "{meeting_date} - WEEKLY MEETING"
    _title: str = "WEEKLY MEETING @ Cadence Living in Chandler, 100 W Queen Creek Rd., Chandler, AZ 85248"
    _salutation: str = "Dear New Horizons Toastmasters Club members,"
    _message_part1: str = (
        "Please find attached the agenda for the {meeting_day}, {meeting_date} meeting. \
                This is going to be a hybrid meeting. Guests are welcome."
    )
    _message_part2: str = (
        "{speakers_display_names} please place your speech introduction(s) and evaluation forms in the meeting folder. \
                {topics_master_display_name} please post the meeting theme here."
    )
    _message_part3: str = "_Meeting Folder:_ {meeting_folder_url}"
    _message_part4: str = "_Agenda:_ {meeting_agenda_url}"
    _message_reminders: str = "REMINDERS: Please mute your phones"
    _message_footer1: str = "Best Regards,"
    _message_footer2: str = "NHTM Education Committee"
    _message: str = (
        " \
        {meeting_date} {title}<br/> \
        {attachments}<div>{salutation}<br/><br/> \
            {message_part1}<br/> \
            {speakers_mention} please place your speech introduction(s) and evaluation forms in the meeting folder. \
                {topics_master_mention} please post the meeting theme here.<br/><br/> \
            <u>Meeting Folder:</u> {meeting_folder_url}<br/> \
            <u>Agenda:</u> {meeting_agenda_url}<br/> \
            {message_reminders}<br/><br/> \
        {message_footer1},<br/> \
        {message_footer2}<br/></div>"
    )
    speaker_users: list = []
    topics_master_user = None
    meeting_agenda_item = None
    meeting_folder_item = None
    attachment_content_type: str = "application/vnd.ms-excel"

    def __init__(
        self,
        meeting_date,
        meeting_day,
        speaker_users,
        topics_master_user,
        meeting_folder_item,
        meeting_agenda_item,
    ) -> None:
        """initialize the message assignments"""
        self._subject = self._subject.format(meeting_date=meeting_date)
        self.speaker_users = speaker_users
        self.topics_master_user = topics_master_user
        self.meeting_agenda_item = meeting_agenda_item
        self.meeting_folder_item = meeting_folder_item
        speakers_mention = ""
        speakers_display_names = ""
        mention_id = 0
        for speaker_user in speaker_users:
            speakers_mention += f'<at id="{mention_id}">{speaker_user["displayName"]}</at>, '
            speakers_display_names += f'{speaker_user["displayName"]}, '
            mention_id += 1
        topics_master_mention = f'<at id="{mention_id}">{topics_master_user["displayName"]}</at>'
        attachments = f'<attachment id="{meeting_agenda_item["id"]}">{meeting_agenda_item["name"]}</attachment>'
        self._message_part1 = self._message_part1.format(meeting_date=meeting_date, meeting_day=meeting_day)
        self._message_part2 = self._message_part2.format(
            speakers_display_names=speakers_display_names, topics_master_display_name=topics_master_user["displayName"]
        )
        self._message_part3 = self._message_part3.format(
            meeting_folder_url=f'[{meeting_folder_item["name"].strip()}]({meeting_folder_item["webUrl"].strip()})'
        )
        self._message_part4 = self._message_part4.format(
            meeting_agenda_url=f'[{meeting_agenda_item["name"].strip()}]({meeting_agenda_item["webUrl"].strip()})'
        )
        self._message = self._message.format(
            meeting_date=meeting_date,
            message_part1=self._message_part1,
            title=self._title,
            salutation=self._salutation,
            speakers_mention=speakers_mention,
            topics_master_mention=topics_master_mention,
            meeting_folder_url=f'<a href="{meeting_folder_item["webUrl"]}">{meeting_folder_item["name"]}</a>',
            meeting_agenda_url=f'<a href="{meeting_agenda_item["webUrl"]}">{meeting_agenda_item["name"]}</a>',
            attachments=attachments,
            message_reminders=self._message_reminders,
            message_footer1=self._message_footer1,
            message_footer2=self._message_footer2,
        )

    @property
    def subject(self) -> None:
        """get the trimmed subject"""
        return self._subject.strip().strip("\n")

    @property
    def message(self) -> None:
        """get the trimmed message"""
        return self._message.strip().strip("\n")

    @property
    def adaptive_card_message(self):
        """get the adaptive card message for notification"""
        adaptive_card_message = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.2",
                        "body": [
                            {
                                "type": "Container",
                                "items": [
                                    {
                                        "type": "TextBlock",
                                        "text": f"{self._subject}",
                                        "weight": "bolder",
                                        "size": "large",
                                        "wrap": True,
                                        "isMarkdown": True,
                                    }
                                ],
                            },
                            {
                                "type": "Container",
                                "items": [
                                    {
                                        "type": "TextBlock",
                                        "text": f"{self._title}",
                                        "weight": "bolder",
                                        "size": "medium",
                                        "wrap": True,
                                        "isMarkdown": True,
                                    },
                                    {
                                        "type": "TextBlock",
                                        "text": f"{self._salutation}",
                                        "size": "medium",
                                        "wrap": True,
                                        "isMarkdown": True,
                                    },
                                    {
                                        "type": "TextBlock",
                                        "text": f"{self._message_part1}",
                                        "size": "medium",
                                        "wrap": True,
                                        "isMarkdown": True,
                                    },
                                    {
                                        "type": "TextBlock",
                                        "text": f"{self._message_part2}",
                                        "size": "medium",
                                        "wrap": True,
                                        "isMarkdown": True,
                                    },
                                    {
                                        "type": "TextBlock",
                                        "text": f"{self._message_part3}",
                                        "size": "medium",
                                        "wrap": True,
                                        "isMarkdown": True,
                                    },
                                    {
                                        "type": "TextBlock",
                                        "text": f"{self._message_part4}",
                                        "size": "medium",
                                        "wrap": True,
                                        "isMarkdown": True,
                                    },
                                    {
                                        "type": "TextBlock",
                                        "text": f"{self._message_reminders}",
                                        "size": "medium",
                                        "weight": "bolder",
                                        "wrap": True,
                                        "isMarkdown": True,
                                    },
                                    {
                                        "type": "TextBlock",
                                        "text": f"{self._message_footer1}",
                                        "size": "medium",
                                        "wrap": True,
                                        "isMarkdown": True,
                                    },
                                    {
                                        "type": "TextBlock",
                                        "text": f"{self._message_footer2}",
                                        "size": "medium",
                                        "wrap": True,
                                        "isMarkdown": True,
                                    },
                                ],
                            },
                        ],
                    },
                }
            ],
        }
        return adaptive_card_message

    @staticmethod
    def adaptive_card_signup_message(meeting_date, meeting_day, meeting_agenda_item, agenda_excel: AgendaExcel):
        """get the adaptive card message for signup reminder"""
        _message_part1: str = (
            f"Please signup [HERE](https://forms.office.com/r/wjCgSjdbk6) \
                for the {meeting_day}, {meeting_date} meeting. \
                    The following functionary roles have not yet been filled \
                        on [{meeting_agenda_item['name']}]({meeting_agenda_item['webUrl']})"
        )
        _message_part2: str = ""
        for role_name, assignment_member in agenda_excel.all_functionary_role_assignments.items():
            if assignment_member is None:
                _message_part2 += f"* {role_name}\n\n"
        if _message_part2 == "":
            return None
        adaptive_card_message = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.2",
                        "body": [
                            {
                                "type": "Container",
                                "items": [
                                    {
                                        "type": "TextBlock",
                                        "text": "Speaker/Functionary Role Signup Reminder",
                                        "weight": "bolder",
                                        "size": "large",
                                        "wrap": True,
                                        "isMarkdown": True,
                                    }
                                ],
                            },
                            {
                                "type": "Container",
                                "items": [
                                    {
                                        "type": "TextBlock",
                                        "text": "Available for next week's weekly meeting",
                                        "weight": "bolder",
                                        "size": "medium",
                                        "wrap": True,
                                        "isMarkdown": True,
                                    },
                                    {
                                        "type": "TextBlock",
                                        "text": "Dear New Horizons Toastmasters Club members,",
                                        "size": "medium",
                                        "wrap": True,
                                        "isMarkdown": True,
                                    },
                                    {
                                        "type": "TextBlock",
                                        "text": _message_part1,
                                        "size": "medium",
                                        "wrap": True,
                                        "isMarkdown": True,
                                    },
                                    {
                                        "type": "TextBlock",
                                        "text": _message_part2,
                                        "size": "medium",
                                        "wrap": True,
                                        "isMarkdown": True,
                                    },
                                    {
                                        "type": "TextBlock",
                                        "text": "Best Regards,",
                                        "size": "medium",
                                        "wrap": True,
                                        "isMarkdown": True,
                                    },
                                    {
                                        "type": "TextBlock",
                                        "text": "Toastmaster",
                                        "size": "medium",
                                        "wrap": True,
                                        "isMarkdown": True,
                                    },
                                ],
                            },
                        ],
                    },
                }
            ],
        }
        return adaptive_card_message

    @staticmethod
    def adaptive_card_signup_sheet_message(meeting_date_role_assignments: dict, meeting_date_absentees: dict):
        """get the adaptive card message for future signup reminder"""

        adaptive_card_message = {
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "type": "AdaptiveCard",
            "version": "1.5",
            "body": [
                {
                    "type": "Container",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "Speaker/Functionary Role Signup Sheet",
                            "weight": "bolder",
                            "size": "large",
                            "wrap": "true",
                            "isMarkdown": "true",
                        }
                    ],
                },
                {
                    "type": "Container",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "Dear New Horizons Toastmasters Club members,",
                            "size": "medium",
                            "wrap": "true",
                            "isMarkdown": "true",
                        },
                        {
                            "type": "TextBlock",
                            "text": "Please signup for a speaking or functionary role for an upcoming meeting.",
                            "size": "medium",
                            "wrap": "true",
                            "isMarkdown": "true",
                        },
                    ],
                },
            ],
        }

        message_signup_sheet_header = {"type": "ColumnSet", "columns": []}
        message_signup_sheet_header_cols = [
            {
                "type": "Column",
                "width": "90px",
                "items": [
                    {
                        "type": "TextBlock",
                        "text": "Role",
                        "weight": "Bolder",
                        "wrap": "true",
                        "size": "medium",
                    }
                ],
            }
        ]
        meeting_dates = meeting_date_role_assignments.keys()
        for meeting_date in meeting_dates:
            message_signup_sheet_header_cols.append(
                {
                    "type": "Column",
                    "width": "85px",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": f"{meeting_date.strftime('%m/%d/%Y')}",
                            "size": "medium",
                            "weight": "Bolder",
                            "wrap": "true",
                        }
                    ],
                },
            )
        message_signup_sheet_header["columns"] = message_signup_sheet_header_cols
        adaptive_card_message["body"].append(message_signup_sheet_header)
        weekly_meeting_planner = WeeklyMeetingPlanner()
        functionary_roles = [
            "Joke Master",
            "Toastmaster",
            "General Evaluator",
            "Speaker 1",
            "Speaker 2",
            "Speaker 3",
            "Manual Evaluator 1",
            "Manual Evaluator 2",
            "Manual Evaluator 3",
            "Ah Counter",
            "Grammarian",
            "Timer",
            "Ballot Counter",
            "WOW",
            "GEM",
        ]

        for role_name in functionary_roles:
            message_signup_sheet_body = {"type": "ColumnSet", "columns": []}
            message_signup_sheet_body_cols = [
                {
                    "type": "Column",
                    "width": "90px",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": role_name,
                            "weight": "Bolder",
                            "wrap": "true",
                            "size": "medium",
                        }
                    ],
                }
            ]
            for meeting_date in meeting_dates:
                date_val = urllib.parse.quote(f"{meeting_date.strftime('%m/%d/%Y')} 7:00 PM")
                functionary_role_4_form = urllib.parse.quote(role_name)
                if "Speaker" in role_name:
                    functionary_role_4_form = urllib.parse.quote("Speaker")
                elif "Manual Evaluator" in role_name:
                    functionary_role_4_form = urllib.parse.quote("Manual Evaluator")
                elif "WOW" in role_name:
                    functionary_role_4_form = urllib.parse.quote("WOW (Words Of Wisdom)")
                elif "GEM" in role_name:
                    functionary_role_4_form = urllib.parse.quote("GEM (Great Educational Moment)")
                # message_text = "[Signup](https://forms.office.com/r/wjCgSjdbk6)"
                message_text = f"[Signup](https://forms.office.com/r/wjCgSjdbk6?\
r9ac7132bd52447e2b6bcd479a021b876=%22{date_val}%22&\
rc90e248ef4b146ecb89c31e0b4ca94c1=%22{functionary_role_4_form}%22)"
                if meeting_date_role_assignments and meeting_date_role_assignments[meeting_date][role_name] is not None:
                    message_text = weekly_meeting_planner.get_assigned_to_user(
                        meeting_date_role_assignments[meeting_date][role_name]
                    ).display_name
                message_signup_sheet_body_cols.append(
                    {
                        "type": "Column",
                        "width": "85px",
                        "items": [
                            {
                                "type": "TextBlock",
                                "text": message_text,
                                "wrap": "true",
                                "size": "medium",
                                "isMarkdown": "true",
                            },
                        ],
                    },
                )
            message_signup_sheet_body["columns"] = message_signup_sheet_body_cols
            adaptive_card_message["body"].append(message_signup_sheet_body)

        message_signup_sheet_absentee_body = {"type": "ColumnSet", "columns": []}
        message_signup_sheet_absentee_body_cols = [
            {
                "type": "Column",
                "width": "90px",
                "items": [
                    {
                        "type": "TextBlock",
                        "text": "Absent",
                        "weight": "Bolder",
                        "wrap": "true",
                        "size": "medium",
                    }
                ],
            }
        ]

        for meeting_date in meeting_dates:
            date_val = urllib.parse.quote(f"{meeting_date.strftime('%m/%d/%Y')} 7:00 PM")
            absentee_member_names = ""
            if meeting_date_absentees:
                for absentee_task in meeting_date_absentees[meeting_date]:
                    absentee_member_name = weekly_meeting_planner.get_assigned_to_user(absentee_task).display_name
                    absentee_member_names = absentee_member_name + "\n"
            message_signup_sheet_absentee_body_cols.append(
                {
                    "type": "Column",
                    "width": "85px",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": f"{absentee_member_names}[Signup](https://forms.office.com/r/wjCgSjdbk6?\
r9ac7132bd52447e2b6bcd479a021b876=%22{date_val}%22&\
rc90e248ef4b146ecb89c31e0b4ca94c1=%22Absent%22)",
                            "wrap": "true",
                            "size": "medium",
                            "isMarkdown": "true",
                        },
                    ],
                },
            )
        message_signup_sheet_absentee_body["columns"] = message_signup_sheet_absentee_body_cols
        adaptive_card_message["body"].append(message_signup_sheet_absentee_body)
        message_footer = {
            "type": "Container",
            "items": [
                {
                    "type": "TextBlock",
                    "text": "If you have read the [Toastmasters promise](https://newhorizonsarizonaorg.sharepoint.com"
                    "/sites/NewHorizonsArizonaToastmastersClub/Shared%20Documents/Forms/AllItems.aspx?"
                    "id=%2Fsites%2FNewHorizonsArizonaToastmastersClub%2FShared%20Documents%2FGeneral%2F2023"
                    "ToastmastersPromise%2EPDF&parent=%2Fsites%2FNewHorizonsArizonaToastmastersClub"
                    "%2FShared%20Documents%2FGeneral&p=true&ct=1730320650666"
                    "&or=Teams%2DHL&ga=1&LOF=1) and are certain that you are going to "
                    "miss the meeting, please mark yourself as absent.",
                    "size": "medium",
                    "wrap": "true",
                    "isMarkdown": "true",
                },
                {
                    "type": "TextBlock",
                    "text": "Best Regards,",
                    "size": "medium",
                    "wrap": "true",
                    "isMarkdown": "true",
                },
                {
                    "type": "TextBlock",
                    "text": "NHTM Education Committee",
                    "size": "medium",
                    "wrap": "true",
                    "isMarkdown": "true",
                },
            ],
        }
        adaptive_card_message["body"].append(message_footer)
        return adaptive_card_message
