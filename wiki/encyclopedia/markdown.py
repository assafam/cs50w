import re

def markdown(content):
    markdown = ''
    inside_paragraph = False
    list_level = 0  # only a single level supported

    for line in content.splitlines():
        # Handle bold
        line = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", line)

        # Handle links
        line = re.sub(r"\[(.*?)\]\((.*?)\)", r'<a href="\2">\1</a>', line)

        # Handle ul
        (line, n) = re.subn(r"^[*-] (.*)", r"<li>\1</li>", line)
        if n and not list_level:
            list_level += 1
            line = "<ul>\n" + line
        if list_level and not n:
            list_level -= 1
            markdown += "</ul>\n"

        # Handle headers
        m = re.match(r"#{1,6} ", line)
        if m is not None:
            n = m.end() - 1
            line = re.sub(r"^#{1,6} (.*)$", rf"<h{n}>\1</h{n}>", line)
            if inside_paragraph:
                line = "</p>\n" + line
                inside_paragraph = False
        # Start a new paragraph for non-header lines
        elif line and not inside_paragraph:
            line = "<p>\n" + line
            inside_paragraph = True

        # Handle paragraph breaks
        if not line:
            if inside_paragraph:
                line += "</p>\n"
                inside_paragraph = False

        # Add line to markdown
        markdown += line + "\n"

    if inside_paragraph:
        markdown += "</p>"
    return markdown
