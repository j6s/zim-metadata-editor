# Metadata Editor for Zim Wiki

A minimal metadata editor for Zim Wiki that allows
adding metadata headers to pages (similar to frontmatter
in Markdown).

![Screenshot](doc/screenshot.png)

## Installation

1. Clone the repository into your zim wiki plugin directory
    - Linux: `git clone https://github.com/j6s/zim-metadata-editor ~/.local/share/zim/plugins/metadata_editor`
    - macOS: `git clone https://github.com/j6s/zim-metadata-editor ~/Library/Application Support/org.zim-wiki.Zim/share/zim/plugins/metadata_editor`
2. Restart Zim
3. Enable the plugin in the Zim settings

## Usage

The plugin provides two ways to view and edit page metadata:

### Sidebar Widget

Once enabled, the plugin adds a "Metadata" panel to the sidebar. 
This panel displays all metadata for the current page and allows editing.

### Inline Block Widget

You can also insert a metadata editor block directly into a page:

1. Go to **Insert > Metadata Block**
2. The block appears inline in your page content
3. Edit metadata directly within the page

Both the sidebar and inline block show the same metadata and stay synchronized.
