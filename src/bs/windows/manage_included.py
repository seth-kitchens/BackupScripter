import psgu
import PySimpleGUI as sg

from src.bs import elements as bs_ge
from src.bs.fs.vfs import VFSBS as VFS
from src.bs.info import window_manage_included as info
from src.bs.script_data import ScriptDataBS


button_size = psgu.sg.button_size


class WindowManageIncluded(psgu.AbstractBlockingWindow):

    def __init__(self, script_data:ScriptDataBS, vfs_static:VFS) -> None:
        data = script_data.to_dict()
        self.vfs_static = vfs_static.clone()
        self.vfs_explorer = psgu.VFSExplorer(self.vfs_static, data.copy())
        super().__init__('WindowManageIncluded', data)

    # Layout

    def get_layout(self):
        frame_explorer = psgu.sg.FrameColumn('Static Inclusion',
            layout=self.layout(bs_ge.VFSExplorerViewBS('IEExplorer', self.vfs_explorer)))
        frame_iepatterns = psgu.sg.FrameColumn('Matching Groups', expand_x=True,
            layout=self.layout(bs_ge.MatchingGroupsList('MatchingGroupsList', self.vfs_static)))
        frame_system = psgu.sg.FrameColumn('Window', expand_y=True, layout=[
            [sg.Button('Return', size=(12, 2), expand_x=True)],
            [sg.Button('Cancel', size=(12, 2), expand_x=True)],
            [psgu.ge.Info(self.gem, info.window, bt='Info', sg_kwargs={'size': (16, 2)})],
            [sg.VPush()]
        ])
        layout = [
            [frame_explorer],
            [frame_iepatterns, frame_system],
            [sg.Sizer(0, 5)],
            [self.status_bar(psgu.ge.StatusBar('StatusBar'))]
        ]
        return layout
    
    # Events

    def define_events(self):
        super().define_events()
        self.event_value_close_success('Return')
        self.event_value_close('Cancel')
        self.event_value_exit(sg.WIN_CLOSED)
    
        @self.eventmethod(self.gem['MatchingGroupsList'].keys['PreviewHere'])
        @self.eventmethod(self.gem['MatchingGroupsList'].key_rcm('ListboxItem', 'PreviewHere'))
        def event_preview_here(context):
            mglist = self.gem['MatchingGroupsList']
            mgs = mglist.get_through_selection().values()
            if not mgs:
                return
            self.preview_match_groups(context, mgs)

        @self.eventmethod(self.gem['MatchingGroupsList'].keys['ResolveHere'])
        @self.eventmethod(self.gem['MatchingGroupsList'].key_rcm('ListboxItem', 'ResolveHere'))
        def event_resolve_here(context):
            mglist = self.gem['MatchingGroupsList']
            mgs = mglist.get_through_selection().values()
            if not mgs:
                return
            if not psgu.popups.confirm(context, text='Resolve up to here?'
                    'This group and all before it will be processed into static inclusion.'):
                return
            self.update_status('Resolving matching groups...')
            self.vfs_static.process_matching_groups(mgs)
            mglist.remove_through_selection()
            self.gem.push_all(context.window)
            self.update_status('Matching groups resolved', 1.0, '',
                text_color=self.COLOR_STATUS_FADED)

        @self.eventmethod(self.gem['MatchingGroupsList'].keys['PreviewAll'])
        def event_preview_all(context):
            mglist = self.gem['MatchingGroupsList']
            mgs = mglist.get_dict().values()
            if not mgs:
                return
            self.preview_match_groups(context, mgs)

        @self.eventmethod(self.gem['MatchingGroupsList'].keys['ResolveAll'])
        def event_resolve_all(context):
            mglist = self.gem['MatchingGroupsList']
            mgs = mglist.get_dict().values()
            if not mgs:
                return
            if not psgu.popups.confirm(context, 'Resolve all?'
                    'All groups will be processed into static inclusion.'):
                return
            self.update_status('Resolving matching groups...')
            self.vfs_static.process_matching_groups(mgs)
            mglist.remove_all()
            self.gem.push_all(context.window)
            self.update_status('Matching groups resolved', 1.0, '',
                text_color=self.COLOR_STATUS_FADED)
    
    # Data

    def save(self, data):
        super().save(data)
        vfsdata = self.vfs_static.calc_vfsdata()
        data['vfsdata_static'] = vfsdata
        data['IncludedItems'] = vfsdata.included_items
        data['ExcludedItems'] = vfsdata.excluded_items

    # Other

    class WindowPreviewMatchGroups(psgu.AbstractBlockingWindow):

        def __init__(self, title, vfs_static, mgs) -> None:
            self.vfs_temp = VFS()
            self.vfs_temp.copy_from_vfs(vfs_static)
            self.vfs_temp.process_matching_groups(mgs)
            data = {}
            self.vfs_explorer = psgu.VFSExplorer(self.vfs_temp, data)
            super().__init__(title, data)

        def get_layout(self):
            self.gem.add_ge(bs_ge.VFSExplorerViewBS('TempExplorerView',
                self.vfs_explorer, read_only=True))
            column_explorer_view = sg.Column(self.gem['TempExplorerView'].get_layout())
            layout = [
                [column_explorer_view],
                [sg.HSeparator()],
                [sg.Push(), sg.OK(size=18), sg.Push()]
            ]
            return layout

        def define_events(self):
            super().define_events()
            self.event_value_close('OK', sg.WIN_CLOSED)

    def preview_match_groups(self, context, mgs):
        w = self.WindowPreviewMatchGroups('Preview', self.vfs_static, mgs)
        w.open(context)
