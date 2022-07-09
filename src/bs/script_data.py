import sys
from dataclasses import dataclass

from src.scriptlib.script_data import *
from src.bs import g


class ScriptDataBS(ScriptData):

    def __init__(self, packfio=g.packfio, data_file=g.paths.rel.files.script_data):
        super().__init__(packfio=packfio, data_file=data_file)
        
        # Script Variables

        # Script File
        self._ScriptFilename = ScriptMetadata('ScriptFilename', ['backup_script', '.pyz'])
        self._ScriptDestination = ScriptMetadata('ScriptDestination', '')

        # Backup File
        self._BackupFilename = ScriptVariable('BackupFilename', ['backup', '.zip'], info='fields: [name][ext]')
        self._BackupDatePostfix = ScriptVariable('BackupDatePostfix', '_YYYYMMDD_HHmm', info='Replaces any YYYY/MM/DD/HH/hh/mm/SV/UU in date field with date/time')
        self._BackupDestination = ScriptVariable('BackupDestination', '')
        
        # Static Inclusion
        self._IncludedItems = ScriptVariable('IncludedItems', [])
        self._ExcludedItems = ScriptVariable('ExcludedItems', [])
        
        # Archive
        self._ArchiveFormat = ScriptVariable('ArchiveFormat', 'zip')
        self._ArchiveMode = ScriptVariable('ArchiveMode', 'append', info='compile | append')
        
        # Backup Settings
        self._MaxBackups = ScriptVariable('MaxBackups', None)
        self._BackupOldAge = ScriptVariable('BackupOldAge', None)
        self._BackupRecentAge = ScriptVariable('BackupRecentAge', None)
        self._PullAgeFromPostfix = ScriptVariable('PullAgeFromPostfix', True)

        # Dynamic Inclusion
        self._MatchingGroupsList = ScriptVariable('MatchingGroupsList', {})    

    def _getScriptFilename(self): return self._ScriptFilename.get()
    def _setScriptFilename(self, value): self._ScriptFilename.set(value)
    ScriptFilename:list[str] = property(fget=_getScriptFilename, fset=_setScriptFilename)

    def _getScriptDestination(self): return self._ScriptDestination.get()
    def _setScriptDestination(self, value): self._ScriptDestination.set(value)
    ScriptDestination:str = property(fget=_getScriptDestination, fset=_setScriptDestination)

    def _getBackupFilename(self): return self._BackupFilename.get()
    def _setBackupFilename(self, value): self._BackupFilename.set(value)
    BackupFilename:list[str] = property(fget=_getBackupFilename, fset=_setBackupFilename)

    def _getBackupDatePostfix(self): return self._BackupDatePostfix.get()
    def _setBackupDatePostfix(self, value): self._BackupDatePostfix.set(value)
    BackupDatePostfix:str = property(fget=_getBackupDatePostfix, fset=_setBackupDatePostfix)

    def _getBackupDestination(self): return self._BackupDestination.get()
    def _setBackupDestination(self, value): self._BackupDestination.set(value)
    BackupDestination:str = property(fget=_getBackupDestination, fset=_setBackupDestination)

    def _getIncludedItems(self): return self._IncludedItems.get()
    def _setIncludedItems(self, value): self._IncludedItems.set(value)
    IncludedItems:list[str] = property(fget=_getIncludedItems, fset=_setIncludedItems)

    def _getExcludedItems(self): return self._ExcludedItems.get()
    def _setExcludedItems(self, value): self._ExcludedItems.set(value)
    ExcludedItems:list[str] = property(fget=_getExcludedItems, fset=_setExcludedItems)

    def _getArchiveFormat(self): return self._ArchiveFormat.get()
    def _setArchiveFormat(self, value): self._ArchiveFormat.set(value)
    ArchiveFormat:str = property(fget=_getArchiveFormat, fset=_setArchiveFormat)

    def _getArchiveMode(self): return self._ArchiveMode.get()
    def _setArchiveMode(self, value): self._ArchiveMode.set(value)
    ArchiveMode:str = property(fget=_getArchiveMode, fset=_setArchiveMode)

    def _getMaxBackups(self): return self._MaxBackups.get()
    def _setMaxBackups(self, value): self._MaxBackups.set(value)
    MaxBackups:int|None = property(fget=_getMaxBackups, fset=_setMaxBackups)

    def _getBackupOldAge(self): return self._BackupOldAge.get()
    def _setBackupOldAge(self, value): self._BackupOldAge.set(value)
    BackupOldAge:int|None = property(fget=_getBackupOldAge, fset=_setBackupOldAge)

    def _getBackupRecentAge(self): return self._BackupRecentAge.get()
    def _setBackupRecentAge(self, value): self._BackupRecentAge.set(value)
    BackupRecentAge:int|None = property(fget=_getBackupRecentAge, fset=_setBackupRecentAge)

    def _getPullAgeFromPostfix(self): return self._PullAgeFromPostfix.get()
    def _setPullAgeFromPostfix(self, value): self._PullAgeFromPostfix.set(value)
    PullAgeFromPostfix:bool = property(fget=_getPullAgeFromPostfix, fset=_setPullAgeFromPostfix)

    def _getMatchingGroupsList(self): return self._MatchingGroupsList.get()
    def _setMatchingGroupsList(self, value): self._MatchingGroupsList.set(value)
    MatchingGroupsList:list = property(fget=_getMatchingGroupsList, fset=_setMatchingGroupsList)

    def make_load_pyz_command(self, path, comm_file):
        command = '{} "{}" {} {}'.format(sys.executable, path, '--getdata', comm_file)
        return command

    def fetch_comm_file(self):
        return g.cli.getdata_file()
