from typing import Optional
from datetime import datetime

def parse_datetime(s: Optional[str]) -> Optional[datetime]:
    if s is None:
        return None 
    # Check whether it has Z at the end
    add = 'Z' if s.endswith("Z") else ''
    try:
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%f"+add)
    except ValueError:
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S"+add)

def remove_unsubscribe(text: str) -> str:
    # From google groups
    unsubs = [
        """To unsubscribe from this group and stop receiving emails from it, send an email to""",
        """You received this message because you are subscribed to the""",
    ]
    for unsub in unsubs:
        if text.find(unsub) != -1:
            text = text[:text.find(unsub)]
    text = text.strip()

    # Make sure there's no \n\n as well.
    while "\n\n" in text:
        text = text.replace("\n\n", "\n")
    return text

import re

def to_richtext(text: str) -> str:
    text = text.strip()
    # Convert markdown links to HTML links
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    # Split the text into lines
    lines = text.split('\n')

    html_lines = []
    in_list = False
    for line in lines:
        # Convert bullet points to list items
        if line.startswith('- '):
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            html_lines.append(f'<li>{line[2:]}</li>')
        else:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            html_lines.append(f'<div>{line}</div>')

    # Close the list tag if the text ends with a bullet point
    if in_list:
        html_lines.append('</ul>')

    return ''.join(html_lines)