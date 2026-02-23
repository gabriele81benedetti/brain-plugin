#!/usr/bin/env python3
"""
HTML to Google Slides Converter.

Converts any HTML file or URL into an editable Google Slides presentation
using the company's branded template. Extracts semantic sections, text,
lists, and tables as native, editable Slides elements.

Usage:
    python3 data/html_to_slides.py <html-file-or-url> [--title "Title"] [--out <path>]

Examples:
    python3 data/html_to_slides.py data/Report-GoogleAds/fiko.html
    python3 data/html_to_slides.py https://example.com/report.html --title "Q1 Report"
    python3 data/html_to_slides.py report.html --out clients/acme/reports/slides.txt

Requirements (one-time setup):
    Run /EnableGooglePresentation in Claude Code for guided setup.
    Or manually:
      1. https://console.cloud.google.com → Enable Slides + Drive API
      2. Create OAuth 2.0 Client ID → Desktop App → Download JSON
      3. Save as ~/.google-slides-credentials.json && chmod 600 ~/.google-slides-credentials.json
"""

import sys
import re
import argparse
import warnings
warnings.filterwarnings("ignore")

from pathlib import Path
from urllib.request import urlopen

try:
    from bs4 import BeautifulSoup, NavigableString
except ImportError:
    print("❌  Missing dependency: pip install beautifulsoup4")
    sys.exit(1)

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ── Auth ────────────────────────────────────────────────────────────────────────
SCOPES     = ["https://www.googleapis.com/auth/presentations",
               "https://www.googleapis.com/auth/drive"]
CREDS_PATH = Path.home() / ".google-slides-credentials.json"
TOKEN_PATH = Path.home() / ".google-slides-token.json"

# ── Template ───────────────────────────────────────────────────────────────────
# Company branded template — preserves master slides, layouts, and fonts.
# To use your own template: pass --template "YOUR_TEMPLATE_ID" when running.
SLIDES_TEMPLATE_ID = "1Cy0pGP-Cnp8x-hNcDdjjvZAo9ksuUxwTcSZOIdqTwxQ"

# ── Design constants ───────────────────────────────────────────────────────────
TEAL   = {"red": 0.227, "green": 0.765, "blue": 0.824}   # #3AC3D2
INK    = {"red": 0.110, "green": 0.110, "blue": 0.110}   # #1C1C1C
GRAY   = {"red": 0.349, "green": 0.349, "blue": 0.349}   # #595959
WHITE  = {"red": 1.0,   "green": 1.0,   "blue": 1.0}
WARM   = {"red": 0.933, "green": 0.933, "blue": 0.933}   # #EEEEEE
TEAL_L = {"red": 0.878, "green": 0.969, "blue": 0.976}   # #E0F7FA
FONT   = "Poppins"

MAX_BODY_CHARS = 900   # characters per content slide before truncation
MAX_TABLE_ROWS = 20    # max rows per table slide

def emu(inches): return int(inches * 914400)


# ── OAuth ──────────────────────────────────────────────────────────────────────
def authenticate():
    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDS_PATH.exists():
                print(f"\n❌  Credentials not found at {CREDS_PATH}")
                print("Run /EnableGooglePresentation in Claude Code for guided setup.\n")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_PATH), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_PATH.write_text(creds.to_json())
        print(f"✅  Token saved → {TOKEN_PATH}")
    return build("slides", "v1", credentials=creds), build("drive", "v3", credentials=creds)


# ── Deck builder ───────────────────────────────────────────────────────────────
class Deck:
    """Minimal fluent builder for Google Slides presentations via batch API."""

    def __init__(self, service, title, template_id=None, drive_svc=None):
        self.svc = service
        if template_id and drive_svc:
            copy = drive_svc.files().copy(
                fileId=template_id, body={"name": title}
            ).execute()
            self.pid = copy["id"]
            pres = service.presentations().get(presentationId=self.pid).execute()
            self._existing = [s["objectId"] for s in pres.get("slides", [])]
            self.layouts = {
                l.get("layoutProperties", {}).get("displayName", "").strip(): l["objectId"]
                for l in pres.get("layouts", [])
            }
        else:
            pres = service.presentations().create(body={"title": title}).execute()
            self.pid = pres["presentationId"]
            self._existing = [pres["slides"][0]["objectId"]]
            self.layouts = {}
        self.reqs = []
        self._n = 0

    def _id(self, p="o"):
        self._n += 1
        return f"{p}_{self._n:04d}"

    def flush(self):
        if self.reqs:
            self.svc.presentations().batchUpdate(
                presentationId=self.pid, body={"requests": self.reqs}
            ).execute()
            self.reqs = []

    def delete_template_slides(self):
        for sid in self._existing:
            self.reqs.append({"deleteObject": {"objectId": sid}})

    def url(self):
        return f"https://docs.google.com/presentation/d/{self.pid}/edit"

    def slide(self, layout_name=None, index=None):
        sid = self._id("sl")
        layout_id = self.layouts.get(layout_name) if layout_name else None
        req = {"createSlide": {
            "objectId": sid,
            "slideLayoutReference": (
                {"layoutId": layout_id} if layout_id
                else {"predefinedLayout": "BLANK"}
            ),
        }}
        if index is not None:
            req["createSlide"]["insertionIndex"] = index
        self.reqs.append(req)
        return sid

    def text(self, slide_id, txt, l, t, w, h,
             size=10, bold=False, color=None, align="START", font=None, italic=False):
        oid = self._id("tx")
        color = color or INK
        font = font or FONT
        _AM = {"LEFT": "START", "RIGHT": "END"}
        align = _AM.get(align, align)
        self.reqs += [
            {"createShape": {
                "objectId": oid, "shapeType": "TEXT_BOX",
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {"width":  {"magnitude": emu(w), "unit": "EMU"},
                             "height": {"magnitude": emu(h), "unit": "EMU"}},
                    "transform": {"scaleX": 1, "scaleY": 1, "unit": "EMU",
                                  "translateX": emu(l), "translateY": emu(t)},
                }
            }},
            {"insertText": {"objectId": oid, "text": txt, "insertionIndex": 0}},
            {"updateTextStyle": {
                "objectId": oid,
                "style": {"fontSize": {"magnitude": size, "unit": "PT"},
                          "bold": bold, "italic": italic,
                          "foregroundColor": {"opaqueColor": {"rgbColor": color}},
                          "fontFamily": font},
                "fields": "fontSize,bold,italic,foregroundColor,fontFamily",
                "textRange": {"type": "ALL"},
            }},
            {"updateParagraphStyle": {
                "objectId": oid,
                "style": {"alignment": align},
                "fields": "alignment",
                "textRange": {"type": "ALL"},
            }},
        ]
        return oid

    def rect(self, slide_id, l, t, w, h, fill):
        oid = self._id("r")
        self.reqs += [
            {"createShape": {
                "objectId": oid, "shapeType": "RECTANGLE",
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {"width":  {"magnitude": emu(w), "unit": "EMU"},
                             "height": {"magnitude": emu(h), "unit": "EMU"}},
                    "transform": {"scaleX": 1, "scaleY": 1, "unit": "EMU",
                                  "translateX": emu(l), "translateY": emu(t)},
                }
            }},
            {"updateShapeProperties": {
                "objectId": oid,
                "shapeProperties": {
                    "shapeBackgroundFill": {"solidFill": {"color": {"rgbColor": fill}}},
                    "outline": {"outlineFill": {"solidFill": {"color": {"rgbColor": fill}}}},
                },
                "fields": "shapeBackgroundFill,outline",
            }},
        ]
        return oid

    def table(self, slide_id, rows, cols, l, t, w, h):
        oid = self._id("tbl")
        self.reqs.append({"createTable": {
            "objectId": oid,
            "elementProperties": {
                "pageObjectId": slide_id,
                "size": {"width":  {"magnitude": emu(w), "unit": "EMU"},
                         "height": {"magnitude": emu(h), "unit": "EMU"}},
                "transform": {"scaleX": 1, "scaleY": 1, "unit": "EMU",
                              "translateX": emu(l), "translateY": emu(t)},
            },
            "rows": rows, "columns": cols,
        }})
        return oid

    def cell(self, tbl_id, row, col, txt,
             bold=False, size=8, color=None, bg=None, align="START"):
        color = color or INK
        _AM = {"LEFT": "START", "RIGHT": "END"}
        align = _AM.get(align, align)

        # Only add text and styles if cell has content
        if txt and txt.strip():
            self.reqs += [
                {"insertText": {
                    "objectId": tbl_id,
                    "cellLocation": {"rowIndex": row, "columnIndex": col},
                    "text": txt, "insertionIndex": 0,
                }},
                {"updateTextStyle": {
                    "objectId": tbl_id,
                    "cellLocation": {"rowIndex": row, "columnIndex": col},
                    "style": {"fontSize": {"magnitude": size, "unit": "PT"},
                              "bold": bold,
                              "foregroundColor": {"opaqueColor": {"rgbColor": color}}},
                    "fields": "fontSize,bold,foregroundColor",
                    "textRange": {"type": "ALL"},
                }},
                {"updateParagraphStyle": {
                    "objectId": tbl_id,
                    "cellLocation": {"rowIndex": row, "columnIndex": col},
                    "style": {"alignment": align},
                    "fields": "alignment",
                    "textRange": {"type": "ALL"},
                }},
            ]
        if bg:
            self.reqs.append({"updateTableCellProperties": {
                "objectId": tbl_id,
                "tableRange": {"location": {"rowIndex": row, "columnIndex": col},
                               "rowSpan": 1, "columnSpan": 1},
                "tableCellProperties": {"tableCellBackgroundFill": {
                    "solidFill": {"color": {"rgbColor": bg}}}},
                "fields": "tableCellBackgroundFill",
            }})

    def header_bar(self, slide_id, title, subtitle=None):
        """Standard content slide header (aligns with 'Titolo e testo' layout)."""
        self.text(slide_id, title, 2.45, 0.08, 7.2, 0.56, size=22, bold=True, color=INK)
        if subtitle:
            self.text(slide_id, subtitle, 2.45, 0.66, 7.2, 0.24, size=9, color=GRAY)
        self.footer(slide_id)

    def footer(self, slide_id, label="Search On Consulting · Confidential"):
        self.rect(slide_id, 0, 5.38, 10, 0.245, INK)
        self.text(slide_id, label, 0.3, 5.40, 9.4, 0.20, size=7, color=GRAY, align="END")


# ── HTML parsing ───────────────────────────────────────────────────────────────

def load_html(source):
    """Load HTML from file path or URL."""
    if source.startswith("http://") or source.startswith("https://"):
        with urlopen(source) as r:
            raw = r.read().decode("utf-8", errors="replace")
    else:
        raw = Path(source).read_text(encoding="utf-8", errors="replace")
    return BeautifulSoup(raw, "html.parser")


def clean_text(node):
    return re.sub(r"\s+", " ", node.get_text(separator=" ", strip=True)).strip()


def node_to_text(node):
    """Recursively convert a BS4 node to plain text with minimal formatting."""
    # Handle NavigableString (plain text nodes)
    if isinstance(node, NavigableString):
        text = re.sub(r"\s+", " ", str(node)).strip()
        return text if text else ""

    # Handle tags with children
    lines = []
    for child in node.children:
        if not hasattr(child, "name"):
            t = re.sub(r"\s+", " ", str(child)).strip()
            if t:
                lines.append(t)
            continue
        tag = child.name
        if tag in ("script", "style", "noscript", "svg", "canvas", "figure"):
            continue
        elif tag in ("h2", "h3", "h4", "h5", "h6"):
            t = clean_text(child)
            if t:
                lines.append(f"\n{t}\n")
        elif tag == "p":
            t = clean_text(child)
            if t:
                lines.append(t)
        elif tag in ("ul", "ol"):
            for li in child.find_all("li", recursive=False):
                t = clean_text(li)
                if t:
                    lines.append(f"• {t}")
        elif tag in ("br",):
            pass
        elif tag == "table":
            pass   # tables are handled separately
        elif tag in ("div", "section", "article", "main", "aside",
                     "header", "blockquote", "figcaption"):
            lines.append(node_to_text(child))
        else:
            t = clean_text(child)
            if t:
                lines.append(t)
    joined = " ".join(filter(None, lines))
    return re.sub(r"\s{3,}", "  ", joined).strip()


def extract_table_data(table_node):
    rows = []
    for tr in table_node.find_all("tr"):
        cells = [clean_text(td) for td in tr.find_all(["th", "td"])]
        if any(c for c in cells):
            rows.append(cells)
    return rows


def extract_sections(soup):
    """
    Split HTML into logical sections. Returns list of:
      {"title": str, "body": str, "tables": [[row]]}

    Strategy priority:
      1. <section> / <article> tags (semantic HTML)
      2. Split by <h2> headings
      3. Fallback: entire body as one section
    """
    sections = []

    semantic = soup.find_all(["section", "article"])
    if len(semantic) >= 2:
        for node in semantic:
            node_copy = BeautifulSoup(str(node), "html.parser")
            heading = node_copy.find(["h1", "h2", "h3", "h4"])
            title = clean_text(heading) if heading else ""
            tables = [extract_table_data(t) for t in node_copy.find_all("table")]
            for t in node_copy.find_all("table"):
                t.decompose()
            if heading:
                heading.decompose()
            body = node_to_text(node_copy).strip()
            sections.append({"title": title, "body": body, "tables": tables})
        return sections

    body_node = soup.find("body") or soup
    h2_tags = body_node.find_all(["h2", "h3"])
    if h2_tags:
        for h in h2_tags:
            title = clean_text(h)
            content_nodes = []
            for sib in h.next_siblings:
                if hasattr(sib, "name") and sib.name in ("h2", "h3"):
                    break
                content_nodes.append(sib)
            tables = []
            body_parts = []
            for n in content_nodes:
                if not hasattr(n, "name"):
                    t = re.sub(r"\s+", " ", str(n)).strip()
                    if t:
                        body_parts.append(t)
                    continue
                if n.name == "table":
                    tables.append(extract_table_data(n))
                elif n.name not in ("script", "style"):
                    body_parts.append(node_to_text(n))
            body_text = " ".join(filter(None, body_parts)).strip()
            sections.append({"title": title, "body": body_text, "tables": tables})
        return sections

    # Fallback
    title_node = soup.find("h1")
    title = clean_text(title_node) if title_node else (
        soup.title.string.strip() if soup.title else "Document"
    )
    tables = [extract_table_data(t) for t in body_node.find_all("table")]
    for t in body_node.find_all("table"):
        t.decompose()
    body_text = node_to_text(body_node).strip()
    sections.append({"title": title, "body": body_text, "tables": tables})
    return sections


def get_cover_info(soup):
    h1 = soup.find("h1")
    title = clean_text(h1) if h1 else (
        soup.title.string.strip() if soup.title else "Presentation"
    )
    meta = soup.find("meta", attrs={"name": "description"})
    if meta and meta.get("content"):
        subtitle = meta["content"].strip()[:160]
    else:
        first_p = soup.find("p")
        subtitle = clean_text(first_p)[:160] if first_p else ""
    return title, subtitle


# ── Slide builders ─────────────────────────────────────────────────────────────

def build_cover(deck, title, subtitle, cover_layout="Copertina"):
    sid = deck.slide(cover_layout, index=0)
    deck.flush()
    deck.text(sid, title[:120], 0.5, 1.6, 9.0, 1.4,
              size=34, bold=True, color=WHITE, align="CENTER")
    if subtitle:
        deck.text(sid, subtitle, 1.0, 3.2, 8.0, 0.7,
                  size=12, color=TEAL_L, align="CENTER")
    return sid


def build_content_slide(deck, index, title, body, subtitle=None, content_layout="Titolo e testo"):
    sid = deck.slide(content_layout, index=index)
    deck.flush()
    deck.header_bar(sid, title[:100], subtitle)
    if body:
        body_txt = body[:MAX_BODY_CHARS]
        if len(body) > MAX_BODY_CHARS:
            body_txt += "…"
        deck.text(sid, body_txt, 2.45, 1.0, 7.2, 4.2, size=9, color=INK)
    return sid


def build_table_slide(deck, index, title, table_rows, content_layout="Titolo e testo"):
    rows = table_rows[:MAX_TABLE_ROWS]
    if not rows:
        return
    cols = max((len(r) for r in rows), default=1)
    cols = max(cols, 1)

    sid = deck.slide(content_layout, index=index)
    deck.flush()
    deck.header_bar(sid, title[:100])

    tbl_h = min(4.1, len(rows) * 0.30)
    tbl_id = deck.table(sid, len(rows), cols, l=0.3, t=1.0, w=9.4, h=tbl_h)
    deck.flush()   # table must be created before cells can be filled

    for ri, row in enumerate(rows):
        is_header = ri == 0
        bg = TEAL if is_header else (WARM if ri % 2 == 0 else None)
        txt_color = WHITE if is_header else INK
        for ci in range(cols):
            cell_txt = row[ci] if ci < len(row) else ""
            deck.cell(tbl_id, ri, ci, cell_txt[:80],
                      bold=is_header, size=8, color=txt_color, bg=bg)
    return sid


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Convert any HTML file or URL to an editable Google Slides presentation"
    )
    parser.add_argument("source", help="HTML file path or URL")
    parser.add_argument("--title",    help="Override presentation title")
    parser.add_argument("--out",      help="Write URL to this file path")
    parser.add_argument("--template", default=SLIDES_TEMPLATE_ID,
                        help="Google Slides template ID (default: company template)")
    parser.add_argument("--cover-layout", default="Copertina",
                        help="Layout name for cover slide (default: 'Copertina' for Italian, use 'Title Slide' for English)")
    parser.add_argument("--content-layout", default="Titolo e testo",
                        help="Layout name for content slides (default: 'Titolo e testo' for Italian, use 'Title and Body' for English)")
    args = parser.parse_args()

    print("🔐  Authenticating…")
    slides_svc, drive_svc = authenticate()

    print(f"📄  Loading: {args.source}")
    soup = load_html(args.source)

    cover_title, cover_subtitle = get_cover_info(soup)
    pres_title = args.title or cover_title

    print("📐  Extracting sections…")
    sections = extract_sections(soup)
    n_tables = sum(len(s["tables"]) for s in sections)
    print(f"    {len(sections)} section(s), {n_tables} table(s)")

    print(f"🎨  Creating presentation: '{pres_title}'")
    deck = Deck(slides_svc, pres_title, template_id=args.template, drive_svc=drive_svc)
    deck.delete_template_slides()
    deck.flush()

    idx = 0
    build_cover(deck, cover_title, cover_subtitle, cover_layout=args.cover_layout)
    deck.flush()
    idx += 1

    for i, sec in enumerate(sections, 1):
        title = sec["title"] or f"Section {i}"
        body  = sec["body"]
        tables = sec["tables"]

        if body:
            print(f"    [{i}/{len(sections)}] {title[:50]}")
            build_content_slide(deck, idx, title, body, content_layout=args.content_layout)
            deck.flush()
            idx += 1

        for tbl in tables:
            if len(tbl) > 1:
                build_table_slide(deck, idx, title, tbl, content_layout=args.content_layout)
                deck.flush()
                idx += 1

    url = deck.url()
    print(f"\n✅  Done! Total slides: {idx}")
    print(f"🔗  {url}\n")

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(url)
        print(f"    URL saved → {args.out}")

    return url


if __name__ == "__main__":
    main()
