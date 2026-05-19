from gi.repository import Gtk

from zim.gui.widgets import WindowSidePaneWidget

from ..model import MetadataModel
from .key_value_table import KeyValueTableWidget

TITLE = 'Metadata'


class MetadataEditorWidget(Gtk.ScrolledWindow, WindowSidePaneWidget):
    """Sidebar widget for editing page metadata."""

    title = TITLE

    def __init__(self, model: MetadataModel):
        Gtk.ScrolledWindow.__init__(self)
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.set_shadow_type(Gtk.ShadowType.IN)

        self._model = model
        self._table = KeyValueTableWidget(model, toolbar_style='bottom')

        self.add(self._table)
        self._table.show_all()

        self._model.connect('changed', self._on_model_changed)

    def refresh(self) -> None:
        """Refresh the sidebar info display."""
        count = len(self._model.get_data())
        self.set_info(f'{count} {TITLE}')

    def _on_model_changed(self, model) -> None:
        """Update info when model changes."""
        self.refresh()
