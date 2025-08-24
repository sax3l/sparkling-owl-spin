# SOS (Sparkling Owl Spin) Templates

Detta är mallar för crawling-systemet. Varje YAML-fil definierar hur en specifik typ av webbplats ska crawlas.

## Template Format

### Grundstruktur
```yaml
name: "Template namn"
start_urls:
  - "https://example.com/start"

follow:
  - selector: "a.link"
    type: "generic|detail|pagination"
    match: "URL-filter (optional)"

extract:
  - name: "field_name"
    selector: "CSS selector"
    type: "text|html|attr"
    attr: "attribute name (för attr type)"
    regex: "extraction regex (optional)"

render:
  enabled: true/false

actions:
  scroll: true/false
  scroll_max: antal
  wait_ms: millisekunder
  click_selector: "selector för element att klicka"

limits:
  max_pages: max antal sidor
  max_depth: max crawl-djup

respect_robots: true/false
delay_ms: fördröjning mellan requests
```

### Använda mallar

Via CLI:
```bash
# Skapa template
sos create-template "My Template" templates/my-template.yaml

# Lista templates  
sos list-templates

# Starta crawl
sos start-job 1 --output results.csv
```

Via API:
```bash
# POST /templates
curl -X POST http://localhost:8080/templates \
  -H "Content-Type: application/json" \
  -d '{"name": "Test", "yaml": "..."}'

# POST /jobs
curl -X POST http://localhost:8080/jobs \
  -H "Content-Type: application/json" \
  -d '{"template_id": 1}'
```
