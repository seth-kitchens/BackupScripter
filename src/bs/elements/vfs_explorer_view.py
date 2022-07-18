import PySimpleGUI as sg

import psgu


__all__ = ['VFSExplorerViewBS']


class VFSExplorerViewBS(psgu.ge.VFSExplorerView):

    def __init__(self, object_id, vfs_explorer, read_only=False) -> None:
        super().__init__(object_id, vfs_explorer, read_only=read_only)

    ### GuiElement

    def _get_row_actions(self):
        row = super()._get_row_actions()
        row.append(sg.Button('Exclude', key=self.keys['Exclude'], size=10)),
        row.append(sg.Button('Include', key=self.keys['Include'], size=10))
        return row

    ### VFSExplorerView

    def define_events(self):
        super().define_events()
        if self.read_only:
            return

        @self.eventmethod(self.keys['Remove'])
        def event_remove(event_context:psgu.EventContext):
            if not self.selection:
                return
            path = self.selection.get_path()
            root = self.vfs.find_root_entry(path)
            if path != root.get_path():
                event_context.event = self.keys['Exclude']
                return self.handle_event(event_context)
            else:
                self.vfs.remove(path)
            root.calc_ie()
            self.vfs_explorer.refresh_current_dir()
            self.deselect()
            self.push(event_context.window_context.window)

        # VFSExplorerViewBS

        @self.eventmethod(self.keys['Include'])
        def event_include(event_context:psgu.EventContext):
            if not self.selection:
                return
            self.selection.include()
            root = self.vfs.find_root_entry(self.selection.get_path())
            root.calc_ie()
            self.push(event_context.window_context.window)

        @self.eventmethod(self.keys['Exclude'])
        def event_exclude(event_context:psgu.EventContext):
            if not self.selection:
                return
            self.selection.exclude()
            path = self.selection.get_path()
            root = self.vfs.find_root_entry(path)
            if path == root.get_path():
                event_context.event = self.keys['Remove']
                return self.handle_event(event_context)
            root.calc_ie()
            self.push(event_context.window_context.window)
