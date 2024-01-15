from o365.excel.range_assignments import RangeAssignments

class RangeAssignmentsReverse(RangeAssignments):
    """This class is used for storing the reverse meeting range assignments"""

    range_assignments_map: dict = {
        "C3:D3": {
            "names": [["Meeting Day", "Meeting Date"]],  # C3,D3
            "values": [[None, None]],  # C3,D3
            "formats": [[None, "d-mmm-yy"]],  # C3,D3
            "formulas": [[None, None]],  # C3,D3
        },
        "G5:G40": {
            "names": [
                ["Presiding Officer"],  # G5
                [None],  # G6
                ["WOW"],  # G7
                ["GEM"],  # G8
                [None],  # G9
                ["Ballot Counter"],  # G10
                ["Toastmaster"],  # G11
                ["General Evaluator"],  # G12
                ["Grammarian"],  # G13
                ["Ah Counter"],  # G14
                ["Timer"],  # G15
                ["Manual Evaluator 3"],  # G16
                ["Manual Evaluator 2"],  # G17
                ["Manual Evaluator 1"],  # G18
                ["Toastmaster"],  # G19
                [None],  # G20
                ["Topics Master"],  # G21
                ["Speaker 3"],  # G22
                [None],  # G23
                ["Speaker 2"],  # G24
                [None],  # G25
                ["Speaker 1"],  # G26
                ["General Evaluator"],  # G27
                [None],  # G28
                ["Timer"],  # G29
                ["Ah Counter"],  # G30
                ["Manual Evaluator 3"],  # G31
                ["Manual Evaluator 2"],  # G32
                ["Manual Evaluator 1"],  # G33
                ["Grammarian"],  # G34
                ["Toastmaster"],  # G35
                [None],  # G36
                ["Joke Master"],  # G37
                [None],  # G38
                [None],  # G39
                ["Presiding Officer"],  # G40
            ],
            "values": [
                [None],  # G5
                [None],  # G6
                [None],  # G7
                [None],  # G8
                [None],  # G9
                [None],  # G10
                [None],  # G11
                [None],  # G12
                [None],  # G13
                [None],  # G14
                [None],  # G15
                [None],  # G16
                [None],  # G17
                [None],  # G18
                [None],  # G19
                [None],  # G20
                [None],  # G21
                [None],  # G22
                [None],  # G23
                [None],  # G24
                [None],  # G25
                [None],  # G26
                [None],  # G27
                [None],  # G28
                [None],  # G29
                [None],  # G30
                [None],  # G31
                [None],  # G32
                [None],  # G33
                [None],  # G34
                [None],  # G35
                [None],  # G36
                [None],  # G37
                [None],  # G38
                [None],  # G39
                [None],  # G40
            ],
            "formats": [
                [None],  # G5
                [None],  # G6
                [None],  # G7
                [None],  # G8
                [None],  # G9
                [None],  # G10
                [None],  # G11
                [None],  # G12
                [None],  # G13
                [None],  # G14
                [None],  # G15
                [None],  # G16
                [None],  # G17
                [None],  # G18
                [None],  # G19
                [None],  # G20
                [None],  # G21
                [None],  # G22
                [None],  # G23
                [None],  # G24
                [None],  # G25
                [None],  # G26
                [None],  # G27
                [None],  # G28
                [None],  # G29
                [None],  # G30
                [None],  # G31
                [None],  # G32
                [None],  # G33
                [None],  # G34
                [None],  # G35
                [None],  # G36
                [None],  # G37
                [None],  # G38
                [None],  # G39
                [None],  # G40
            ],
            "formulas": [
                ["=A5"],  # G5
                [None],  # G6
                [None],  # G7
                [None],  # G8
                [None],  # G9
                [None],  # G10
                [None],  # G11
                [None],  # G12
                [None],  # G13
                [None],  # G14
                [None],  # G15
                [None],  # G16
                [None],  # G17
                [None],  # G18
                ["=G11"],  # G19
                [None],  # G20
                [None],  # G21
                [None],  # G22
                [None],  # G23
                [None],  # G24
                ["=G9"],  # G25
                [None],  # G26
                ["=G12"],  # G27
                [None],  # G28
                ["=G15"],  # G29
                ["=G14"],  # G30
                ["=G16"],  # G31
                ["=G17"],  # G32
                ["=G18"],  # G33
                ["=G13"],  # G34
                ["=G11"],  # G35
                [None],  # G36
                [None],  # G37
                [None],  # G38
                [None],  # G39
                ["=G5"],  # G40
            ],
        },
    }

    def __init__(self) -> None:
        """initialize the reverse range assignments"""

    def populate_values(self, meeting_assignments: dict) -> None:
        """populate the meeting assignments"""
        super().populate_values(meeting_assignments)
        return self.range_assignments_map
