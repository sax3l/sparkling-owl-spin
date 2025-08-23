import re

text = "Pris: 12 345 kr"
pattern = r"(\d[\d\s]+)"
match = re.search(pattern, text)
if match:
    result = match.group(1)
    print(f"Raw match: '{result}'")
    print(f"Stripped match: '{result.strip()}'")
    print(f"Length: {len(result)}, stripped length: {len(result.strip())}")
