import re

from zim.base import LastDefinedOrderedDict
from zim.signals import SignalEmitter, SIGNAL_RUN_LAST
from zim.gui.pageview import PageView

class MetadataModel(SignalEmitter):
    """Shared model for page metadata. All data operations go through this model."""

    __signals__ = {
        'changed': (SIGNAL_RUN_LAST, None, ()),
    }

    def __init__(self):
        self._page_view: PageView = None
        self._data: dict[str, str] = {}

    def on_page_change(self, page_view: PageView) -> None:
        """Load metadata from a new page."""
        self._page_view = page_view
        self._data = page_view.page.get_parsetree().meta
        self._on_change()

    def _on_change(self) -> None:
        print("_on_change")
        if self._page_view:
            # In order to reliably update metadata, it has to be removed from both, the parsetree
            # as well as the page, as zim default logic will try to preserve headers from both locations
            # on save.
            self._page_view.page.get_parsetree().meta = LastDefinedOrderedDict(self._data)
            self._page_view.page._meta = self._data
            self._page_view.notebook.store_page(self._page_view.page)

        self.emit('changed')

    def get_data(self) -> dict[str, str]:
        """Get all metadata as a dict."""
        return self._data.copy()

    def get_value(self, key: str) -> str:
        """Get value for a key."""
        return self._data.get(key, '')

    def set_value(self, key: str, value: str) -> None:
        """Set value for a key."""
        print("set_value", key, value)
        if value.strip() == '':
            value = '-'
        if self._data.get(key) != value:
            self._data[key] = value
            self._on_change()

    def add_key(self, base_name: str = 'New-Header') -> str:
        """Add a new key with empty value. Returns the actual key used."""
        print("add_key", base_name)
        key = self._get_unique_key(base_name)
        self._data[key] = '-'
        self._on_change()
        return key

    def remove_key(self, key: str) -> None:
        """Remove a key."""
        print("remove_key", key)
        if key in self._data:
            del self._data[key]
            self._on_change()

    def rename_key(self, old_key: str, new_key_base: str) -> str:
        """Rename a key. Returns the actual new key used."""
        print("rename_key", old_key, new_key_base)
        if old_key not in self._data:
            return old_key
        value = self._data.pop(old_key)
        new_key = self._get_unique_key(new_key_base)
        self._data[new_key] = value
        self._on_change()
        return new_key

    def _get_unique_key(self, base_name: str) -> str:
        """Generate a unique key based on the given name."""
        key = self.normalize_key(base_name)
        if key not in self._data:
            return key
        counter = 1
        while f'{base_name}-{counter}' in self._data:
            counter += 1
        return f'{base_name}-{counter}'

    @staticmethod
    def normalize_key(key: str) -> str:
        """Normalize a metadata key to kebab-case."""
        return re.sub(
            "[^a-zA-Z0-9-]+",
            "-",
            key.strip()
        )