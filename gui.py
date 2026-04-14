import logging
import typing

from gi.repository import Gtk

from zim.gui.pageview import PageView
from zim.gui.widgets import WindowSidePaneWidget
from zim.notebook import Page

from .metadata_handler import MetadataHandler

logger = logging.getLogger('zim.plugins.dataview')


try:
    from zim.i18n import _
except ImportError:
    _ = lambda x: x

TITLE = 'Metadata'

class MetadataEditorWidget(Gtk.ScrolledWindow, WindowSidePaneWidget):
    title = TITLE

    def __init__(self, pageview: PageView, metadata_handler: MetadataHandler):
        Gtk.ScrolledWindow.__init__(self)
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.set_shadow_type(Gtk.ShadowType.IN)

        self._pageview: PageView = pageview
        self._current_page: typing.Optional[Page] = None
        self._headers: dict[str, str] = {}
        self._metadata_handler: MetadataHandler = metadata_handler

        self._build_ui()

    def _build_ui(self) -> None:
        """Build the widget UI."""
        # Main container box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        # Create ListStore: key, value
        self.liststore = Gtk.ListStore(str, str)

        # Create TreeView
        self.treeview = Gtk.TreeView(model=self.liststore)
        self.treeview.set_headers_visible(True)
        self.treeview.set_enable_search(True)
        self.treeview.set_search_column(0)

        # Selection
        self.selection = self.treeview.get_selection()
        self.selection.set_mode(Gtk.SelectionMode.SINGLE)

        # Key column (editable)
        key_renderer = Gtk.CellRendererText()
        key_renderer.set_property('editable', True)
        key_renderer.connect('edited', self._on_key_edited)
        key_column = Gtk.TreeViewColumn('Header', key_renderer, text=0)
        key_column.set_resizable(True)
        key_column.set_min_width(80)
        self.treeview.append_column(key_column)

        # Value column (editable)
        value_renderer = Gtk.CellRendererText()
        value_renderer.set_property('editable', True)
        value_renderer.connect('edited', self._on_value_edited)
        value_column = Gtk.TreeViewColumn('Value', value_renderer, text=1)
        value_column.set_resizable(True)
        value_column.set_expand(True)
        self.treeview.append_column(value_column)

        main_box.pack_start(self.treeview, True, True, 0)

        # Toolbar with add/remove buttons
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        toolbar.set_margin_top(4)
        toolbar.set_margin_start(4)
        toolbar.set_margin_end(4)
        toolbar.set_margin_bottom(4)

        add_button = Gtk.Button()
        add_button.set_image(Gtk.Image.new_from_icon_name(
            'list-add-symbolic', Gtk.IconSize.BUTTON))
        add_button.set_tooltip_text('Add new header')
        add_button.connect('clicked', self._on_add_clicked)
        toolbar.pack_start(add_button, False, False, 0)

        remove_button = Gtk.Button()
        remove_button.set_image(Gtk.Image.new_from_icon_name(
            'list-remove-symbolic', Gtk.IconSize.BUTTON))
        remove_button.set_tooltip_text('Remove selected header')
        remove_button.connect('clicked', self._on_remove_clicked)
        toolbar.pack_start(remove_button, False, False, 0)

        main_box.pack_start(toolbar, False, False, 0)

        # Info label for empty state
        self.info_label = Gtk.Label()
        self.info_label.set_markup('<i>Click + to add metadata</i>')
        self.info_label.set_xalign(0.5)
        self.info_label.set_margin_top(8)
        self.info_label.set_margin_bottom(8)
        main_box.pack_start(self.info_label, False, False, 0)

        # Add main box to scrolled window
        self.add(main_box)
        main_box.show_all()
        self._update_infotext()

    def load_page(self, page: Page) -> None:
        logger.debug(f'Loading metadata for {page.name}')
        logger.debug(vars(page))

        """Load metadata from a page."""
        self._current_page = page
        self._headers = self._metadata_handler.read(page)
        self.set_info(f'{len(self._headers)} {TITLE}')

        # Refresh liststore
        self.liststore.clear()
        for key, value in sorted(self._headers.items()):
            self.liststore.append([key, str(value)])

        self._update_infotext()

    def _update_infotext(self) -> None:
        """Update visibility of components based on state."""
        has_page = self._current_page is not None
        has_headers = len(self.liststore) > 0

        self.treeview.set_visible(has_page)
        self.info_label.set_visible(not has_page or not has_headers)

        if not has_page:
            self.info_label.set_markup('<i>No page loaded</i>')
        elif not has_headers:
            self.info_label.set_markup(
                '<i>No metadata headers.\nClick + to add one.</i>'
            )

    def _on_key_edited(self, renderer: Gtk.CellRendererText, path: str, new_text: str) -> None:
        iter = self.liststore.get_iter(path)
        old_key = self.liststore.get_value(iter, 0)

        value = self._headers.pop(old_key, '')
        new_key = self._get_unique_key(new_text)
        self._headers[new_key] = value

        # Update liststore
        self.liststore.set_value(iter, 0, new_key)
        self._save_headers()

    def _on_value_edited(self, renderer: Gtk.CellRendererText, path: str, new_text: str) -> None:
        iter = self.liststore.get_iter(path)
        key = self.liststore.get_value(iter, 0)

        # Update headers dict
        self._headers[key] = new_text

        # Update liststore
        self.liststore.set_value(iter, 1, new_text)
        self._save_headers()

    def _on_add_clicked(self, button: Gtk.Button) -> None:
        """Add a new header."""
        key = self._get_unique_key('New-Header')

        # Add to headers and liststore
        self._headers[key] = ''
        iter = self.liststore.append([key, '', True, False])

        # Select and start editing the new row
        path = self.liststore.get_path(iter)
        self.treeview.set_cursor(path, self.treeview.get_column(0), True)

        self._update_infotext()

    def _get_unique_key(self, base_name: str) -> str:
        key = self._metadata_handler.normalize_key(base_name)
        counter = 1
        while key in self._headers:
            key = f'{base_name}-{counter}'
            counter += 1

        return key

    def _on_remove_clicked(self, button: Gtk.Button) -> None:
        model, iter = self.selection.get_selected()
        if iter is None:
            return

        key = model.get_value(iter, 0)

        # Remove from headers and liststore
        self._headers.pop(key, None)
        model.remove(iter)

        self._update_infotext()

    def _save_headers(self) -> None:
        """Save current headers back to the page."""
        if self._current_page is None:
            logger.warning('No page loaded')
            return

        self._pageview.notebook.store_page(self._current_page)
