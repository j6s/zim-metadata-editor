from gi.repository import Gtk, Gdk, GLib

from ..model import MetadataModel


class KeyValueTableWidget(Gtk.Box):
    """Widget for editing key-value pairs. All data operations go through the model."""

    def __init__(self, model: MetadataModel):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL, spacing=0)

        self._model: MetadataModel = model

        self._build_ui()
        self._model.connect('changed', self._on_model_changed)

    def _build_ui(self) -> None:
        """Build the widget UI."""
        self._build_header_toolbar()

        # Create ListStore: key, value
        self.liststore = Gtk.ListStore(str, str)

        # Create TreeView
        self.treeview = Gtk.TreeView(model=self.liststore)
        self.treeview.set_headers_visible(True)
        self.treeview.set_enable_search(True)
        self.treeview.set_search_column(0)
        self.treeview.set_no_show_all(True)

        self.selection = self.treeview.get_selection()
        self.selection.set_mode(Gtk.SelectionMode.SINGLE)

        # Key column (editable)
        key_renderer = Gtk.CellRendererText()
        key_renderer.set_property('editable', True)
        key_renderer.connect('edited', self._on_key_edited)
        self._key_column = Gtk.TreeViewColumn('Header', key_renderer, text=0)
        self._key_column.set_resizable(True)
        self._key_column.set_min_width(80)
        self.treeview.append_column(self._key_column)

        # Value column (editable)
        value_renderer = Gtk.CellRendererText()
        value_renderer.set_property('editable', True)
        value_renderer.connect('edited', self._on_value_edited)
        self._value_column = Gtk.TreeViewColumn('Value', value_renderer, text=1)
        self._value_column.set_resizable(True)
        self._value_column.set_expand(True)
        self.treeview.append_column(self._value_column)

        self.pack_start(self.treeview, True, True, 0)

        # Info label for empty state
        self.info_label = Gtk.Label()
        self.info_label.set_markup('<i>No metadata. Click + to add.</i>')
        self.info_label.set_xalign(0.5)
        self.info_label.set_margin_top(8)
        self.info_label.set_margin_bottom(8)
        self.info_label.set_no_show_all(True)
        self.pack_start(self.info_label, False, False, 0)

        self.show_all()
        self._refresh_from_model()

    def _build_header_toolbar(self) -> None:
        """Build toolbar in header style (title + buttons on right)."""
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        header_box.set_margin_start(6)
        header_box.set_margin_end(6)
        header_box.set_margin_top(4)
        header_box.set_margin_bottom(4)

        header_label = Gtk.Label()
        header_label.set_markup('<b>Page Metadata</b>')
        header_label.set_xalign(0)
        header_box.pack_start(header_label, True, True, 0)

        add_button = Gtk.Button()
        add_button.set_image(Gtk.Image.new_from_icon_name(
            'list-add-symbolic', Gtk.IconSize.SMALL_TOOLBAR))
        add_button.set_tooltip_text('Add new header')
        add_button.set_relief(Gtk.ReliefStyle.NONE)
        add_button.connect('clicked', self._on_add_clicked)
        header_box.pack_end(add_button, False, False, 0)

        remove_button = Gtk.Button()
        remove_button.set_image(Gtk.Image.new_from_icon_name(
            'list-remove-symbolic', Gtk.IconSize.SMALL_TOOLBAR))
        remove_button.set_tooltip_text('Remove selected header')
        remove_button.set_relief(Gtk.ReliefStyle.NONE)
        remove_button.connect('clicked', self._on_remove_clicked)
        header_box.pack_end(remove_button, False, False, 0)

        self.pack_start(header_box, False, False, 0)

        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        self.pack_start(separator, False, False, 0)

    def _refresh_from_model(self) -> None:
        """Refresh the display from the model."""
        self.liststore.clear()
        for key, value in sorted(self._model.get_data().items()):
            self.liststore.append([key, str(value)])
        self._update_visibility()

    def _update_visibility(self) -> None:
        """Update visibility of components based on state."""
        has_items = len(self.liststore) > 0
        self.treeview.set_visible(has_items)
        self.info_label.set_visible(not has_items)

    def _on_model_changed(self, model) -> None:
        """Handle model changes."""
        self._refresh_from_model()

    def _on_key_edited(self, renderer, path: str, new_text: str) -> None:
        """Handle key edit - delegate to model."""
        tree_iter = self.liststore.get_iter(path)
        old_key = self.liststore.get_value(tree_iter, 0)
        if old_key != new_text:
            self._model.rename_key(old_key, new_text)

    def _on_value_edited(self, renderer, path: str, new_text: str) -> None:
        """Handle value edit - delegate to model."""
        tree_iter = self.liststore.get_iter(path)
        key = self.liststore.get_value(tree_iter, 0)
        self._model.set_value(key, new_text)

    def _on_add_clicked(self, button) -> None:
        """Handle add button - delegate to model."""
        new_key = self._model.add_key()
        # Find and select the new row for editing
        for i, row in enumerate(self.liststore):
            if row[0] == new_key:
                path = Gtk.TreePath.new_from_indices([i])
                self.treeview.set_cursor(path, self.treeview.get_column(0), True)
                break

    def _on_remove_clicked(self, button) -> None:
        """Handle remove button - delegate to model."""
        model, tree_iter = self.selection.get_selected()
        if tree_iter is not None:
            key = model.get_value(tree_iter, 0)
            self._model.remove_key(key)
