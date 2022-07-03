import PySimpleGUI as sg
import nssgui as nss

__all__ = ['VFSExplorerViewBS']

class VFSExplorerViewBS(nss.ge.VFSExplorerView):
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
        def event_remove(context):
            if not self.selection:
                return
            path = self.selection.get_path()
            root = self.vfs.find_root_entry(path)
            if path != root.get_path():
                context.event = self.keys['Exclude']
                return self.handle_event(context)
            else:
                self.vfs.remove(path)
            root.calc_ie()
            self.vfs_explorer.refresh_current_dir()
            self.deselect()
            self.push(context.window)

        # VFSExplorerViewBS

        @self.eventmethod(self.keys['Include'])
        def event_include(context):
            if not self.selection:
                return
            self.selection.include()
            root = self.vfs.find_root_entry(self.selection.get_path())
            root.calc_ie()
            self.push(context.window)

        @self.eventmethod(self.keys['Exclude'])
        def event_exclude(context):
            if not self.selection:
                return
            self.selection.exclude()
            path = self.selection.get_path()
            root = self.vfs.find_root_entry(path)
            if path == root.get_path():
                context.event = self.keys['Remove']
                return self.handle_event(context)
            root.calc_ie()
            self.push(context.window)
