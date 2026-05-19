import logging

from zim.gui.notebookview import NotebookViewExtension
from zim.notebook import Notebook, Page, NotebookExtension
from zim.plugins import PluginClass, InsertedObjectTypeExtension
from zim.gui.pageview import PageViewExtension, PageView
from zim.gui.widgets import RIGHT_PANE
from zim.signals import SIGNAL_AFTER
from .model import MetadataModel
from .gui import MetadataEditorWidget, MetadataBlockWidget

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

    model = MetadataModel()


class MetadataEditorNotebookExtension(NotebookViewExtension):
    def __init__(self, plugin: MetadataEditorPlugin, pageview: PageView):
        NotebookViewExtension.__init__(self, plugin, pageview)

        self.plugin.model.on_page_change(pageview, pageview.page)
        self.connectto(pageview, "page-changed", self.plugin.model.on_page_change)

class MetadataEditorPageViewExtension(PageViewExtension):
    """Extension that adds the metadata editor sidebar."""

    def __init__(self, plugin: MetadataEditorPlugin, pageview: PageView):
        PageViewExtension.__init__(self, plugin, pageview)

        self.widget = MetadataEditorWidget(plugin.model)

        # Add to sidebar (hardcoded to right pane)
        self._window.add_sidepane_widget(self.widget.__class__.__name__, self.widget, RIGHT_PANE)
        self._sidepane_widgets[self.widget] = None  # No preference signal to disconnect
        self.widget.show_all()

        # Load initial page and connect to changes
        self.widget.refresh()

    def teardown(self):
        """Clean up when plugin is disabled."""
        PageViewExtension.teardown(self)


class MetadataBlockObjectType(InsertedObjectTypeExtension):
    """Extension that registers the metadata block as an insertable object."""

    name = 'metadatablock'
    label = _('Metadata Block')
    verb_icon = 'accessories-text-editor-symbolic'

    def model_from_data(self, notebook, page, attrib, data):
        """All blocks use the same model."""
        return self.plugin.model

    def data_from_model(self, model):
        return {'type': self.name}, ''

    def create_widget(self, model):
        return MetadataBlockWidget(model)