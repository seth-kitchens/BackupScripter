import bs
from bs.script_data import ScriptDataBS
import nssgui as nss
import PySimpleGUI as sg
from bs.fs.vfs import VFSBS as VFS
from bs.info import window_manage_included as info

button_size = nss.sg.button_size

class WindowManageIncluded(nss.AbstractBlockingWindow):
    def __init__(self, script_data:ScriptDataBS, vfs_static:VFS) -> None:
        data = script_data.to_dict()
        self.vfs_static = vfs_static.clone()
        self.vfs_explorer = nss.VFSExplorer(self.vfs_static, data.copy())
        super().__init__('WindowManageIncluded', data)

    # Layout

    def get_layout(self):
        gem = self.gem
        frame_explorer = nss.sg.FrameColumn('Static Inclusion',
            layout=gem.layout(bs.el.VFSExplorerViewBS('IEExplorer', self.vfs_explorer)))
        frame_iepatterns = nss.sg.FrameColumn('Matching Groups', expand_x=True,
            layout=gem.layout(bs.el.MatchingGroupsList('MatchingGroupsList', self.vfs_static)))
        frame_system = nss.sg.FrameColumn('Window', expand_y=True, layout=[
            [sg.Button('Return', size=(12, 2), expand_x=True)],
            [sg.Button('Cancel', size=(12, 2), expand_x=True)],
            [nss.ge.Info(gem, info.window, bt='Info', header='Manage Included', sg_kwargs={'size': (16, 2)})],
            [sg.VPush()]
        ])
        layout = [
            [frame_explorer],
            [frame_iepatterns, frame_system],
            [sg.Sizer(0, 5)],
            [self.status_bar(nss.ge.StatusBar('StatusBar'))]
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
            if not nss.popups.confirm(context, 'Resolve up to here? This group and all before it will be processed into static inclusion.'):
                return
            self.vfs_static.process_matching_groups(mgs)
            mglist.remove_through_selection()
            self.gem.push_all(context.window)

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
            if not nss.popups.confirm(context, 'Resolve all? All groups will be processed into static inclusion.'):
                return
            self.vfs_static.process_matching_groups(mgs)
            mglist.remove_all()
            self.gem.push_all(context.window)
    
    # Data

    def save(self, data):
        super().save(data)
        vfsdata = self.vfs_static.calc_vfsdata()
        data['vfsdata_static'] = vfsdata
        data['IncludedItems'] = vfsdata.included_items
        data['ExcludedItems'] = vfsdata.excluded_items

    # Other

    class WindowPreviewMatchGroups(nss.AbstractBlockingWindow):
        def __init__(self, title, vfs_static, mgs) -> None:
            self.vfs_temp = VFS()
            self.vfs_temp.copy_from_vfs(vfs_static)
            self.vfs_temp.process_matching_groups(mgs)
            data = {}
            self.vfs_explorer = nss.VFSExplorer(self.vfs_temp, data)
            super().__init__(title, data)
        def get_layout(self):
            self.gem.add_ge(bs.el.VFSExplorerViewBS('TempExplorerView', self.vfs_explorer, read_only=True))
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
