from typing import Optional
from datetime import datetime
import re

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

    text = text.replace("\n>", "\n") # Remove quotes at new lines
    text = text.replace(' |', "") # Remove pipes
    text = text.replace('---', "") # Remove horizontal lines
    # Remove 2x tab/space
    text = re.sub(r'\s{2,}', ' ', text)

    # Make sure there's no \n\n as well.
    while "\n\n" in text:
        text = text.replace("\n\n", "\n")
    return text

def to_richtext(text: str) -> str:
    text = text.strip()
    block_pattern = re.compile(r"```(.*?)```", re.DOTALL)
    text = block_pattern.sub(r'<pre style="background-color: #f4f4f4; border: 1px solid #ddd; border-left: 3px solid #f36d33; color: #666; page-break-inside: avoid; font-family: monospace; font-size: 15px; line-height: 1.6; margin-bottom: 1.6em; max-width: 100%; overflow: auto; padding: 1em 1.5em; display: block; word-wrap: break-word;"><code>\1</code></pre>', text)

    # Convert inline code
    inline_pattern = re.compile(r"`(.*?)`")
    text = inline_pattern.sub(r'<pre style="background-color: #f4f4f4; border: 1px solid #ddd; border-left: 3px solid #f36d33; color: #666; page-break-inside: avoid; font-family: monospace; font-size: 15px; line-height: 1.6; margin-bottom: 1.6em; max-width: 100%; overflow: auto; padding: 1em 1.5em; display: block; word-wrap: break-word;"><code>\1</code></pre>', text)
    # Convert markdown links to HTML links
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    # Convert markdown bold to HTML bold
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
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