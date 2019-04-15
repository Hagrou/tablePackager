import markdown
from packager.tablePackager import version

import os, sys


output = """<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="utf-8">
    <style type="text/css">
"""
cssin = open('styles.css')
output += cssin.read()
output += """</style>
</head>

<body>
"""

menu = open('help-menu.html')
output += menu.read()
output += "<p>1.1.0</p>"
output += """

<div class="tip" style="margin-left:25%;padding:1px 16px;height:1000px;">
"""
mkin = open('help-content.md')
output += markdown.markdown(mkin.read())

output += """
</div>
</body>
</html>
"""

outfile = open('help.html','w')
outfile.write(output)
outfile.close()