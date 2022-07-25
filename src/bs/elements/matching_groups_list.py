import PySimpleGUI as sg
import psgu

from src.bs.elements import DetailListBS
from src.bs.windows.edit_matching_group import WindowEditMatchingGroups
from src.bs.fs.matching_group import MatchingGroup


__all__ = ['MatchingGroupsList']


class MatchingGroupsList(DetailListBS):

    def __init__(self, object_id, vfs):
        super().__init__(object_id)

    ### DetailList

    def make_details(self, item, data:MatchingGroup):
        mg = data
        if mg == None:
            return psgu.FormatText('No Data')        
        mg.make_invalid_none()
        d = mg.d
        highlights = {
            'green': '#aaffaa',
            'blue': '#bbbbff',
            'purple': '#dfbbff'
        }
        colors_var = ('black', highlights['green'])
        colors_bad = ('black', 'orange')
        colors_alert = ('black', 'yellow')
        colors_pattern = ('black', highlights['blue'])
        colors_cond = ('black', highlights['purple'])

        format_text = psgu.FormatText()
        def ft_text(s):    format_text.append(s)
        def ft_var(s):     format_text.color(s, *colors_var)
        def ft_bad(s):     format_text.color(s, *colors_bad)
        def ft_pattern(s): format_text.color(s, *colors_pattern)
        def ft_cond(s):    format_text.color(s, *colors_cond)
        def ft_alert(s):   format_text.color(s, *colors_alert)
        
        cond_f_sz = cond_F_sz = cond_pF_sz = cond_apply_if = False
        if d.apply_to_files and (d.min_file_size or d.max_file_size):
            cond_f_sz = True
        if d.apply_to_folders and (d.min_folder_size or d.max_folder_size):
            cond_F_sz = True
        if d.min_parent_folder_size or d.max_parent_folder_size:
            cond_pF_sz = True
        if cond_f_sz or cond_F_sz or cond_pF_sz:
            cond_apply_if = True
        
        cond_bsb = cond_bsa = cond_tsd = cond_apply_group_if = False
        if d.min_backup_size_before or d.max_backup_size_before:
            cond_bsb = True
        if d.min_backup_size_after or d.max_backup_size_after:
            cond_bsa = True
        if d.min_total_size_diff or d.max_total_size_diff:
            cond_tsd = True
        if cond_bsb or cond_bsa or cond_tsd:
            cond_apply_group_if = True
        
        has_cond = False
        if d.patterns or cond_apply_if or cond_apply_group_if:
            has_cond = True
        elif d.within_paths or d.not_within_paths:
            has_cond = True
        elif d.apply_if_extensions or d.do_not_apply_if_extensions:
            has_cond = True
        

        s_ie_action = '[' + d.ie_action.capitalize() + ']'
        ft_var(s_ie_action)
        ft_text(' ')

        if d.apply_to_files and d.apply_to_folders:
            if not has_cond:
                ft_bad('[All]')
                return format_text
            s_types = 'Files/Folders'
        elif d.apply_to_files:
            if not has_cond:
                ft_bad('[All Files]')
                return format_text
            s_types = 'Files'
        elif d.apply_to_folders:
            if not has_cond:
                ft_bad('[All Folders]')
                return format_text
            s_types = 'Folders'
        else:
            ft_bad('[None]')
            return format_text

        s = '['
        if d.apply_to_files:
            s += 'Files'
            if d.apply_to_folders:
                s += ', '
        ft_var(s)
        s = ''
        if d.apply_to_folders:
            s += 'Folders'
            if not d.apply_recursive:
                s += ' (NR)'
        if d.apply_if_extensions or d.do_not_apply_if_extensions:
            ft_bad(s)
            ft_var(']')
        else:
            ft_var(s + ']')
        
        if d.within_paths:
            ft_text(' from paths ')
            ft_var('[' + ', '.join(['"' + p + '"' for p in d.within_paths]) + ']')
        else:
            ft_text(' from ')
            ft_var('[Included]')
        if d.not_within_paths:
            ft_text(' and not within paths ')
            ft_var('[' + ', '.join(['"' + p + '"' for p in d.not_within_paths]) + ']')

        if d.apply_if_extensions or d.do_not_apply_if_extensions:
            ft_text(' ')
        if d.apply_if_extensions:
            s1 = 'if any of extensions '
            s2 = '[' + ', '.join(d.apply_if_extensions) + ']'
            if d.do_not_apply_if_extensions or d.apply_to_folders:
                ft_bad(s1 + s2)
            else:
                ft_text(s1)
                ft_var(s2)
        if d.do_not_apply_if_extensions:
            s1 = 'not any of extensions '
            s2 = '[' + ', '.join(d.do_not_apply_if_extensions) + ']'
            if d.apply_if_extensions:
                ft_bad(' but ' + s1 + s2)
            elif d.apply_to_folders:
                ft_bad('if ' + s1 + s2)
            else:
                ft_text('if ' + s1)
                ft_var(s2)

        if d.patterns:
            ft_text('. Matches names with ')
            if d.match_all:
                ft_var('[All]')
            else:
                ft_var('[Any]')
            ft_text(' of ')
            if d.use_regex:
                ft_var('[Regex]')
            else:
                ft_var('[Text]')
            ft_text(' patterns below, with conditions ')
            s = '[Match Case' if d.match_case else '[Match Case'
            s += ', Whole ' if d.whole_name else ', In '
            s += 'Name (Stripped)]' if d.strip_extensions else 'Name]'
            ft_var(s)
            s_indent = '\n  '
            for pattern in ['"' + p + '"' for p in d.patterns]:
                ft_text(s_indent)
                ft_pattern(pattern)

        def below_size(a):
            ft_cond('[Below ' + psgu.units.Bytes(a, psgu.units.Bytes.B).get_best() + ']')
        
        def above_size(a):
            ft_cond('[Above ' + psgu.units.Bytes(a, psgu.units.Bytes.B).get_best() + ']')
        
        def within_size(a, b):
            if not (a or b):
                return
            if not a:
                return below_size(b)
            if not b:
                return above_size(a)
            s = '[Between '
            s += psgu.units.Bytes(a, psgu.units.Bytes.B).get_best(decimal_digits=1, minimum=0.5)
            s += ' and '
            s += psgu.units.Bytes(b, psgu.units.Bytes.B).get_best(decimal_digits=1, minimum=0.5)
            s += ']'
            if a < b:
                ft_cond(s)
            else:
                ft_bad(s)
        
        if cond_apply_if:
            ft_text('\nApply to:')
        if cond_f_sz or (cond_F_sz and d.apply_to_files):
            if cond_f_sz:
                ft_text('\n  Files ')
                within_size(d.min_file_size, d.max_file_size)
            else:
                ft_text('\n  Files of any size.')
        if cond_F_sz or (cond_f_sz and d.apply_to_folders):
            if cond_F_sz:
                ft_text('\n  Folders ')
                within_size(d.min_folder_size, d.max_folder_size)
            else:
                ft_text('\n  Folders of any size')
        if cond_pF_sz:
            ft_text('\n  ' + s_types + ' within folders ')
            within_size(d.min_parent_folder_size, d.max_parent_folder_size)
        
        if cond_apply_group_if:
            ft_text('\nApply Group If:')
        if cond_bsb:
            ft_text('\n  Included size before ')
            within_size(d.min_backup_size_before, d.max_backup_size_before)
        if cond_bsa:
            ft_text('\n  Included size after ')
            within_size(d.min_backup_size_after, d.max_backup_size_after)
        if cond_tsd:
            ft_text('\n  Included size change ')
            within_size(d.min_total_size_diff, d.max_total_size_diff)
        return format_text
    
    def edit_data(self, window_context:psgu.WindowContext, item, data):
        mg = data if data != None else MatchingGroup()
        window_edit_matching_groups = WindowEditMatchingGroups(
            'Matching Group "' + item + '"', mg.to_dict())
        rv = psgu.WRC(window_edit_matching_groups.open(window_context))
        if rv.check_success():
            mg.load_dict(window_edit_matching_groups.get_data())
            return rv, mg
        return rv, data

    def pack_data(self, data):
        mg = data if data != None else MatchingGroup()
        return mg.to_dict()
    
    def unpack_data(self, packed_data):
        if not packed_data:
            return MatchingGroup()
        return MatchingGroup.from_dict(packed_data)

