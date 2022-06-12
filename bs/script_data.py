from scriptlib.script_data import ScriptDataManager, ScriptVariable, ScriptDataGroup, ScriptMetadataGroup
from bs import g

class ScriptDataManagerBS(ScriptDataManager):
    def __init__(self, packfio=g.packfio, script_data_file:str|None=g.paths.files.script_data, read_only=False):
        super().__init__(packfio, script_data_file=script_data_file, read_only=read_only)
        SV = ScriptVariable
        
        self.define_variables([
            ScriptMetadataGroup('Script File', [
                SV('ScriptFileName', ['backup_script', '.pyz']),
                SV('ScriptDestination', '')
            ]),
            ScriptDataGroup('Backup File', [
                SV('BackupFileName', ['backup', '.zip'], info='fields: [name][ext]'),
                SV('BackupFileNameDate', '_YYYYMMDD_HHmm', info='Replaces any YYYY/MM/DD/HH/hh/mm/SV/UU in date field with date/time'),
                SV('BackupDestination', '')
            ]),
            ScriptDataGroup('Static Inclusion', [
                SV('IncludedItems', []),
                SV('ExcludedItems', [])
            ]),
            ScriptDataGroup('Compression', [
                SV('ArchiveType', '')
            ]),
            ScriptDataGroup('Backup Settings', [
                SV('MaxBackups', None),
                SV('BackupOldAge', None),
                SV('BackupRecentAge', None),
                SV('PullAgeFromPostfix', True)
            ]),
            ScriptDataGroup('Dynamic Inclusion', [
                SV('MatchingGroupsList', {})
            ])
        ])
        if self.script_data_file != None:
            self.load_save_file()
