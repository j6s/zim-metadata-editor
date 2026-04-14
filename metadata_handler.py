import re

from zim.notebook.page import Page

class MetadataHandler:

    def normalize_key(self, key):
        return re.sub(
            "[^a-zA-Z0-9-]+",
            "-",
            key.strip()
        )

    def read(self, page: Page):
        return page.get_parsetree().meta

    def write(self, page: Page, metadata):
        page.get_parsetree().update(metadata)
