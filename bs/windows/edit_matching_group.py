import PySimpleGUI as sg
import nssgui as nss

from bs.info import matching_groups_list as info
from bs.fs.matching_group import MatchingGroup
MG = MatchingGroup

class WindowEditMatchingGroups(nss.AbstractBlockingWindow):
    def __init__(self, title, data=None) -> None:
        super().__init__(title, data)
    
    # Layout

    def get_layout(self):
        gem = self.gem
        column_file_size = sg.Column(expand_x=True, element_justification='center', layout=[
            [sg.Text('Within Size (File)')],
            [sg.Sizer(0, 3)],
            gem.row(nss.el.InputUnits('max_file_size', 'Max', nss.units.Bytes, default_degree=nss.units.Bytes.MB, store_as_degree=nss.units.Bytes.B, negative_invalid=True)),
            gem.row(nss.el.InputUnits('min_file_size', 'Min', nss.units.Bytes, default_degree=nss.units.Bytes.MB, store_as_degree=nss.units.Bytes.B, negative_invalid=True))
        ])
        column_folder_size = sg.Column(expand_x=True, element_justification='center', layout=[
            [sg.Text('Within Size (Folder)')],
            [sg.Sizer(0, 3)],
            gem.row(nss.el.InputUnits('max_folder_size', 'Max', nss.units.Bytes, default_degree=nss.units.Bytes.MB, store_as_degree=nss.units.Bytes.B, negative_invalid=True)),
            gem.row(nss.el.InputUnits('min_folder_size', 'Min', nss.units.Bytes, default_degree=nss.units.Bytes.MB, store_as_degree=nss.units.Bytes.B, negative_invalid=True))
        ])
        column_total_size = sg.Column(expand_x=True, element_justification='center', layout=[
            [sg.Text('Total Size Diff')],
            [sg.Sizer(0, 3)],
            gem.row(nss.el.InputUnits('max_total_size_diff', 'Max', nss.units.Bytes, default_degree=nss.units.Bytes.MB, store_as_degree=nss.units.Bytes.B, negative_invalid=True)),
            gem.row(nss.el.InputUnits('min_total_size_diff', 'Min', nss.units.Bytes, default_degree=nss.units.Bytes.MB, store_as_degree=nss.units.Bytes.B, negative_invalid=True))
        ])
        column_backup_size_before = sg.Column(expand_x=True, element_justification='center', layout=[
            [sg.Text('Backup Size Before')],
            [sg.Sizer(0, 3)],
            gem.row(nss.el.InputUnits('max_backup_size_before', 'Max', nss.units.Bytes, default_degree=nss.units.Bytes.MB, store_as_degree=nss.units.Bytes.B, negative_invalid=True)),
            gem.row(nss.el.InputUnits('min_backup_size_before', 'Min', nss.units.Bytes, default_degree=nss.units.Bytes.MB, store_as_degree=nss.units.Bytes.B, negative_invalid=True))
        ])
        column_backup_size_after = sg.Column(expand_x=True, element_justification='center', layout=[
            [sg.Text('Backup Size After')],
            [sg.Sizer(0, 3)],
            gem.row(nss.el.InputUnits('max_backup_size_after', 'Max', nss.units.Bytes, default_degree=nss.units.Bytes.MB, store_as_degree=nss.units.Bytes.B, negative_invalid=True)),
            gem.row(nss.el.InputUnits('min_backup_size_after', 'Min', nss.units.Bytes, default_degree=nss.units.Bytes.MB, store_as_degree=nss.units.Bytes.B, negative_invalid=True))
        ])
        row_parent_folder_size = [
            sg.Text('Parent Folder Size:'),
            *gem.row(nss.el.InputUnits('max_parent_folder_size', 'Max', nss.units.Bytes, default_degree=nss.units.Bytes.MB, store_as_degree=nss.units.Bytes.B, negative_invalid=True)),
            sg.Sizer(5, 0),
            *gem.row(nss.el.InputUnits('min_parent_folder_size', 'Min', nss.units.Bytes, default_degree=nss.units.Bytes.MB, store_as_degree=nss.units.Bytes.B, negative_invalid=True))
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
                gem.sge(nss.el.Checkbox('apply_to_files', 'Files')),
                gem.sge(nss.el.Checkbox('apply_to_folders', 'Folders').sg_kwargs_checkbox(enable_events=True))
            ]
        ])
        frame_apply_if = sg.Frame('Apply If', expand_x=True, layout=[
            row_apply_to_size,
            [
                *gem.row(nss.el.StringContainer('Within paths:',
                    nss.el.TextList('within_paths', delim=';', strip=(' .', ' ')),
                    folder_browse=True, blank_invalid=True
                )),
                nss.el.Info(gem, 'If empty, applies to all included/excluded before this group.')
            ],
            [
                *gem.row(nss.el.StringContainer('Not within paths:',
                    nss.el.TextList('not_within_paths', delim=';', strip=(' .', ' ')), folder_browse=True, blank_invalid=True
                ))
            ],
            [
                *gem.row(nss.el.StringContainer('Has extensions:',
                    nss.el.TextList('apply_if_extensions', delim=',', strip=(' .', ' ')), blank_invalid=True
                ))
            ],
            [
                *gem.row(nss.el.StringContainer('Does not have extensions:',
                    nss.el.TextList('do_not_apply_if_extension', delim=',', strip=(' .', ' ')), blank_invalid=True
                ))
            ],
            row_parent_folder_size
        ])
        frame_apply_group_if = sg.Frame('Apply Group If', expand_x=True, layout=[
            row_apply_group_if_size
        ])
        frame_action = sg.Frame('Action', expand_x=True, layout=[
            gem.row(nss.el.Radio('ie_action', '', {'exclude':'Exclude', 'include':'Include'}))
        ])
        frame_pattern_options = sg.Frame('Pattern Options', expand_x=True, layout=[
            [
                gem.sge(nss.el.Checkbox('strip_extensions', 'Strip Extensions')),
                gem.sge(nss.el.Checkbox('whole_name', 'Match Whole Name'))
            ],
            [   
                gem.sge(nss.el.Checkbox('match_case', 'Match Case')),
                gem.sge(nss.el.Checkbox('use_regex', 'Use Regex')),
            ],
            [
                gem.sge(nss.el.Checkbox('match_all', 'Match All Patterns'))
            ]
        ])
        layout_patterns = [[sg.Column(gem.layout(nss.el.TextList('patterns', empty_text='None (Matches Any)', border='"')), expand_y=True)]]
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
                nss.el.Info(gem, info.window, bt='Info', sg_kwargs={'size': 10}), 
                sg.Push(),
                sg.OK(size=10),
                sg.Cancel(size=10)],
            [sg.Sizer(0, 5)],
            [self.status_bar(nss.el.StatusBar('StatusBar'))]
        ]
        return layout

    # Events

    def define_events(self):
        super().define_events()
        self.em.bool_events(['OK'], ['Cancel', sg.WIN_CLOSED])

    # Data

    def init_window(self, window):
        super().init_window(window)
        include_rb_key = self.gem['ie_action'].v_to_k['include']
        window[include_rb_key].update(disabled=True)

    # Other
