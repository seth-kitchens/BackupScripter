import PySimpleGUI as sg
import psgu
from psgu import ge, units

from src.bs.info import matching_groups_list as info
from src.bs.fs.matching_group import MatchingGroup
MG = MatchingGroup


class WindowEditMatchingGroups(psgu.AbstractBlockingWindow):

    def __init__(self, title, data=None) -> None:
        super().__init__(title, data)
    
    # Layout

    def get_layout(self):
        column_file_size = sg.Column(expand_x=True, element_justification='center', layout=[
            [sg.Text('Within Size (File)')],
            [sg.Sizer(0, 3)],
            self.row(ge.InputUnits('max_file_size', 'Max', units.Bytes,
                default_degree=units.Bytes.MB,
                store_as_degree=units.Bytes.B,
                negative_invalid=True)),
            self.row(ge.InputUnits('min_file_size', 'Min', units.Bytes,
                default_degree=units.Bytes.MB,
                store_as_degree=units.Bytes.B,
                negative_invalid=True))
        ])
        column_folder_size = sg.Column(expand_x=True, element_justification='center', layout=[
            [sg.Text('Within Size (Folder)')],
            [sg.Sizer(0, 3)],
            self.row(ge.InputUnits('max_folder_size', 'Max', units.Bytes,
                default_degree=units.Bytes.MB,
                store_as_degree=units.Bytes.B,
                negative_invalid=True)),
            self.row(ge.InputUnits('min_folder_size', 'Min', units.Bytes,
                default_degree=units.Bytes.MB,
                store_as_degree=units.Bytes.B,
                negative_invalid=True))
        ])
        column_total_size = sg.Column(expand_x=True, element_justification='center', layout=[
            [sg.Text('Total Size Diff')],
            [sg.Sizer(0, 3)],
            self.row(ge.InputUnits('max_total_size_diff', 'Max', units.Bytes,
                default_degree=units.Bytes.MB,
                store_as_degree=units.Bytes.B, 
                negative_invalid=True)),
            self.row(ge.InputUnits('min_total_size_diff', 'Min', units.Bytes,
                default_degree=units.Bytes.MB,
                store_as_degree=units.Bytes.B,
                negative_invalid=True))
        ])
        column_backup_size_before = sg.Column(expand_x=True, element_justification='center', layout=[
            [sg.Text('Backup Size Before')],
            [sg.Sizer(0, 3)],
            self.row(ge.InputUnits('max_backup_size_before', 'Max', units.Bytes, 
                default_degree=units.Bytes.MB,
                store_as_degree=units.Bytes.B,
                negative_invalid=True)),
            self.row(ge.InputUnits('min_backup_size_before', 'Min', units.Bytes,
                default_degree=units.Bytes.MB,
                store_as_degree=units.Bytes.B,
                negative_invalid=True))
        ])
        column_backup_size_after = sg.Column(expand_x=True, element_justification='center', layout=[
            [sg.Text('Backup Size After')],
            [sg.Sizer(0, 3)],
            self.row(ge.InputUnits('max_backup_size_after', 'Max', units.Bytes,
                default_degree=units.Bytes.MB,
                store_as_degree=units.Bytes.B, 
                negative_invalid=True)),
            self.row(ge.InputUnits('min_backup_size_after', 'Min', units.Bytes,
                default_degree=units.Bytes.MB,
                store_as_degree=units.Bytes.B,
                negative_invalid=True))
        ])
        row_parent_folder_size = [
            sg.Text('Parent Folder Size:'),
            *self.row(ge.InputUnits('max_parent_folder_size', 'Max', units.Bytes,
                default_degree=units.Bytes.MB,
                store_as_degree=units.Bytes.B,
                negative_invalid=True)),
            sg.Sizer(5, 0),
            *self.row(ge.InputUnits('min_parent_folder_size', 'Min', units.Bytes,
                default_degree=units.Bytes.MB,
                store_as_degree=units.Bytes.B,
                negative_invalid=True))
        ]
        row_apply_to_size = [
            sg.Push(),
            column_file_size,
            sg.Push(),
            column_folder_size,
            sg.Push(),
            sg.Sizer(200, 0)
        ]
        row_apply_group_if_size = [
            sg.Push(),
            column_backup_size_before,
            sg.Push(),
            column_backup_size_after,
            sg.Push(),
            column_total_size,
            sg.Push(),
        ]
        frame_apply_to = sg.Frame('Apply To', layout=[
            [
                self.sge(ge.Checkbox('apply_to_files', 'Files')),
                self.sge(ge.Checkbox('apply_to_folders', 'Folders') \
                    .sg_kwargs_checkbox(enable_events=True))
            ]
        ])
        frame_apply_if = sg.Frame('Apply If', expand_x=True, layout=[
            row_apply_to_size,
            [
                *self.row(
                    ge.StringContainer('Within paths:',
                        ge.TextList('within_paths',
                            delim=';',
                            strip=(' .', ' ')),
                        folder_browse=True,
                        blank_invalid=True)),
                ge.Info(self.gem, 'If empty, applies to all included/excluded before this group.')
            ],
            [
                *self.row(
                    ge.StringContainer('Not within paths:',
                        ge.TextList('not_within_paths',
                            delim=';', 
                            strip=(' .', ' ')),
                        folder_browse=True,
                        blank_invalid=True))
            ],
            [
                *self.row(
                    ge.StringContainer('Has extensions:',
                        ge.TextList('apply_if_extensions',
                            delim=',', 
                            strip=(' .', ' ')),
                        blank_invalid=True))
            ],
            [
                *self.row(
                    ge.StringContainer('Does not have extensions:',
                        ge.TextList('do_not_apply_if_extension',
                            delim=',',
                            strip=(' .', ' ')),
                        blank_invalid=True))
            ],
            row_parent_folder_size
        ])
        frame_apply_group_if = sg.Frame('Apply Group If', expand_x=True, layout=[
            row_apply_group_if_size
        ])
        frame_action = sg.Frame('Action', expand_x=True, layout=[
            self.row(ge.RadioGroup('ie_action', '', {'exclude':'Exclude', 'include':'Include'}))
        ])
        frame_pattern_options = sg.Frame('Pattern Options', expand_x=True, layout=[
            [
                self.sge(ge.Checkbox('strip_extensions', 'Strip Extensions')),
                self.sge(ge.Checkbox('whole_name', 'Match Whole Name'))
            ],
            [   
                self.sge(ge.Checkbox('match_case', 'Match Case')),
                self.sge(ge.Checkbox('use_regex', 'Use Regex')),
            ],
            [
                self.sge(ge.Checkbox('match_all', 'Match All Patterns'))
            ]
        ])
        layout_patterns = [
            [
                sg.Column(
                    layout=self.layout(
                        ge.TextList('patterns',
                            empty_text='None (Matches Any)', 
                            border='"')),
                    expand_y=True)
            ]
        ]
        frame_patterns = sg.Frame('Patterns', expand_x=True, expand_y=True, layout=layout_patterns)
        column_left = sg.Column(expand_y=True, layout=[
            [frame_action],
            [frame_pattern_options],
            [frame_patterns]
        ])
        column_right = sg.Column([
            [frame_apply_to],
            [frame_apply_if],
            [frame_apply_group_if]
        ])
        layout = [
            [column_left, column_right],
            [
                ge.Info(self.gem, info.window, bt='Info', sg_kwargs={'size': 10}), 
                sg.Push(),
                sg.OK(size=10),
                sg.Cancel(size=10)],
            [sg.Sizer(0, 5)],
            [self.status_bar(ge.StatusBar('StatusBar'))]
        ]
        return layout

    # Events

    def define_events(self):
        super().define_events()
        self.event_value_close_success('OK')
        self.event_value_close('Cancel')
        self.event_value_exit(sg.WIN_CLOSED)

    # Data

    def init_window_finalized(self, window:sg.Window):
        super().init_window_finalized(window)
        include_rb_key = self.gem['ie_action'].v_to_k['include']
        window[include_rb_key].update(disabled=True)
