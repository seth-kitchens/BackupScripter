import os
from pprint import pprint

import nssgui as nss
import PySimpleGUI as sg

from src.bs.create import create_script
from src.bs.fs.vfs import VFSBS as VFS
from src.bs.g import colors
from src.bs.info import window_main as info
from src.bs.windows.manage_included import WindowManageIncluded
from src.bs.script_data import ScriptDataBS


button_size = nss.sg.button_size


class WindowMain(nss.AbstractBlockingWindow):

    archive_exts = {
            'zip': '.zip',
            '7z': '.7z'
    }

    def __init__(self, script_data:ScriptDataBS, init_script=None) -> None:
        self.script_data:ScriptDataBS = script_data
        if init_script != None:
            self._load_script(init_script)
        sd_dict = script_data.to_dict()
        self.vfs_static = VFS(sd_dict['IncludedItems'], sd_dict['ExcludedItems'])
        self.vfs_final = self.vfs_static.clone()
        self.vfs_final.process_matching_groups_dict(sd_dict['MatchingGroupsList'])
        super().__init__('WindowMain', sd_dict)
    
    ### Window

    # Layout

    def get_layout(self):
        frame_script_file = nss.sg.FrameColumn('Script File', expand_x=True, layout=[
            self.row(nss.ge.Filename('ScriptFilename', 'Filename').sg_kwargs_name(expand_x=True)),
            self.row(nss.ge.Path('ScriptDestination', 'Destination').sg_kwargs_path(expand_x=True)),
            [
                sg.Button('Load Script', key='LoadScript', size=10),
                sg.Push(),
                sg.Button('Export Script', key='ExportScript', size=10),
                sg.Button('Export and Quit', key='ExportQuit', size=12)
            ]
        ])
        frame_backup_file = nss.sg.FrameColumn('Backup File', expand_x=True, layout=[
            self.row(nss.ge.Filename('BackupFilename', 'Filename').sg_kwargs_name(expand_x=True)),
            [
                *self.row(nss.ge.Input('BackupDatePostfix', 'Date Postfix').sg_kwargs_in(expand_x=True)),
                nss.ge.Info(self.gem, info.date_postfix)
            ],
            self.row(nss.ge.Path('BackupDestination', 'Destination').sg_kwargs_path(expand_x=True)),
            self.row(nss.ge.Dropdown('ArchiveFormat', 'Archive Format', list(WindowMain.archive_exts.keys()))),
            self.row(nss.ge.Radio('ArchiveMode', 'Archive Mode:', {'append': 'Append', 'compile': 'Compile'}))
        ])
        frame_backup_settings = nss.sg.FrameColumn('Backup Settings', expand_y=True, layout=[
            [
                *self.row(nss.ge.Input('MaxBackups', 'Max Backups', type='int', negative_invalid=True)),
                sg.Push(),
                nss.ge.Info(self.gem, info.backup_settings, '?')
            ],
            self.row(nss.ge.InputUnits('BackupRecentAge', 'Recent Age', nss.units.Time, nss.units.Time.DAY, store_as_degree=nss.units.Time.SECOND, negative_invalid=True)),
            self.row(nss.ge.InputUnits('BackupOldAge', 'Old Age', nss.units.Time, nss.units.Time.DAY, store_as_degree=nss.units.Time.SECOND, negative_invalid=True)),
            [self.sge(nss.ge.Checkbox('PullAgeFromPostfix', 'Pull Age From Filename'))],
            [sg.VPush()]
        ])
        column_included_labels = sg.Column(pad=0, layout=[
            [sg.Text('Total Folders')],
            [sg.Text('Total Files')]
        ])
        column_included_numbers = sg.Column(element_justification='center', pad=0, layout=[
            self.row(nss.ge.OutText('TotalFolders')),
            self.row(nss.ge.OutText('TotalFiles'))
        ])
        column_included = sg.Column(element_justification='left', pad=0, layout=[
            [sg.Text('Included', text_color=colors.header)],
            [column_included_labels, column_included_numbers],
            [sg.Column(pad=0, expand_x=True, layout=[[sg.Text('Size'), sg.Push(), *self.row(nss.ge.OutText('SizeIncluded'))]])]
        ])
        column_excluded_labels = sg.Column(pad=0, layout=[
            [sg.Text('Total Folders')],
            [sg.Text('Total Files')]
        ])
        column_excluded_numbers = sg.Column(element_justification='center', pad=0, layout=[
            self.row(nss.ge.OutText('TotalFoldersExcluded')),
            self.row(nss.ge.OutText('TotalFilesExcluded'))
        ])
        column_excluded = sg.Column(pad=0, expand_y=True, layout=[
            [sg.Text('Excluded', text_color=colors.header)],
            [column_excluded_labels, column_excluded_numbers],
            [sg.Column(pad=0, expand_x=True, layout=[[sg.Text('Size'), sg.Push(), *self.row(nss.ge.OutText('SizeExcluded'))]])]
        ])
        frame_ie = nss.sg.FrameColumn('To Backup', layout=[
            [
                column_included,
                sg.VSeparator(),
                column_excluded
            ],
            [sg.VPush()],
            [
                sg.Push(),
                *self.row(nss.ge.Radio('IENumbers', text=None, options={'final':'Final', 'static':'Static', 'both':'Static/Final'}).load_value('final')),
                sg.Push()
            ],
            [sg.Button('Manage Included', key='ManageIncluded', expand_x=True)]
        ])
        row_items = [
            frame_ie,
            frame_backup_settings
        ]
        system_button_size = 10
        row_system = [
            nss.ge.Info(self.gem, info.backup_scripter, 'Info', sg_kwargs={'size': system_button_size}),
            sg.Button('Set Defaults', key='SetDefaults', size=system_button_size),
            sg.Button('Load Defaults', key='LoadDefaults', size=system_button_size),
            sg.Push()
        ]
        layout = [
            #[sg.Menu(self.menubar.get_def())],
            [sg.Sizer(0, 2)],
            row_system,
            [frame_script_file],
            [frame_backup_file],
            [row_items],
            [sg.Sizer(0, 5)],
            [self.status_bar(nss.ge.StatusBar('StatusBar'))]
        ]
        return layout
    
    def define_menus(self):
        mb = self.menubar = nss.sg.MenuBar()
        mb.unlock()
        pass
        mb.lock()
    
    # Events

    def define_events(self):
        super().define_events()
        self.event_value_exit(sg.WIN_CLOSED)

        radio_button_keys = self.gem['IENumbers'].get_button_keys()
        @self.eventmethod(*radio_button_keys)
        def event_radio_ie_numbers(context:nss.WindowContext):
            self.gem['IENumbers'].pull(context.values)
            self.refresh_ie(context.window)
            self.gem['IENumbers'].push(context.window)

        @self.eventmethod('SetDefaults')
        def event_set_defaults(context:nss.WindowContext):
            self.update_status('Setting defaults...')
            self.pull(context.values)
            self.save(self.data)
            self.script_data.load_dict(self.data)
            self.script_data.save_to_file(save_all=True)
            self.update_status('Defaults set', 1.0, '', text_color=self.COLOR_STATUS_FADED)

        @self.eventmethod('LoadDefaults')
        def event_load_defaults(context:nss.WindowContext):
            self.update_status('Loading defaults...')
            self.script_data.load_save_file()
            self.load()
            self.push(context.window)
            self.update_status('Defaults loaded', 1.0, '', text_color=self.COLOR_STATUS_FADED)

        @self.eventmethod(self.gem['ArchiveFormat'].keys['Dropdown'])
        def event_compression_type_chosen(context:nss.WindowContext):
            selection = context.values[self.gem['ArchiveFormat'].keys['Dropdown']]
            archive_ext = WindowMain.archive_exts[selection]
            self.gem['BackupFilename'].update(context.window, extension=archive_ext)
            if selection == 'zip':
                self.gem['ArchiveMode'].disable_button(context.window, 'compile')
                if self.gem['ArchiveMode'].is_selected('compile'):
                    self.gem['ArchiveMode'].update(context.window, value='append')
            elif selection == '7z':
                self.gem['ArchiveMode'].enable_button(context.window, 'compile')
                self.gem['ArchiveMode'].update(context.window, value='compile')

        @self.eventmethod('ExportQuit')
        def event_export_quit(context:nss.WindowContext):
            self.pull(context.values)
            self.save(self.data)
            success = self.create_script(context, auto_close=True)
            return True if success else None
        
        @self.eventmethod('ExportScript')
        def event_export_script(context:nss.WindowContext):
            self.update_status('Exporting script...')
            self.pull(context.values)
            self.save(self.data)
            self.create_script(context, auto_close=False)
            self.update_status('Script exported', 1.0, '', text_color=self.COLOR_STATUS_FADED)
        
        @self.eventmethod('LoadScript')
        def event_load_script(context:nss.WindowContext):
            script_to_load = nss.sg.browse_file(context.window)
            if not script_to_load:
                return
            self.update_status('Loading script...')
            self._load_script(script_to_load)
            self.load()
            self.push(context.window)
            self.update_status('Script Loaded', 1.0, '', text_color=self.COLOR_STATUS_FADED)
        
        @self.eventmethod('CompressionSettings')
        def event_compression_settings(context:nss.WindowContext):
            pass

        @self.eventmethod('ManageIncluded')
        def event_manage_included(context:nss.WindowContext):
            self.script_data.load_dict(self.data)
            window_manage_included = WindowManageIncluded(self.script_data, self.vfs_static)
            rv = nss.WRC(window_manage_included.open(context))
            if rv.check_exit():
                return rv
            if not rv.check_success():
                return
            wmi_data = window_manage_included.get_data()
            self.script_data.load_dict(wmi_data)
            self.data.update(self.script_data.to_dict())
            self.vfs_static.copy_from_vfs(window_manage_included.vfs_static)
            self.vfs_final.copy_from_vfs(self.vfs_static)
            self.vfs_final.process_matching_groups_dict(self.data['MatchingGroupsList'])
            self.refresh_ie(context.window)

    # Data

    def save(self, data):
        super().save(data)
        data['IncludedItems'], data['ExcludedItems'] = self.vfs_static.make_ie_lists()

    def load(self, data=None):
        """data: defaults to self.script_data.to_dict() if None"""
        if data == None:
            data = self.script_data.to_dict()
        super().load(data)
        self.vfs_static.remove_all()
        self.vfs_static.build_from_ie_lists(data['IncludedItems'], data['ExcludedItems'])
        self.vfs_final.copy_from_vfs(self.vfs_static)
        self.vfs_final.process_matching_groups_dict(data['MatchingGroupsList'])

    def push(self, window):
        super().push(window)
        self.refresh_ie(window)

    def init_window(self, window):
        super().init_window(window)
        self.refresh_ie(window)
        archive_mode = self.gem['ArchiveMode']
        archive_mode.disable_button(window, 'compile')
        archive_mode.update(window, value='append')

    ### WindowMain

    def create_script(self, context:nss.WindowContext, auto_close=True):
        popup_title = 'Create Script'
        self.script_data.load_dict(self.data)
        popup_progress = nss.ProgressWindow('Progress', header='Creating Script')
        progress_function = popup_progress.get_progress_function()
        popup_progress.open(context)
        try:
            success = create_script(context, self.script_data, progress_function)
        except Exception as e:
            success = False
            nss.PopupBuilder().text(('Script Creation Failed!', 'Exception: ' + str(e))).title(popup_title).ok().open(context)
            raise e
        popup_progress.close(context)
        if success:
            popup = nss.PopupBuilder().text('Script Created Successfully').title(popup_title).ok()
            if auto_close:
                popup.auto_ok()
            popup.open(context)
        return success
    
    def _load_script(self, script):
        """Loads script into self.script_data"""
        self.script_data.load_pyz(script)
        name = os.path.basename(script)
        i = name.rfind('.')
        self.script_data.ScriptFilename = [name[:i], name[i:]]
        self.script_data.ScriptDestination = os.path.dirname(script)
    
    def refresh_ie(self, window):
        vfsdata_static = self.vfs_static.calc_vfsdata()
        vfsdata_final = self.vfs_final.calc_vfsdata()

        if_static = vfsdata_static.included_file_count
        iF_static = vfsdata_static.included_folder_count
        isz_static = nss.units.Bytes(vfsdata_static.included_size, nss.units.Bytes.B).get_best(1, 0.1)
        ef_static = vfsdata_static.excluded_file_count
        eF_static = vfsdata_static.excluded_folder_count
        esz_static = nss.units.Bytes(vfsdata_static.excluded_size, nss.units.Bytes.B).get_best(1, 0.1)

        if_final = vfsdata_final.included_file_count
        iF_final = vfsdata_final.included_folder_count
        isz_final = nss.units.Bytes(vfsdata_final.included_size, nss.units.Bytes.B).get_best(1, 0.1)
        ef_final = vfsdata_final.excluded_file_count
        eF_final = vfsdata_final.excluded_folder_count
        esz_final = nss.units.Bytes(vfsdata_final.excluded_size, nss.units.Bytes.B).get_best(1, 0.1)

        def sbs(a, b):
            return str(a) + ' / ' + str(b)
        
        mode = self.gem['IENumbers'].get_selected_value()
        if mode == 'static':
            inf = if_static
            iF = iF_static
            isz = isz_static
            ef = ef_static
            eF = eF_static
            esz = esz_static
        elif mode == 'final':
            inf = if_final
            iF = iF_final
            isz = isz_final
            ef = ef_final
            eF = eF_final
            esz = esz_final
        elif mode == 'both':
            inf = sbs(if_static, if_final)
            iF = sbs(iF_static, iF_final)
            isz = sbs(isz_static, isz_final)
            ef = sbs(ef_static, ef_final)
            eF = sbs(eF_static, eF_final)
            esz = sbs(esz_static, esz_final)

        window['OutTotalFiles'](inf)
        window['OutTotalFolders'](iF)
        window['OutSizeIncluded'](isz)

        window['OutTotalFilesExcluded'](ef)
        window['OutTotalFoldersExcluded'](eF)
        window['OutSizeExcluded'](esz)
