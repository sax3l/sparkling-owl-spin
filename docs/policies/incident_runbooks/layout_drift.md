# Runbook: Website Layout Drift Detected

This runbook details the steps to take when data quality metrics drop significantly for a specific template, indicating a website layout change.

## 1. Triage
- **Identify the affected template and domain** from the data quality alerts.
- **Review the DQ metrics** to see which fields are failing to extract.

## 2. Immediate Actions
- **Pause all scrape jobs** using the affected template.
- **Fetch a sample raw HTML page** for manual inspection.

## 3. Investigation
- **Compare the new HTML structure** with the selectors (CSS/XPath) in the template file.
- **Identify the changes** that broke the selectors.

## 4. Resolution
- **Update the template file** with the new, correct selectors.
- **Test the updated template** against the sample HTML.
- **Resume the scrape jobs** with the new template version.