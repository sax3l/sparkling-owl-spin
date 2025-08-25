import re
from typing import Dict, Optional

class TemplateDetector:
    """
    Identifies the template of a page based on a set of predefined URL patterns.
    """
    def __init__(self, rules: Dict[str, str]):
        """
        Initializes the detector with a dictionary of rules.
        Args:
            rules: A dictionary where keys are template names and values are regex patterns.
                   Example: {"vehicle_detail": "/fordon/[A-Z0-9-]+"}
        """
        self.compiled_rules = {
            template_name: re.compile(pattern)
            for template_name, pattern in rules.items()
        }

    def classify(self, url: str) -> Optional[str]:
        """
        Classifies a URL against the loaded rules and returns the matching template name.
        """
        for template_name, pattern in self.compiled_rules.items():
            if pattern.search(url):
                return template_name
        return None