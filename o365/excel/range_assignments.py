class RangeAssignments:
    """This class is used for storing the meeting range assignments"""

    range_assignments_map: dict = {
        "C3:D3": {
            "names": [["Meeting Day", "Meeting Date"]],  # C3,D3
            "values": [[None, None]],  # C3,D3
            "formats": [[None, "d-mmm-yy"]],  # C3,D3
            "formulas": [[None, None]],  # C3,D3
        },
        "G5:G41": {
            "names": [
                ["Presiding Officer"],  # G5
                [None],  # G6
                ["Joke Master"],  # G7
                ["Toastmaster"],  # G8
                ["General Evaluator"],  # G9
                [None],  # G10
                ["Grammarian"],  # G11
                ["Manual Evaluator 1"],  # G12
                ["Manual Evaluator 2"],  # G13
                ["Manual Evaluator 3"],  # G14
                ["Ah Counter"],  # G15
                ["Timer"],  # G16
                ["Speaker 1"],  # G17
                [None],  # G18
                ["Speaker 2"],  # G19
                [None],  # G20
                ["Speaker 3"],  # G21
                ["Topics Master"],  # G22
                [None],  # G23
                [None],  # G24
                ["General Evaluator"],  # G25
                [None],  # G26
                ["Manual Evaluator 1"],  # G27
                ["Manual Evaluator 2"],  # G28
                ["Manual Evaluator 3"],  # G29
                ["Ballot Counter"],  # G30
                ["Timer"],  # G31
                ["Ah Counter"],  # G32
                ["Grammarian"],  # G33
                ["General Evaluator"],  # G34
                ["Toastmaster"],  # G35
                [None],  # G36
                ["GEM"],  # G37
                ["WOW"],  # G38
                [None],  # G39
                [None],  # G40
                ["Presiding Officer"],  # G41
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
                [None],  # G41
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
                [None],  # G41
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
                [None],  # G19
                [None],  # G20
                [None],  # G21
                [None],  # G22
                [None],  # G23
                [None],  # G24
                ["=G9"],  # G25
                [None],  # G26
                ["=G12"],  # G27
                ["=G13"],  # G28
                ["=G14"],  # G29
                [None],  # G30
                ["=G16"],  # G31
                ["=G15"],  # G32
                ["=G11"],  # G33
                ["=G9"],  # G34
                ["=G8"],  # G35
                [None],  # G36
                [None],  # G37
                [None],  # G38
                [None],  # G39
                [None],  # G40
                ["=G5"],  # G41
            ],
        },
    }

    def __init__(self) -> None:
        """initialize the range assignments"""

    def populate_values(self, meeting_assignments: dict) -> None:
        """populate the meeting assignments"""
        for (
            meeting_assignment_key,
            meeting_assignment_value,
        ) in meeting_assignments.items():
            value_populated: bool = False
            for range_assignment_value_map in self.range_assignments_map.values():
                value_row_idx: int = 0
                for range_assignment_value_row_values in range_assignment_value_map["names"]:
                    value_column_idx: int = 0
                    for range_assignment_value_col_value in range_assignment_value_row_values:
                        if (
                            range_assignment_value_map["formulas"][value_row_idx][value_column_idx] == None
                            and meeting_assignment_key == range_assignment_value_col_value
                        ):
                            range_assignment_value_map["values"][value_row_idx][
                                value_column_idx
                            ] = meeting_assignment_value
                            value_populated = True
                        value_column_idx += 1
                    if value_populated:
                        break
                    value_row_idx += 1
                if value_populated:
                    break

        return self.range_assignments_map
