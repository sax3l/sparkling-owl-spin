"""
Test template runtime functionality - extractor -> writer pipeline.
"""
import json
from pathlib import Path
import pytest
import yaml

from src.scraper.dsl.schema import ScrapingTemplate as TemplateDefinition
from src.scraper.template_runtime import (
    load_template,
    extract_fields_from_html,
    InlineFetcher,
    JsonlWriter,
    run_template_over_urls,
)

VEHICLE_TEMPLATE = """
template_id: vehicle_detail_v1
version: 1.0.0
domain: synthetic.local
entity: vehicle
url_pattern: "^https://synthetic\\.local/vehicle/[A-Z0-9]{3}\\d{3}$"
requires_js: false
fields:
  - name: registration_number
    selector: "h1 span.reg"
    selector_type: css
    attr: text
    required: true
    transforms:
      - type: strip
      - type: upper
    validators:
      - type: regex
        pattern: "^[A-ZÅÄÖ]{3}\\d{3}$"

  - name: vin
    selector: "//div[@id='tech']/dl/dd[@data-key='vin']"
    selector_type: xpath
    attr: text
    transforms:
      - type: strip
      - type: null_if
        equals: "N/A"
    validators:
      - type: length_range
        min: 11
        max: 20

  - name: make
    selector: "div.kv .make"
    selector_type: css
    attr: text
    transforms:
      - type: strip
      - type: title

  - name: model
    selector: "div.kv .model"
    selector_type: css
    attr: text
    transforms:
      - type: strip

  - name: model_year
    selector: "//div[@class='kv']//span[@class='year']"
    selector_type: xpath
    attr: text
    transforms:
      - type: strip
      - type: to_int
    validators:
      - type: numeric_range
        min: 1950
        max: 2100

  - name: features
    selector: "ul.features li"
    selector_type: css
    attr: text
    multi: true
    transforms:
      - type: strip
      - type: normalize_whitespace

postprocessors:
  - type: ensure_fields
    fields: ["make", "model", "model_year"]
"""

HTML_ABC123 = """
<!doctype html>
<html>
  <body>
    <h1>Fordon <span class="reg">abc123</span></h1>
    <div class="kv"><span class="make">volvo</span> <span class="model">xc60</span> <span class="year">2021</span></div>
    <div id="tech">
      <dl>
        <dt>VIN</dt><dd data-key="vin">YV1UZ7AL1M1234567</dd>
      </dl>
    </div>
    <table id="emissions">
      <tr><td>CO₂ (WLTP)</td><td>148 g/km</td></tr>
    </table>
    <div class="inspections">
      <span class="next">2025-06-01</span>
    </div>
    <ul class="features">
      <li> adaptiv farthållare </li>
      <li>lane assist</li>
    </ul>
  </body>
</html>
"""

HTML_DEF456 = """
<!doctype html>
<html>
  <body>
    <h1>Fordon <span class="reg">DEF456</span></h1>
    <div class="kv"><span class="make">Toyota</span> <span class="model">Corolla</span> <span class="year">2019</span></div>
    <div id="tech"><dl><dt>VIN</dt><dd data-key="vin">N/A</dd></dl></div>
    <ul class="features"><li>bluetooth</li></ul>
  </body>
</html>
"""

def test_template_pydantic_validation(tmp_path):
    # skriv tempfil
    tpath = tmp_path / "vehicle_detail_v1.yaml"
    tpath.write_text(VEHICLE_TEMPLATE, encoding="utf-8")
    tpl = load_template(tpath)
    assert isinstance(tpl, TemplateDefinition)
    assert tpl.template_id == "vehicle_detail_v1"
    assert len(tpl.fields) >= 5

def test_single_extraction_html():
    # validera extraktion mot en sida
    tpl = TemplateDefinition.model_validate(yaml.safe_load(VEHICLE_TEMPLATE))

    row = extract_fields_from_html(HTML_ABC123, tpl, url="https://synthetic.local/vehicle/ABC123")
    assert row["registration_number"] == "ABC123"
    assert row["make"] == "Volvo"
    assert row["model"] == "xc60"
    assert row["model_year"] == 2021
    assert row["features"] == ["adaptiv farthållare", "lane assist"]
    assert row["_template_id"] == "vehicle_detail_v1"

def test_run_over_multiple_urls(tmp_path):
    tpl = TemplateDefinition.model_validate(yaml.safe_load(VEHICLE_TEMPLATE))
    inline = InlineFetcher({
        "https://synthetic.local/vehicle/ABC123": HTML_ABC123,
        "https://synthetic.local/vehicle/DEF456": HTML_DEF456,
    })
    out = tmp_path / "out.jsonl"
    writer = JsonlWriter(out)

    stats = run_template_over_urls(
        urls=[
            "https://synthetic.local/vehicle/ABC123",
            "https://synthetic.local/vehicle/DEF456"
        ],
        template=tpl,
        fetcher=inline,
        writer=writer
    )
    assert stats["processed"] == 2
    # DEF456 saknar giltigt VIN men det är inte required i mallen
    lines = out.read_text(encoding="utf-8").strip().splitlines()
    rows = [json.loads(x) for x in lines]
    assert any(r["registration_number"] == "ABC123" for r in rows)
    assert any(r["registration_number"] == "DEF456" for r in rows)