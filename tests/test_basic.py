import asyncio
from types import SimpleNamespace
from fastapi.testclient import TestClient

from rockauto import rockauto_api, search_part_by_number

client = TestClient(rockauto_api)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data.get("message") == "Welcome to the RockAuto API"


def test_search_part_by_number_mocked(monkeypatch):
    """Ensure part number search parses basic details without network"""

    def fake_get(url, *args, **kwargs):
        if "partsearch" in url:
            html = (
                "<table>"
                "<tbody class='listing-inner'>"
                "<tr>"
                "<td><span class='listing-final-partnumber'>12345</span></td>"
                "<td><span class='listing-final-manufacturer'>TESTCO</span></td>"
                "<td><a class='ra-btn-moreinfo' href='https://example.com/info'></a></td>"
                "</tr>"
                "</tbody>"
                "</table>"
            )
            return SimpleNamespace(text=f"<html><body>{html}</body></html>")
        else:
            html = "<section aria-label='Warranty Information'>Lifetime</section>"
            return SimpleNamespace(text=f"<html><body>{html}</body></html>")

    monkeypatch.setattr("rockauto.requests.get", fake_get)
    results = asyncio.run(search_part_by_number("12345"))

    assert results == [
        {
            "manufacturer": "TESTCO",
            "part_number": "12345",
            "extra_details": {"Warranty Information": "Lifetime"},
        }
    ]
