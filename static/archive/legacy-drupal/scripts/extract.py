#!/usr/bin/env python3
"""
SBPL Drupal 7 dump extractor.

Streams ../dump-2018-04-12.sql, decodes the relevant tables, and writes a
clean, human-readable bundle under ../newwebsite/{content,data}/.

Tables consumed:
    Page content
        node, field_data_body, node_revision, node_type
        field_data_field_image, field_data_field_page_file, field_data_field_tags
    Navigation
        menu_links, menu_custom, url_alias
    People + permissions
        users, users_roles, role, role_permission
    Files
        file_managed, file_usage
    Custom HTML blocks (sidebar / footer)
        block_custom, block
    Taxonomy / tags
        taxonomy_vocabulary, taxonomy_term_data,
        taxonomy_term_hierarchy, taxonomy_index
    Comments
        comment, field_data_comment_body
    Contact form
        contact
    Filters / WYSIWYG text formats
        filter_format, filter
    Site config
        variable

Outputs (relative to repo root):
    newwebsite/content/pages/<nid:04d>-<slug>.{html,md,json}
    newwebsite/content/menus.json
    newwebsite/content/users.json
    newwebsite/content/blocks/<bid>-<slug>.{html,md,json}
    newwebsite/content/blocks_index.json
    newwebsite/content/site_variables.json
    newwebsite/data/pages_index.csv
    newwebsite/data/files_managed.json
    newwebsite/data/file_usage.json
    newwebsite/data/url_aliases.json
    newwebsite/data/node_types.json
    newwebsite/data/taxonomy.json
    newwebsite/data/comments.json
    newwebsite/data/roles.json
    newwebsite/data/contact_categories.json
    newwebsite/data/text_formats.json
    newwebsite/data/page_field_image.json
    newwebsite/data/page_field_page_file.json
    newwebsite/data/page_field_tags.json
    newwebsite/data/drupal_variables.json

Pure stdlib - no third-party deps.
"""

from __future__ import annotations

import csv
import html
import json
import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
NEWWEBSITE = SCRIPT_DIR.parent
REPO_ROOT = NEWWEBSITE.parent
SQL_DUMP = REPO_ROOT / "dump-2018-04-12.sql"

PAGES_DIR = NEWWEBSITE / "content" / "pages"
CONTENT_DIR = NEWWEBSITE / "content"
DATA_DIR = NEWWEBSITE / "data"

# ---------------------------------------------------------------------------
# Schemas (column lists, in dump order)
# ---------------------------------------------------------------------------

NODE_COLUMNS = [
    "nid", "vid", "type", "language", "title", "uid", "status",
    "created", "changed", "comment", "promote", "sticky", "tnid",
    "translate",
]

FIELD_DATA_BODY_COLUMNS = [
    "entity_type", "bundle", "deleted", "entity_id", "revision_id",
    "language", "delta", "body_value", "body_summary", "body_format",
]

NODE_REVISION_COLUMNS = [
    "nid", "vid", "uid", "title", "log", "timestamp", "status",
    "comment", "promote", "sticky",
]

MENU_LINKS_COLUMNS = [
    "menu_name", "mlid", "plid", "link_path", "router_path", "link_title",
    "options", "module", "hidden", "external", "has_children", "expanded",
    "weight", "depth", "customized",
    "p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8", "p9",
    "updated",
]

USERS_COLUMNS = [
    "uid", "name", "pass", "mail", "theme", "signature", "signature_format",
    "created", "access", "login", "status", "timezone", "language",
    "picture", "init", "data",
]

FILE_MANAGED_COLUMNS = [
    "fid", "uid", "filename", "uri", "filemime", "filesize", "status",
    "timestamp",
]

VARIABLE_COLUMNS = ["name", "value"]

# --- Additional content-bearing tables ----------------------------------------

NODE_TYPE_COLUMNS = [
    "type", "name", "base", "module", "description", "help", "has_title",
    "title_label", "custom", "modified", "locked", "disabled", "orig_type",
]

URL_ALIAS_COLUMNS = ["pid", "source", "alias", "language"]

BLOCK_CUSTOM_COLUMNS = ["bid", "body", "info", "format"]

FIELD_DATA_FIELD_IMAGE_COLUMNS = [
    "entity_type", "bundle", "deleted", "entity_id", "revision_id",
    "language", "delta",
    "field_image_fid", "field_image_alt", "field_image_title",
    "field_image_width", "field_image_height",
]

FIELD_DATA_FIELD_PAGE_FILE_COLUMNS = [
    "entity_type", "bundle", "deleted", "entity_id", "revision_id",
    "language", "delta",
    "field_page_file_fid", "field_page_file_display",
    "field_page_file_description",
]

FIELD_DATA_FIELD_TAGS_COLUMNS = [
    "entity_type", "bundle", "deleted", "entity_id", "revision_id",
    "language", "delta", "field_tags_tid",
]

FILE_USAGE_COLUMNS = ["fid", "module", "type", "id", "count"]

TAXONOMY_VOCABULARY_COLUMNS = [
    "vid", "name", "machine_name", "description", "hierarchy",
    "module", "weight",
]

TAXONOMY_TERM_DATA_COLUMNS = [
    "tid", "vid", "name", "description", "format", "weight",
]

TAXONOMY_TERM_HIERARCHY_COLUMNS = ["tid", "parent"]

TAXONOMY_INDEX_COLUMNS = ["nid", "tid", "sticky", "created"]

COMMENT_COLUMNS = [
    "cid", "pid", "nid", "uid", "subject", "hostname", "created", "changed",
    "status", "thread", "name", "mail", "homepage", "language",
]

FIELD_DATA_COMMENT_BODY_COLUMNS = [
    "entity_type", "bundle", "deleted", "entity_id", "revision_id",
    "language", "delta", "comment_body_value", "comment_body_format",
]

ROLE_COLUMNS = ["rid", "name", "weight"]

USERS_ROLES_COLUMNS = ["uid", "rid"]

ROLE_PERMISSION_COLUMNS = ["rid", "permission", "module"]

CONTACT_COLUMNS = ["cid", "category", "recipients", "reply", "weight", "selected"]

FILTER_FORMAT_COLUMNS = ["format", "name", "cache", "status", "weight"]
FILTER_COLUMNS = ["format", "module", "name", "weight", "status", "settings"]

TABLES_OF_INTEREST = {
    # Page content
    "node": NODE_COLUMNS,
    "field_data_body": FIELD_DATA_BODY_COLUMNS,
    "node_revision": NODE_REVISION_COLUMNS,
    "node_type": NODE_TYPE_COLUMNS,
    "field_data_field_image": FIELD_DATA_FIELD_IMAGE_COLUMNS,
    "field_data_field_page_file": FIELD_DATA_FIELD_PAGE_FILE_COLUMNS,
    "field_data_field_tags": FIELD_DATA_FIELD_TAGS_COLUMNS,
    # Navigation
    "menu_links": MENU_LINKS_COLUMNS,
    "url_alias": URL_ALIAS_COLUMNS,
    # People + permissions
    "users": USERS_COLUMNS,
    "users_roles": USERS_ROLES_COLUMNS,
    "role": ROLE_COLUMNS,
    "role_permission": ROLE_PERMISSION_COLUMNS,
    # Files
    "file_managed": FILE_MANAGED_COLUMNS,
    "file_usage": FILE_USAGE_COLUMNS,
    # Custom HTML blocks (sidebar / footer)
    "block_custom": BLOCK_CUSTOM_COLUMNS,
    # Taxonomy / tags
    "taxonomy_vocabulary": TAXONOMY_VOCABULARY_COLUMNS,
    "taxonomy_term_data": TAXONOMY_TERM_DATA_COLUMNS,
    "taxonomy_term_hierarchy": TAXONOMY_TERM_HIERARCHY_COLUMNS,
    "taxonomy_index": TAXONOMY_INDEX_COLUMNS,
    # Comments
    "comment": COMMENT_COLUMNS,
    "field_data_comment_body": FIELD_DATA_COMMENT_BODY_COLUMNS,
    # Contact form
    "contact": CONTACT_COLUMNS,
    # Text formats / WYSIWYG
    "filter_format": FILTER_FORMAT_COLUMNS,
    "filter": FILTER_COLUMNS,
    # Site config
    "variable": VARIABLE_COLUMNS,
}


# ---------------------------------------------------------------------------
# Streaming SQL value parser
# ---------------------------------------------------------------------------

# MySQL backslash-escape decoding (per the dump format mysqldump produces).
_MYSQL_ESCAPES = {
    "0": "\0",
    "'": "'",
    '"': '"',
    "b": "\b",
    "n": "\n",
    "r": "\r",
    "t": "\t",
    "Z": "\x1a",
    "\\": "\\",
    "%": "\\%",  # \% / \_ are LIKE-escapes; preserve verbatim
    "_": "\\_",
}


def _decode_mysql_string(raw: str) -> str:
    """Decode a MySQL-quoted string body (without the surrounding quotes)."""
    out = []
    i = 0
    n = len(raw)
    while i < n:
        c = raw[i]
        if c == "\\" and i + 1 < n:
            nxt = raw[i + 1]
            out.append(_MYSQL_ESCAPES.get(nxt, nxt))
            i += 2
        else:
            out.append(c)
            i += 1
    return "".join(out)


def parse_values(values_str: str):
    """
    Parse the `(...),(...),(...)` payload of a MySQL INSERT.
    Yields one tuple (list of Python values) at a time.

    Values can be:
      - NULL                           -> None
      - integers / decimals            -> int or float
      - 'string with \\\\ \\' escapes' -> str
      - hex literals like 0xABCD       -> bytes
    """
    n = len(values_str)
    i = 0

    while i < n:
        # Skip whitespace, commas, and the leading '('.
        while i < n and values_str[i] in " \t\r\n,":
            i += 1
        if i >= n:
            break
        if values_str[i] == ";":
            break
        if values_str[i] != "(":
            raise ValueError(f"expected '(' at offset {i}, got {values_str[i]!r}")
        i += 1  # consume '('

        row = []
        while True:
            # skip leading whitespace
            while i < n and values_str[i] in " \t\r\n":
                i += 1
            if i >= n:
                raise ValueError("unexpected EOF inside row")

            c = values_str[i]
            if c == ")":
                i += 1
                break

            if c == "'":
                # quoted string
                i += 1
                start = i
                buf = []
                while i < n:
                    ch = values_str[i]
                    if ch == "\\" and i + 1 < n:
                        i += 2
                        continue
                    if ch == "'":
                        # could be end-of-string OR doubled '' (rare in mysqldump)
                        if i + 1 < n and values_str[i + 1] == "'":
                            i += 2
                            continue
                        break
                    i += 1
                if i >= n:
                    raise ValueError("unterminated string literal")
                raw = values_str[start:i]
                i += 1  # consume closing quote
                # handle SQL '' -> '
                raw = raw.replace("''", "'")
                row.append(_decode_mysql_string(raw))
            else:
                # unquoted token: NULL, number, hex, etc.
                start = i
                while i < n and values_str[i] not in ",)":
                    i += 1
                token = values_str[start:i].strip()
                if token.upper() == "NULL":
                    row.append(None)
                elif token.startswith("0x") or token.startswith("0X"):
                    try:
                        row.append(bytes.fromhex(token[2:]))
                    except ValueError:
                        row.append(token)
                else:
                    # number
                    try:
                        if "." in token or "e" in token or "E" in token:
                            row.append(float(token))
                        else:
                            row.append(int(token))
                    except ValueError:
                        row.append(token)

            # after value: expect ',' or ')'
            while i < n and values_str[i] in " \t\r\n":
                i += 1
            if i < n and values_str[i] == ",":
                i += 1
            elif i < n and values_str[i] == ")":
                i += 1
                break
            else:
                raise ValueError(f"unexpected char after value at {i}: {values_str[i:i+20]!r}")

        yield row


# ---------------------------------------------------------------------------
# Stream the dump and collect rows for tables of interest
# ---------------------------------------------------------------------------

INSERT_RE = re.compile(r"^INSERT INTO `([^`]+)` VALUES\s+(.+);\s*$", re.DOTALL)


def stream_inserts(sql_path: Path, wanted: set[str]):
    """
    Yield (table_name, row_dict) tuples for every INSERT into a wanted table.
    Reads the file line-by-line; mysqldump puts each INSERT on its own line.
    """
    with sql_path.open("r", encoding="utf-8", errors="replace", newline="\n") as f:
        # increase max line length is automatic for Python; defaults are fine
        for line in f:
            if not line.startswith("INSERT INTO `"):
                continue
            # Quick prefix filter to skip irrelevant inserts cheaply.
            tick_close = line.find("`", len("INSERT INTO `"))
            if tick_close < 0:
                continue
            table = line[len("INSERT INTO `"):tick_close]
            if table not in wanted:
                continue
            m = INSERT_RE.match(line)
            if not m:
                continue
            payload = m.group(2)
            cols = TABLES_OF_INTEREST[table]
            for row in parse_values(payload):
                if len(row) != len(cols):
                    raise ValueError(
                        f"{table}: expected {len(cols)} cols, got {len(row)} -> {row[:3]}..."
                    )
                yield table, dict(zip(cols, row))


# ---------------------------------------------------------------------------
# PHP serialize() decoder (for menu_links.options)
# ---------------------------------------------------------------------------

class PhpUnserializeError(Exception):
    pass


def php_unserialize(data):
    """
    Minimal php_unserialize() supporting: N, b, i, d, s, a.
    `data` may be str or bytes; returns Python objects.
    """
    if isinstance(data, bytes):
        data = data.decode("utf-8", errors="replace")

    pos = [0]

    def peek(n=1):
        return data[pos[0]:pos[0] + n]

    def consume(n):
        pos[0] += n

    def expect(ch):
        if peek() != ch:
            raise PhpUnserializeError(
                f"expected {ch!r} at {pos[0]}, got {peek()!r} in {data[max(0, pos[0]-10):pos[0]+10]!r}"
            )
        consume(1)

    def read_until(ch):
        end = data.find(ch, pos[0])
        if end < 0:
            raise PhpUnserializeError(f"missing {ch!r}")
        out = data[pos[0]:end]
        pos[0] = end + 1
        return out

    def parse():
        if pos[0] >= len(data):
            raise PhpUnserializeError("unexpected EOF")
        type_ch = data[pos[0]]
        if type_ch == "N":
            consume(1)
            expect(";")
            return None
        if type_ch == "b":
            consume(2)  # 'b:'
            v = read_until(";")
            return v == "1"
        if type_ch == "i":
            consume(2)
            v = read_until(";")
            return int(v)
        if type_ch == "d":
            consume(2)
            v = read_until(";")
            return float(v)
        if type_ch == "s":
            consume(2)
            length = int(read_until(":"))
            expect('"')
            # PHP serialize length is in bytes; our `data` is unicode, so
            # use a byte-aware slice.
            byts = data[pos[0]:].encode("utf-8", errors="replace")
            chunk = byts[:length].decode("utf-8", errors="replace")
            # advance pos by the codepoint length of `chunk`
            pos[0] += len(chunk)
            expect('"')
            expect(";")
            return chunk
        if type_ch == "a":
            consume(2)
            length = int(read_until(":"))
            expect("{")
            out = {}
            for _ in range(length):
                k = parse()
                v = parse()
                out[k] = v
            expect("}")
            # PHP arrays may be lists if keys are 0..N-1
            if all(isinstance(k, int) for k in out) and \
                    list(out.keys()) == list(range(length)):
                return [out[k] for k in range(length)]
            return out
        raise PhpUnserializeError(f"unsupported type {type_ch!r} at {pos[0]}")

    try:
        return parse()
    except PhpUnserializeError:
        # Return the raw blob as a string so callers can still see it.
        return {"__raw__": data}


# ---------------------------------------------------------------------------
# Slug + path helpers
# ---------------------------------------------------------------------------

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(title: str) -> str:
    s = title.lower().strip()
    s = _SLUG_RE.sub("-", s).strip("-")
    return s or "untitled"


# ---------------------------------------------------------------------------
# Asset URL rewriting (HTML body -> local media paths)
# ---------------------------------------------------------------------------

# Pages live at content/pages/, media at media/. Relative path:
REL_MEDIA = "../../media"

_ASSET_REWRITES = [
    # /shared/Images/foo.png -> ../../media/images/foo.png
    (re.compile(r'(?P<q>["\'])(?:https?://[^"\']*)?/shared/Images/'),
        lambda m: f'{m.group("q")}{REL_MEDIA}/images/'),
    # /shared/SBPL/...   -> ../../media/uploads/SBPL/...
    # (old site served this folder as an Apache directory listing of
    #  sbpl.tar.gz / sbpl.zip downloads)
    (re.compile(r'(?P<q>["\'])(?:https?://[^"\']*)?/shared/SBPL/'),
        lambda m: f'{m.group("q")}{REL_MEDIA}/uploads/SBPL/'),
    # /shared/Venkat/... -> ../../media/videos/...  (only ICRA13/beam_graphs.mp4 lives there)
    (re.compile(r'(?P<q>["\'])(?:https?://[^"\']*)?/shared/Venkat/ICRA13/'),
        lambda m: f'{m.group("q")}{REL_MEDIA}/videos/'),
    # /sites/default/files/pictures/foo.jpg -> ../../media/pictures/foo.jpg
    (re.compile(r'(?P<q>["\'])(?:https?://[^"\']*)?/sites/default/files/pictures/'),
        lambda m: f'{m.group("q")}{REL_MEDIA}/pictures/'),
    # /sites/default/files/sbpl_logo... -> ../../media/logos/...
    (re.compile(r'(?P<q>["\'])(?:https?://[^"\']*)?/sites/default/files/(sbpl_logo[^"\']*)'),
        lambda m: f'{m.group("q")}{REL_MEDIA}/logos/{m.group(2)}'),
    # /sites/default/files/Images|ImagesImages|site/... -> ../../media/uploads/...
    (re.compile(r'(?P<q>["\'])(?:https?://[^"\']*)?/sites/default/files/(Images/|ImagesImages/|site/)'),
        lambda m: f'{m.group("q")}{REL_MEDIA}/uploads/{m.group(2)}'),
    # public://Images/... -> ../../media/uploads/Images/... (Drupal stream wrapper, rare)
    (re.compile(r'(?P<q>["\'])public://Images/'),
        lambda m: f'{m.group("q")}{REL_MEDIA}/uploads/Images/'),
    (re.compile(r'(?P<q>["\'])public://pictures/'),
        lambda m: f'{m.group("q")}{REL_MEDIA}/pictures/'),
]


def rewrite_assets(html_text: str) -> str:
    out = html_text
    for pat, fn in _ASSET_REWRITES:
        out = pat.sub(fn, out)
    return out


# --- alias -> page-file rewriter --------------------------------------------
#
# The People page contains links like <a href="AndrewDornbush">…</a>. These
# are Drupal URL aliases that resolved to /node/<nid> on the live site.
# We feed `url_alias` into a map { 'AndrewDornbush' -> 'node/15' } and rewrite
# such bare hrefs to point at the corresponding ../<nid:04d>-<slug>.html page
# file in this bundle.

def make_alias_rewriter(alias_to_nid: dict, nid_to_stem: dict):
    """Return rewrite_alias_links(html_text) -> html_text."""
    if not alias_to_nid:
        return lambda html_text: html_text

    # Build a single regex that matches href|src="<bare_alias>" for any known alias.
    # We only rewrite quoted bare relative refs (no protocol, no slash).
    aliases = sorted(alias_to_nid, key=len, reverse=True)
    # Escape and join. Allow URL-encoded spaces (%20) too.
    parts = []
    for a in aliases:
        parts.append(re.escape(a).replace(r"\ ", r"(?:\ |%20)"))
    big = "(?:" + "|".join(parts) + ")"
    pat = re.compile(
        r'(?P<attr>(?:href|src))=(?P<q>["\'])(?:https?://sbpl\.net/?)?(?P<alias>'
        + big + r')(?P<frag>[?#][^"\']*)?(?P=q)',
        flags=re.IGNORECASE,
    )

    def repl(m: re.Match) -> str:
        alias = m.group("alias")
        # Decode %20 back to space for lookup
        clean = alias.replace("%20", " ")
        nid = alias_to_nid.get(clean) or alias_to_nid.get(alias)
        if nid is None:
            return m.group(0)
        stem = nid_to_stem.get(nid)
        if stem is None:
            return m.group(0)
        frag = m.group("frag") or ""
        return f'{m.group("attr")}={m.group("q")}{stem}.html{frag}{m.group("q")}'

    def rewrite(html_text: str) -> str:
        if not html_text:
            return html_text
        return pat.sub(repl, html_text)

    return rewrite


# ---------------------------------------------------------------------------
# Minimal HTML -> Markdown converter (stdlib-only)
# ---------------------------------------------------------------------------

class _Html2Md(HTMLParser):
    """
    Tiny converter good enough for the WYSIWYG HTML in this dump
    (CKEditor output: p, h1-h6, a, img, ul/ol/li, strong/em, br, hr,
    blockquote, code/pre, table is rendered as raw HTML as fallback).
    """

    BLOCK_TAGS = {
        "p", "div", "h1", "h2", "h3", "h4", "h5", "h6",
        "ul", "ol", "li", "blockquote", "pre", "hr", "table", "tr", "tbody",
        "thead", "tfoot",
    }

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.list_stack: list[tuple[str, int]] = []  # (type, counter)
        self.in_pre = 0
        self.link_href: list[str] = []
        self._suppress_text = 0  # script/style depth
        self._raw_html_depth = 0  # inside <table>: emit raw HTML
        self._raw_buf: list[str] = []

    # ------------- helpers -------------
    def _emit(self, s: str):
        if self._raw_html_depth:
            self._raw_buf.append(s)
        else:
            self.parts.append(s)

    def _newline(self, n=1):
        self._emit("\n" * n)

    def _list_prefix(self) -> str:
        if not self.list_stack:
            return ""
        kind, idx = self.list_stack[-1]
        indent = "    " * (len(self.list_stack) - 1)
        if kind == "ol":
            return f"{indent}{idx}. "
        return f"{indent}- "

    # ------------- parser callbacks -------------
    def handle_starttag(self, tag, attrs):
        attrs_d = dict(attrs)
        if tag in ("script", "style"):
            self._suppress_text += 1
            return
        if tag == "table":
            self._raw_html_depth += 1
            self._raw_buf = []
            self._raw_buf.append(self._format_tag(tag, attrs))
            return
        if self._raw_html_depth:
            self._raw_buf.append(self._format_tag(tag, attrs))
            return

        if tag == "br":
            self._emit("  \n")
            return
        if tag == "hr":
            self._newline(2)
            self._emit("---")
            self._newline(2)
            return
        if tag in ("strong", "b"):
            self._emit("**")
            return
        if tag in ("em", "i"):
            self._emit("*")
            return
        if tag == "u":
            # Markdown has no underline; passthrough as HTML
            self._emit("<u>")
            return
        if tag == "code":
            if self.in_pre:
                return
            self._emit("`")
            return
        if tag == "pre":
            self.in_pre += 1
            self._newline(2)
            self._emit("```\n")
            return
        if tag == "blockquote":
            self._newline(2)
            self._emit("> ")
            return
        if tag == "a":
            href = attrs_d.get("href", "")
            self.link_href.append(href)
            self._emit("[")
            return
        if tag == "img":
            alt = attrs_d.get("alt", "").replace("\n", " ").strip()
            src = attrs_d.get("src", "")
            title = attrs_d.get("title", "")
            if title:
                title_part = f' "{title}"'
            else:
                title_part = ""
            self._emit(f"![{alt}]({src}{title_part})")
            return
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = int(tag[1])
            self._newline(2)
            self._emit("#" * level + " ")
            return
        if tag == "p":
            self._newline(2)
            return
        if tag == "div":
            self._newline()
            return
        if tag == "ul":
            self._newline()
            self.list_stack.append(("ul", 1))
            return
        if tag == "ol":
            self._newline()
            self.list_stack.append(("ol", 1))
            return
        if tag == "li":
            self._newline()
            self._emit(self._list_prefix())
            if self.list_stack and self.list_stack[-1][0] == "ol":
                kind, idx = self.list_stack[-1]
                self.list_stack[-1] = (kind, idx + 1)
            return
        # Unknown / passthrough tags (span etc.) — do nothing structural

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._suppress_text = max(0, self._suppress_text - 1)
            return
        if self._raw_html_depth:
            self._raw_buf.append(f"</{tag}>")
            if tag == "table":
                self._raw_html_depth -= 1
                if self._raw_html_depth == 0:
                    self.parts.append("\n\n")
                    self.parts.append("".join(self._raw_buf))
                    self.parts.append("\n\n")
                    self._raw_buf = []
            return

        if tag in ("strong", "b"):
            self._emit("**")
            return
        if tag in ("em", "i"):
            self._emit("*")
            return
        if tag == "u":
            self._emit("</u>")
            return
        if tag == "code":
            if self.in_pre:
                return
            self._emit("`")
            return
        if tag == "pre":
            self.in_pre = max(0, self.in_pre - 1)
            self._emit("\n```")
            self._newline(2)
            return
        if tag == "blockquote":
            self._newline(2)
            return
        if tag == "a":
            href = self.link_href.pop() if self.link_href else ""
            self._emit(f"]({href})")
            return
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6", "p", "div"):
            self._newline(2)
            return
        if tag in ("ul", "ol"):
            if self.list_stack:
                self.list_stack.pop()
            self._newline()
            return
        if tag == "li":
            return

    def handle_data(self, data):
        if self._suppress_text:
            return
        if self._raw_html_depth:
            self._raw_buf.append(html.escape(data, quote=False))
            return
        if self.in_pre:
            self._emit(data)
            return
        # Collapse runs of internal whitespace but preserve newlines as spaces.
        if not data:
            return
        # In HTML, runs of whitespace are equivalent to a single space.
        text = re.sub(r"\s+", " ", data)
        self._emit(text)

    def _format_tag(self, tag, attrs):
        if not attrs:
            return f"<{tag}>"
        attr_str = " ".join(
            f'{k}="{html.escape(v or "", quote=True)}"' for k, v in attrs
        )
        return f"<{tag} {attr_str}>"

    def get_markdown(self) -> str:
        text = "".join(self.parts)
        # Normalise: collapse 3+ blank lines, strip trailing whitespace per line.
        text = re.sub(r"[ \t]+\n", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip() + "\n"


def html_to_markdown(html_text: str) -> str:
    parser = _Html2Md()
    try:
        parser.feed(html_text)
        parser.close()
    except Exception as e:
        # Fall back to raw HTML if parsing dies on something exotic.
        return f"<!-- html2md fallback ({e}) -->\n{html_text}"
    return parser.get_markdown()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if not SQL_DUMP.is_file():
        sys.exit(f"missing dump: {SQL_DUMP}")

    PAGES_DIR.mkdir(parents=True, exist_ok=True)
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Wipe any stale page triplets from previous runs so renames don't leave
    # orphans behind. We never touch data/raw/ (the verbatim SQL copies).
    for stale in PAGES_DIR.glob("*.*"):
        stale.unlink()

    nodes: dict[int, dict] = {}
    bodies: dict[int, dict] = {}  # entity_id -> latest body row
    revisions: dict[int, dict] = {}  # vid -> revision row
    node_types: list[dict] = []
    field_image: list[dict] = []
    field_page_file: list[dict] = []
    field_tags: list[dict] = []

    menu_rows: list[dict] = []
    url_aliases: list[dict] = []

    user_rows: list[dict] = []
    users_roles: list[dict] = []
    roles: list[dict] = []
    role_permissions: list[dict] = []

    file_rows: list[dict] = []
    file_usage_rows: list[dict] = []

    block_custom_rows: list[dict] = []

    tax_vocab: list[dict] = []
    tax_terms: list[dict] = []
    tax_hierarchy: list[dict] = []
    tax_index: list[dict] = []

    comment_rows: list[dict] = []
    comment_bodies: list[dict] = []

    contact_rows: list[dict] = []
    filter_formats: list[dict] = []
    filter_rows: list[dict] = []

    variables: dict[str, str] = {}

    print(f"streaming {SQL_DUMP.name} ...", file=sys.stderr)

    for table, row in stream_inserts(SQL_DUMP, set(TABLES_OF_INTEREST)):
        if table == "node":
            nodes[row["nid"]] = row
        elif table == "field_data_body":
            if row.get("entity_type") != "node":
                continue
            if row.get("deleted"):
                continue
            if row.get("delta", 0) != 0:
                continue
            bodies[row["entity_id"]] = row
        elif table == "node_revision":
            revisions[row["vid"]] = row
        elif table == "node_type":
            node_types.append(row)
        elif table == "field_data_field_image":
            if not row.get("deleted"):
                field_image.append(row)
        elif table == "field_data_field_page_file":
            if not row.get("deleted"):
                field_page_file.append(row)
        elif table == "field_data_field_tags":
            if not row.get("deleted"):
                field_tags.append(row)
        elif table == "menu_links":
            menu_rows.append(row)
        elif table == "url_alias":
            url_aliases.append(row)
        elif table == "users":
            user_rows.append(row)
        elif table == "users_roles":
            users_roles.append(row)
        elif table == "role":
            roles.append(row)
        elif table == "role_permission":
            role_permissions.append(row)
        elif table == "file_managed":
            file_rows.append(row)
        elif table == "file_usage":
            file_usage_rows.append(row)
        elif table == "block_custom":
            block_custom_rows.append(row)
        elif table == "taxonomy_vocabulary":
            tax_vocab.append(row)
        elif table == "taxonomy_term_data":
            tax_terms.append(row)
        elif table == "taxonomy_term_hierarchy":
            tax_hierarchy.append(row)
        elif table == "taxonomy_index":
            tax_index.append(row)
        elif table == "comment":
            comment_rows.append(row)
        elif table == "field_data_comment_body":
            if row.get("entity_type") == "comment" and not row.get("deleted"):
                comment_bodies.append(row)
        elif table == "contact":
            contact_rows.append(row)
        elif table == "filter_format":
            filter_formats.append(row)
        elif table == "filter":
            filter_rows.append(row)
        elif table == "variable":
            try:
                variables[row["name"]] = php_unserialize(row["value"])
            except Exception:
                variables[row["name"]] = None

    print(
        f"  nodes={len(nodes)} bodies={len(bodies)} revisions={len(revisions)} "
        f"node_types={len(node_types)} url_aliases={len(url_aliases)} "
        f"menu_links={len(menu_rows)} users={len(user_rows)} files={len(file_rows)} "
        f"file_usage={len(file_usage_rows)} block_custom={len(block_custom_rows)} "
        f"tax_terms={len(tax_terms)} comments={len(comment_rows)} "
        f"contact={len(contact_rows)} filter_formats={len(filter_formats)}",
        file=sys.stderr,
    )

    # -----------------------------------------------------------------------
    # Build alias->nid + nid->page-file maps so the page writer can rewrite
    # bare intra-site links like <a href="AndrewDornbush">.
    # -----------------------------------------------------------------------
    alias_to_nid: dict[str, int] = {}
    for a in url_aliases:
        src = (a.get("source") or "")
        m = re.fullmatch(r"node/(\d+)", src)
        if not m:
            continue
        alias_to_nid[a.get("alias") or ""] = int(m.group(1))

    nid_to_stem: dict[int, str] = {}
    for nid in sorted(nodes):
        title = (nodes[nid].get("title") or "").strip() or f"untitled-{nid}"
        nid_to_stem[nid] = f"{nid:04d}-{slugify(title)}"

    alias_rewrite = make_alias_rewriter(alias_to_nid, nid_to_stem)

    # Build helper indexes for page metadata (image fields, file fields, tags)
    img_by_nid: dict[int, list[dict]] = {}
    for r in field_image:
        img_by_nid.setdefault(r["entity_id"], []).append(r)
    pf_by_nid: dict[int, list[dict]] = {}
    for r in field_page_file:
        pf_by_nid.setdefault(r["entity_id"], []).append(r)
    tag_by_nid: dict[int, list[int]] = {}
    for r in field_tags:
        tag_by_nid.setdefault(r["entity_id"], []).append(r["field_tags_tid"])

    # -----------------------------------------------------------------------
    # Per-page triplets
    # -----------------------------------------------------------------------
    author_uids = write_pages(
        nodes, bodies, revisions,
        alias_rewrite=alias_rewrite,
        img_by_nid=img_by_nid,
        pf_by_nid=pf_by_nid,
        tag_by_nid=tag_by_nid,
        alias_by_nid=_invert_alias_map(alias_to_nid),
    )

    # -----------------------------------------------------------------------
    # menus.json
    # -----------------------------------------------------------------------
    write_menus(menu_rows, nodes)

    # -----------------------------------------------------------------------
    # users.json (filter spam registrations; keep real members + authors)
    # -----------------------------------------------------------------------
    write_users(user_rows, author_uids, users_roles, roles)

    # -----------------------------------------------------------------------
    # files_managed.json + file_usage.json
    # -----------------------------------------------------------------------
    write_files_managed(file_rows)
    write_file_usage(file_usage_rows)

    # -----------------------------------------------------------------------
    # url_aliases.json + node_types.json
    # -----------------------------------------------------------------------
    write_url_aliases(url_aliases, nodes, nid_to_stem)
    write_node_types(node_types)

    # -----------------------------------------------------------------------
    # Custom HTML blocks (content/blocks/<bid>-<slug>.{html,md,json})
    # -----------------------------------------------------------------------
    write_blocks(block_custom_rows, alias_rewrite)

    # -----------------------------------------------------------------------
    # Field data per page (image / page_file / tags)
    # -----------------------------------------------------------------------
    write_page_fields(field_image, field_page_file, field_tags)

    # -----------------------------------------------------------------------
    # Taxonomy + comments + roles + contact + text formats
    # -----------------------------------------------------------------------
    write_taxonomy(tax_vocab, tax_terms, tax_hierarchy, tax_index)
    write_comments(comment_rows, comment_bodies)
    write_roles(roles, role_permissions)
    write_contact(contact_rows)
    write_text_formats(filter_formats, filter_rows)

    # -----------------------------------------------------------------------
    # all Drupal site variables (decoded from PHP-serialized blobs)
    # -----------------------------------------------------------------------
    write_variables(variables)

    print("done.", file=sys.stderr)


def _invert_alias_map(alias_to_nid: dict) -> dict:
    """{alias -> nid} becomes {nid -> [aliases...]}, sorted shortest first."""
    out: dict = {}
    for alias, nid in alias_to_nid.items():
        out.setdefault(nid, []).append(alias)
    for nid in out:
        out[nid].sort(key=len)
    return out


def write_pages(
    nodes,
    bodies,
    revisions,
    alias_rewrite=lambda s: s,
    img_by_nid=None,
    pf_by_nid=None,
    tag_by_nid=None,
    alias_by_nid=None,
):
    img_by_nid = img_by_nid or {}
    pf_by_nid = pf_by_nid or {}
    tag_by_nid = tag_by_nid or {}
    alias_by_nid = alias_by_nid or {}

    index_rows = []
    author_uids: set[int] = set()
    for nid in sorted(nodes):
        node = nodes[nid]
        body_row = bodies.get(nid, {})
        body_html = body_row.get("body_value", "") or ""
        body_summary = body_row.get("body_summary", "") or ""
        body_format = body_row.get("body_format", "") or ""

        rewritten_html = alias_rewrite(rewrite_assets(body_html))
        markdown = html_to_markdown(rewritten_html)

        title = (node.get("title") or "").strip() or f"untitled-{nid}"
        slug = slugify(title)
        stem = f"{nid:04d}-{slug}"

        rev = revisions.get(node.get("vid"))
        rev_log = (rev or {}).get("log", "") if rev else ""

        # Field data attached to this node (image / page_file / tags)
        page_images = [
            {
                "fid": r.get("field_image_fid"),
                "alt": r.get("field_image_alt"),
                "title": r.get("field_image_title"),
                "width": r.get("field_image_width"),
                "height": r.get("field_image_height"),
                "delta": r.get("delta"),
            }
            for r in sorted(img_by_nid.get(nid, []), key=lambda x: x.get("delta") or 0)
        ]
        page_files = [
            {
                "fid": r.get("field_page_file_fid"),
                "display": r.get("field_page_file_display"),
                "description": r.get("field_page_file_description"),
                "delta": r.get("delta"),
            }
            for r in sorted(pf_by_nid.get(nid, []), key=lambda x: x.get("delta") or 0)
        ]
        page_tags = sorted({int(t) for t in tag_by_nid.get(nid, []) if t is not None})

        json_obj = {
            "nid": nid,
            "vid": node.get("vid"),
            "type": node.get("type"),
            "language": node.get("language"),
            "title": title,
            "slug": slug,
            "uid": node.get("uid"),
            "status": node.get("status"),
            "promote": node.get("promote"),
            "sticky": node.get("sticky"),
            "comment": node.get("comment"),
            "created": node.get("created"),
            "changed": node.get("changed"),
            "url_aliases": alias_by_nid.get(nid, []),
            "tags_tids": page_tags,
            "field_image": page_images,
            "field_page_file": page_files,
            "body_format": body_format,
            "body_summary": body_summary,
            "body_html_rewritten": rewritten_html,
            "body_markdown": markdown,
            "body_html_raw": body_html,
            "revision_log": rev_log,
        }

        (PAGES_DIR / f"{stem}.html").write_text(
            f"<!DOCTYPE html>\n<html><head><meta charset=\"utf-8\">"
            f"<title>{html.escape(title)}</title></head>\n<body>\n"
            f"<h1>{html.escape(title)}</h1>\n"
            f"{rewritten_html}\n"
            f"</body></html>\n",
            encoding="utf-8",
        )
        (PAGES_DIR / f"{stem}.md").write_text(
            f"# {title}\n\n{markdown}", encoding="utf-8"
        )
        (PAGES_DIR / f"{stem}.json").write_text(
            json.dumps(json_obj, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        index_rows.append({
            "nid": nid,
            "title": title,
            "type": node.get("type"),
            "created": node.get("created"),
            "updated": node.get("changed"),
            "uid": node.get("uid"),
            "slug": slug,
            "url_aliases": ";".join(alias_by_nid.get(nid, [])),
            "file_html": f"content/pages/{stem}.html",
            "file_md": f"content/pages/{stem}.md",
            "file_json": f"content/pages/{stem}.json",
        })
        if node.get("uid") is not None:
            author_uids.add(int(node["uid"]))

    # CSV index
    csv_path = DATA_DIR / "pages_index.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=[
                "nid", "title", "type", "created", "updated", "uid", "slug",
                "url_aliases",
                "file_html", "file_md", "file_json",
            ],
        )
        writer.writeheader()
        for r in index_rows:
            writer.writerow(r)
    print(f"  wrote {len(index_rows)} pages -> content/pages/, index -> {csv_path.name}",
          file=sys.stderr)
    return author_uids


def write_menus(menu_rows, nodes):
    """
    Build a JSON tree per menu_name (only those that look like real
    site nav, i.e. main-menu, user-menu, navigation, contact-us, etc.).
    Drop the giant 'management' admin menu.
    """
    # Decode `options` for every row.
    cleaned = []
    for r in menu_rows:
        opts_raw = r.get("options")
        if isinstance(opts_raw, bytes):
            opts_raw = opts_raw.decode("utf-8", errors="replace")
        try:
            opts = php_unserialize(opts_raw) if opts_raw else {}
        except Exception:
            opts = {"__raw__": str(opts_raw)}

        link_path = r.get("link_path") or ""
        node_target = None
        m = re.fullmatch(r"node/(\d+)", link_path)
        if m:
            target_nid = int(m.group(1))
            if target_nid in nodes:
                node_target = {
                    "nid": target_nid,
                    "title": nodes[target_nid].get("title"),
                }

        cleaned.append({
            "menu_name": r.get("menu_name"),
            "mlid": r.get("mlid"),
            "plid": r.get("plid"),
            "link_path": link_path,
            "router_path": r.get("router_path"),
            "link_title": r.get("link_title"),
            "options": opts,
            "module": r.get("module"),
            "hidden": r.get("hidden"),
            "external": r.get("external"),
            "weight": r.get("weight"),
            "depth": r.get("depth"),
            "node_target": node_target,
        })

    # Group by menu_name and build tree by plid.
    INTERESTING_MENUS = {
        "main-menu", "menu-contact-us", "navigation", "user-menu",
        "shortcut-set-1",
    }
    by_menu: dict[str, list[dict]] = {}
    for row in cleaned:
        by_menu.setdefault(row["menu_name"], []).append(row)

    menus_out = {}
    for menu_name, rows in by_menu.items():
        if menu_name not in INTERESTING_MENUS:
            # We still keep a flat list under `_other_menus` for completeness.
            continue
        by_mlid = {r["mlid"]: dict(r, children=[]) for r in rows}
        roots = []
        for r in by_mlid.values():
            parent = by_mlid.get(r["plid"])
            if parent and r["plid"] != 0:
                parent["children"].append(r)
            else:
                roots.append(r)

        def sort_tree(items):
            items.sort(key=lambda x: (x.get("weight", 0), x.get("mlid", 0)))
            for it in items:
                sort_tree(it["children"])

        sort_tree(roots)
        menus_out[menu_name] = roots

    out_path = CONTENT_DIR / "menus.json"
    out_path.write_text(json.dumps(menus_out, ensure_ascii=False, indent=2), encoding="utf-8")
    total_links = sum(len(by_menu[m]) for m in by_menu if m in INTERESTING_MENUS)
    print(f"  wrote {len(menus_out)} site menus ({total_links} links) -> {out_path.name}",
          file=sys.stderr)


def write_users(user_rows, author_uids, users_roles=None, roles=None):
    """
    Drupal 7 with open registration accumulated tens of thousands of
    spam-bot accounts (status=0, never logged in). Drop those; keep
    only real users that:
      - logged in at least once (login > 0)               OR
      - authored a published node (uid in author_uids)    OR
      - are uid 1 (the admin) or uid 0 (the anonymous user pseudo-row).
    """
    users_roles = users_roles or []
    roles = roles or []
    role_name = {r["rid"]: r["name"] for r in roles}
    user_role_names: dict[int, list[str]] = {}
    for ur in users_roles:
        user_role_names.setdefault(ur["uid"], []).append(
            role_name.get(ur["rid"], f"rid:{ur['rid']}")
        )

    real = []
    for u in user_rows:
        uid = u.get("uid") or 0
        login_ts = u.get("login") or 0
        is_real = (
            uid in (0, 1)
            or uid in author_uids
            or (u.get("status") == 1 and login_ts > 0)
        )
        if not is_real:
            continue
        real.append({
            "uid": uid,
            "name": u.get("name"),
            "mail": u.get("mail"),
            "created": u.get("created"),
            "access": u.get("access"),
            "login": login_ts,
            "status": u.get("status"),
            "language": u.get("language"),
            "timezone": u.get("timezone"),
            "picture_fid": u.get("picture"),
            "roles": sorted(user_role_names.get(uid, [])),
            "authored_pages": uid in author_uids,
        })
    real.sort(key=lambda r: r["uid"])
    out_path = CONTENT_DIR / "users.json"
    out_path.write_text(json.dumps(real, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"  wrote {len(real)} real users (filtered "
        f"{len(user_rows) - len(real)} spam rows) -> {out_path.name}",
        file=sys.stderr,
    )


# ---------------------------------------------------------------------------
# Writers for the additional content tables
# ---------------------------------------------------------------------------

def write_url_aliases(rows, nodes, nid_to_stem):
    """Output every URL alias plus a quick lookup table by nid."""
    by_pid = sorted(rows, key=lambda r: r.get("pid") or 0)
    by_nid: dict[int, list[dict]] = {}
    extras = []
    for r in by_pid:
        src = r.get("source") or ""
        m = re.fullmatch(r"node/(\d+)", src)
        rec = {
            "pid": r.get("pid"),
            "source": src,
            "alias": r.get("alias"),
            "language": r.get("language"),
        }
        if m:
            nid = int(m.group(1))
            rec["nid"] = nid
            rec["page_file"] = (nid_to_stem.get(nid) + ".html") if nid in nid_to_stem else None
            by_nid.setdefault(nid, []).append(rec)
        else:
            extras.append(rec)
    out = {
        "by_node": [
            {"nid": nid, "page_file": nid_to_stem.get(nid, "") + ".html",
             "title": (nodes.get(nid, {}).get("title") or "").strip(),
             "aliases": sorted({x["alias"] for x in entries})}
            for nid, entries in sorted(by_nid.items())
        ],
        "non_node_aliases": extras,
        "all": by_pid,
    }
    p = DATA_DIR / "url_aliases.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  wrote {len(by_pid)} url aliases ({len(by_nid)} pages) -> {p.name}",
          file=sys.stderr)


def write_node_types(rows):
    p = DATA_DIR / "node_types.json"
    p.write_text(json.dumps(sorted(rows, key=lambda r: r.get("type") or ""),
                            ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  wrote {len(rows)} node types -> {p.name}", file=sys.stderr)


def write_blocks(rows, alias_rewrite):
    """Custom HTML blocks (sidebar / footer text). Emits one .{html,md,json}
    triplet per block under content/blocks/, plus content/blocks_index.json."""
    blocks_dir = CONTENT_DIR / "blocks"
    blocks_dir.mkdir(parents=True, exist_ok=True)
    # Wipe stale block files
    for stale in blocks_dir.glob("*.*"):
        stale.unlink()

    index = []
    for r in sorted(rows, key=lambda x: x.get("bid") or 0):
        bid = r.get("bid") or 0
        info = (r.get("info") or "").strip() or f"block-{bid}"
        slug = slugify(info)
        stem = f"{int(bid):03d}-{slug}"
        body_html = r.get("body") or ""
        rewritten = alias_rewrite(rewrite_assets(body_html))
        md = html_to_markdown(rewritten)
        meta = {
            "bid": bid,
            "info": info,
            "format": r.get("format"),
            "slug": slug,
            "body_html_rewritten": rewritten,
            "body_html_raw": body_html,
            "body_markdown": md,
        }
        (blocks_dir / f"{stem}.html").write_text(
            f"<!DOCTYPE html>\n<html><head><meta charset=\"utf-8\">"
            f"<title>{html.escape(info)}</title></head>\n<body>\n"
            f"<h1>{html.escape(info)}</h1>\n{rewritten}\n</body></html>\n",
            encoding="utf-8",
        )
        (blocks_dir / f"{stem}.md").write_text(f"# {info}\n\n{md}", encoding="utf-8")
        (blocks_dir / f"{stem}.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        index.append({
            "bid": bid, "info": info, "slug": slug, "format": r.get("format"),
            "file_html": f"content/blocks/{stem}.html",
            "file_md": f"content/blocks/{stem}.md",
            "file_json": f"content/blocks/{stem}.json",
        })

    (CONTENT_DIR / "blocks_index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  wrote {len(index)} custom blocks -> content/blocks/", file=sys.stderr)


def write_page_fields(field_image, field_page_file, field_tags):
    def _strip(rows):
        return [{k: v for k, v in r.items()} for r in rows]
    (DATA_DIR / "page_field_image.json").write_text(
        json.dumps(_strip(field_image), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (DATA_DIR / "page_field_page_file.json").write_text(
        json.dumps(_strip(field_page_file), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (DATA_DIR / "page_field_tags.json").write_text(
        json.dumps(_strip(field_tags), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        f"  wrote {len(field_image)} field_image, {len(field_page_file)} field_page_file, "
        f"{len(field_tags)} field_tags -> data/page_field_*.json",
        file=sys.stderr,
    )


def write_taxonomy(vocab, terms, hierarchy, index):
    parent_of: dict[int, int] = {}
    for r in hierarchy:
        if r.get("parent"):
            parent_of[r["tid"]] = r["parent"]
    out = {
        "vocabularies": sorted(vocab, key=lambda r: r.get("vid") or 0),
        "terms": [
            {
                **r,
                "parent_tid": parent_of.get(r["tid"]),
            }
            for r in sorted(terms, key=lambda r: r.get("tid") or 0)
        ],
        "node_tags": sorted(index, key=lambda r: (r.get("nid") or 0, r.get("tid") or 0)),
    }
    p = DATA_DIR / "taxonomy.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"  wrote {len(vocab)} vocabularies, {len(terms)} terms, "
        f"{len(index)} node->tag links -> {p.name}",
        file=sys.stderr,
    )


def write_comments(comment_rows, comment_bodies):
    body_by_id = {b["entity_id"]: b for b in comment_bodies}
    out = []
    for c in sorted(comment_rows, key=lambda r: r.get("cid") or 0):
        cid = c.get("cid")
        b = body_by_id.get(cid, {})
        out.append({
            "cid": cid,
            "pid": c.get("pid"),
            "nid": c.get("nid"),
            "uid": c.get("uid"),
            "subject": c.get("subject"),
            "name": c.get("name"),
            "mail": c.get("mail"),
            "homepage": c.get("homepage"),
            "hostname": c.get("hostname"),
            "status": c.get("status"),
            "thread": c.get("thread"),
            "language": c.get("language"),
            "created": c.get("created"),
            "changed": c.get("changed"),
            "body_value": b.get("comment_body_value"),
            "body_format": b.get("comment_body_format"),
        })
    p = DATA_DIR / "comments.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  wrote {len(out)} comments -> {p.name}", file=sys.stderr)


def write_roles(roles, role_permissions):
    perms_by_rid: dict[int, list[str]] = {}
    for rp in role_permissions:
        perms_by_rid.setdefault(rp["rid"], []).append(rp["permission"])
    out = []
    for r in sorted(roles, key=lambda r: r.get("rid") or 0):
        out.append({
            "rid": r.get("rid"),
            "name": r.get("name"),
            "weight": r.get("weight"),
            "permissions": sorted(perms_by_rid.get(r["rid"], [])),
        })
    p = DATA_DIR / "roles.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"  wrote {len(out)} roles ({sum(len(r['permissions']) for r in out)} permissions) "
        f"-> {p.name}",
        file=sys.stderr,
    )


def write_contact(rows):
    p = DATA_DIR / "contact_categories.json"
    p.write_text(
        json.dumps(sorted(rows, key=lambda r: r.get("weight") or 0),
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"  wrote {len(rows)} contact categories -> {p.name}", file=sys.stderr)


def write_text_formats(formats, filters):
    filters_by_format: dict[str, list[dict]] = {}
    for f in filters:
        filters_by_format.setdefault(f["format"], []).append(f)
    out = []
    for fmt in sorted(formats, key=lambda r: r.get("weight") or 0):
        out.append({
            "format": fmt.get("format"),
            "name": fmt.get("name"),
            "status": fmt.get("status"),
            "cache": fmt.get("cache"),
            "weight": fmt.get("weight"),
            "filters": sorted(
                filters_by_format.get(fmt["format"], []),
                key=lambda r: r.get("weight") or 0,
            ),
        })
    p = DATA_DIR / "text_formats.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  wrote {len(out)} text formats -> {p.name}", file=sys.stderr)


def write_file_usage(rows):
    p = DATA_DIR / "file_usage.json"
    p.write_text(
        json.dumps(sorted(rows, key=lambda r: (r.get("fid") or 0, r.get("module") or "")),
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"  wrote {len(rows)} file usage links -> {p.name}", file=sys.stderr)


def write_files_managed(file_rows):
    cleaned = []
    for r in file_rows:
        cleaned.append({
            "fid": r.get("fid"),
            "uid": r.get("uid"),
            "filename": r.get("filename"),
            "uri": r.get("uri"),
            "filemime": r.get("filemime"),
            "filesize": r.get("filesize"),
            "status": r.get("status"),
            "timestamp": r.get("timestamp"),
        })
    cleaned.sort(key=lambda r: r.get("fid") or 0)
    out_path = DATA_DIR / "files_managed.json"
    out_path.write_text(json.dumps(cleaned, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  wrote {len(cleaned)} file rows -> {out_path.name}", file=sys.stderr)


def write_variables(variables):
    """
    Write all decoded Drupal `variable` rows to data/drupal_variables.json,
    plus a curated content/site_variables.json with the human-relevant ones.
    """
    # Decoded variables can contain bytes, sets, etc. Coerce.
    def _safe(v):
        if isinstance(v, bytes):
            try:
                return v.decode("utf-8")
            except UnicodeDecodeError:
                return v.hex()
        if isinstance(v, dict):
            return {str(k): _safe(x) for k, x in v.items()}
        if isinstance(v, list):
            return [_safe(x) for x in v]
        return v

    safe_vars = {k: _safe(v) for k, v in sorted(variables.items())}
    out_all = DATA_DIR / "drupal_variables.json"
    out_all.write_text(json.dumps(safe_vars, ensure_ascii=False, indent=2), encoding="utf-8")

    curated_keys = (
        "site_name", "site_slogan", "site_mail", "site_frontpage",
        "site_default_country", "site_404", "site_403", "theme_default",
        "admin_theme", "user_default_timezone", "date_default_timezone",
        "user_register", "user_email_verification",
    )
    curated = {k: safe_vars[k] for k in curated_keys if k in safe_vars}
    out_curated = CONTENT_DIR / "site_variables.json"
    out_curated.write_text(json.dumps(curated, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        f"  wrote {len(safe_vars)} variables -> data/{out_all.name}, "
        f"{len(curated)} curated -> content/{out_curated.name}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
