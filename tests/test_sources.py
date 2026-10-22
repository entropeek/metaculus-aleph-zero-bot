"""Offline tests for resolution-source page cleaning."""
import io

from aleph_bot import sources

PAGE = ('<html><header>Site banner</header><nav><a>Menu</a></nav>'
        '<div data-mw=\'{"a":"<b>x</b>"}\'>Rate: 4.3 percent</div><footer>Contact</footer></html>')


def test_page_text_keeps_content_only(monkeypatch):
    # Fake download: page with menus, footer and a '>' inside a quoted attribute.
    monkeypatch.setattr(sources.urllib.request, "urlopen", lambda *a, **k: io.BytesIO(PAGE.encode()))
    assert sources._page_text("https://example.org") == "Rate: 4.3 percent"
