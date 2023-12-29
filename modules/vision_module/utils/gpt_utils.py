import re


def extract_content(tag, string):
    pattern = f"<{tag}>(.*?)</{tag}>"
    match = re.search(pattern, string, re.DOTALL)
    return match.group(1).strip() if match else None
