class RangeAssignments:
    """This class is used for storing the meeting range assignments"""

    _range_assignments_map: dict = {
                                "C3": {
                                        "name": "Meeting Day",
                                        "value": "Tuesday",
                                        "format": "",
                                        "formula": "",
                                    },
                                "D3": {
                                        "name": "Meeting Date",
                                        "value": "",
                                        "format": "d-mmm-yy",
                                        "formula": "",
                                    },
                                "G5": {
                                        "name": "Presiding Officer",
                                        "value": "",
                                        "format": "",
                                        "formula": "=LEFT(A5, SEARCH(' ',A5,1)-1)",
                                    },
                                "G7": {
                                        "name": "Joke Master",
                                        "value": "",
                                        "format": "",
                                        "formula": "",
                                    },
                                "G8": {
                                        "name": "Toastmaster",
                                        "value": "",
                                        "format": "",
                                        "formula": "",
                                    },
                                "G9": {
                                        "name": "General Evaluator",
                                        "value": "",
                                        "format": "",
                                        "formula": "",
                                    },
                                "G11": {
                                        "name": "Grammarian",
                                        "value": "",
                                        "format": "",
                                        "formula": "",
                                    },
                                "G12": {
                                        "name": "Manual Evaluator 1",
                                        "value": "",
                                        "format": "",
                                        "formula": "",
                                    },
                                "G13": {
                                        "name": "Manual Evaluator 2",
                                        "value": "",
                                        "format": "",
                                        "formula": "",
                                    },
                                "G14": {
                                        "name": "Manual Evaluator 3",
                                        "value": "",
                                        "format": "",
                                        "formula": "",
                                    },
                                "G15": {
                                        "name": "Ah Counter",
                                        "value": "",
                                        "format": "",
                                        "formula": "",
                                    },
                                "G16": {
                                        "name": "Timer",
                                        "value": "",
                                        "format": "",
                                        "formula": "",
                                    },
                                "G17": {
                                        "name": "Speaker 1",
                                        "value": "",
                                        "format": "",
                                        "formula": "",
                                    },
                                "G19": {
                                        "name": "Speaker 2",
                                        "value": "",
                                        "format": "",
                                        "formula": "",
                                    },
                                "G21": {
                                        "name": "Speaker 3",
                                        "value": "",
                                        "format": "",
                                        "formula": "",
                                    },
                                "G22": {
                                        "name": "Topics Master",
                                        "value": "",
                                        "format": "",
                                        "formula": "",
                                    },
                                "G25": {
                                        "name": "General Evaluator",
                                        "value": "",
                                        "format": "",
                                        "formula": "=G9",
                                    },
                                "G27": {
                                        "name": "Manual Evaluator 1",
                                        "value": "",
                                        "format": "",
                                        "formula": "=G12",
                                    },
                                "G28": {
                                        "name": "Manual Evaluator 2",
                                        "value": "",
                                        "format": "",
                                        "formula": "=G13",
                                    },
                                "G29": {
                                        "name": "Manual Evaluator 3",
                                        "value": "",
                                        "format": "",
                                        "formula": "=G14",
                                    },
                                "G30": {
                                        "name": "Ballot Counter",
                                        "value": "",
                                        "format": "",
                                        "formula": "",
                                    },
                                "G31": {
                                        "name": "Timer",
                                        "value": "",
                                        "format": "",
                                        "formula": "=G16",
                                    },
                                "G32": {
                                        "name": "Ah Counter",
                                        "value": "",
                                        "format": "",
                                        "formula": "=G15",
                                    },
                                "G33": {
                                        "name": "Grammarian",
                                        "value": "",
                                        "format": "",
                                        "formula": "=G11",
                                    },
                                "G34": {
                                        "name": "General Evaluator",
                                        "value": "",
                                        "format": "",
                                        "formula": "=G9",
                                    },
                                "G35": {
                                        "name": "Toastmaster",
                                        "value": "",
                                        "format": "",
                                        "formula": "=G8",
                                    },
                                "G37": {
                                        "name": "GEM",
                                        "value": "",
                                        "format": "",
                                        "formula": "",
                                    },
                                "G38": {
                                        "name": "WOW",
                                        "value": "",
                                        "format": "",
                                        "formula": "",
                                    },
                                "G41": {
                                        "name": "Presiding Officer",
                                        "value": "",
                                        "format": "",
                                        "formula": "=G5",
                                    }
                                }
    
    def __init__(self, meeting_date) -> None:
        """initialize the range assignments"""
        self._range_assignments_map['D3']['value'] = meeting_date

    def populate_values(self, meeting_assignments: dict) -> None:
        """populate the meeting assignments"""
        for meeting_assignment_key, meeting_assignment_value in meeting_assignments.items():
            for range_assignment_value in self._range_assignments_map.values():
                if range_assignment_value['name'] in meeting_assignment_key:
                    range_assignment_value['value'] = meeting_assignment_value
                    break
                
        return self._range_assignments_map
    
