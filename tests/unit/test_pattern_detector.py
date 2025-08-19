import pytest
# Placeholder for pattern detector
def find_repeating(html, container, item):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    container_el = soup.select_one(container)
    if not container_el:
        return type('obj', (object,), {'count': 0})()
    items = container_el.select(item)
    return type('obj', (object,), {'count': len(items)})()


@pytest.mark.unit
def test_find_repeating_simple():
    html = "<ul><li>A</li><li>B</li><li>C</li></ul>"
    r = find_repeating(html, container="ul", item="li")
    assert r.count == 3