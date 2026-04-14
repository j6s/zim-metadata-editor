import logging

from zim.notebook import Page
from zim.plugins import PluginClass
from zim.gui.pageview import PageViewExtension, PageView
from .metadata_handler import MetadataHandler
from zim.gui.widgets import RIGHT_PANE
from .gui import MetadataEditorWidget

logger = logging.getLogger('zim.plugins.metadata_editor')


try:
    from zim.i18n import _
except ImportError:
    _ = lambda x: x


class MetadataEditorPlugin(PluginClass):

    plugin_info = {
        'name': _('Metadata Editor'),
        'description': _('''\
Provider a metadata editing pane in order to add custom metadata to notes.
The metadata is saved based on the underlying file format (e.g. RFC822 headers
for zim-wiki files or front-matter for markdown files).
'''),
        'author': 'Johannes Hertenstein <zim-wiki@j6s.dev>',
    }

    plugin_preferences = (
        # (key, type, label, default)
    )

    metadata_handler = MetadataHandler()


class MetadataEditorPageViewExtension(PageViewExtension):
    """Extension that adds the metadata editor sidebar."""

    def __init__(self, plugin: MetadataEditorPlugin, pageview: PageView):
        PageViewExtension.__init__(self, plugin, pageview)

        self.widget = MetadataEditorWidget(pageview, self.plugin.metadata_handler)

        # Add to sidebar (hardcoded to right pane)
        self._window.add_sidepane_widget(self.widget.__class__.__name__, self.widget, RIGHT_PANE)
        self._sidepane_widgets[self.widget] = None  # No preference signal to disconnect
        self.widget.show_all()

        # Connect to page change signal
        if pageview.page is not None:
            self.on_page_changed(pageview, pageview.page)
        self.connectto(pageview, 'page-changed', self.on_page_changed)

    def on_page_changed(self, pageview: PageView, page: Page):
        """Handle page navigation."""
        self.widget.load_page(page)

    def teardown(self):
        """Clean up when plugin is disabled."""
        PageViewExtension.teardown(self)

