import logging

from zim.gui.notebookview import NotebookViewExtension
from zim.notebook import Notebook, Page, NotebookExtension
from zim.plugins import PluginClass, InsertedObjectTypeExtension
from zim.gui.pageview import PageViewExtension, PageView
from zim.gui.widgets import LEFT_PANE, RIGHT_PANE, BOTTOM_PANE, PANE_POSITIONS
from zim.signals import SIGNAL_AFTER
from .model import MetadataModel
from .gui import MetadataEditorWidget, MetadataBlockWidget

logger = logging.getLogger('zim.plugins.metadata_editor')


try:
    from zim.i18n import _
except ImportError:
    _ = lambda x: x

# Pane positions including "none" to disable sidebar
SIDEBAR_POSITIONS = PANE_POSITIONS + (('none', _('Disabled')),)

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
        ('pane', 'choice', _('Sidebar position'), RIGHT_PANE, SIDEBAR_POSITIONS),
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

        self.widget = None
        self._add_sidebar_if_enabled(plugin.preferences)

        # Listen for preference changes
        self.connectto(plugin.preferences, 'changed', self._add_sidebar_if_enabled)

    def _add_sidebar_if_enabled(self, preferences) -> None:
        """Add sidebar widget if pane preference is not 'none'."""
        if self.widget is not None:
            self._window.remove(self.widget)
            if self.widget in self._sidepane_widgets:
                del self._sidepane_widgets[self.widget]
            self.widget = None

        pane = preferences['pane']
        if pane != 'none':
            self.widget = MetadataEditorWidget(self.plugin.model)
            self._window.add_sidepane_widget(
                self.widget.__class__.__name__, self.widget, pane)
            self._sidepane_widgets[self.widget] = None
            self.widget.show_all()
            self.widget.refresh()

    def teardown(self) -> None:
        """Clean up when plugin is disabled."""
        PageViewExtension.teardown(self)


class MetadataBlockObjectType(InsertedObjectTypeExtension):
    """Extension that registers the metadata block as an insertable object."""

    name = 'metadatablock'
    label = _('Metadata Block')
    verb_icon = 'accessories-text-editor-symbolic'

    def model_from_data(self, notebook, page, attrib, data) -> MetadataModel:
        """All blocks use the same model."""
        return self.plugin.model

    def data_from_model(self, model: MetadataModel):
        return {'type': self.name}, ''

    def create_widget(self, model: MetadataModel):
        return MetadataBlockWidget(model)