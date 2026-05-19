from gi.repository import Gtk

from zim.gui.insertedobjects import InsertedObjectWidget

from ..model import MetadataModel
from .key_value_table import KeyValueTableWidget


class MetadataBlockWidget(InsertedObjectWidget):
    """Insertable block widget for editing page metadata inline."""

    def __init__(self, model: MetadataModel):
        InsertedObjectWidget.__init__(self)
        self._model = model
        self._build_ui()

    def _build_ui(self) -> None:
        """Build the widget UI."""
        frame = Gtk.Frame()
        frame.set_shadow_type(Gtk.ShadowType.ETCHED_IN)

        self._table = KeyValueTableWidget(self._model, toolbar_style='header')

        frame.add(self._table)
        self.add(frame)
        self.show_all()
