import markdown
import time
import os, sys


def gen_header(output_dir:str) -> str:
    output = """<!DOCTYPE html>
        <html lang="en">

        <head>
            <meta charset="utf-8">
            <style type="text/css">
        """
    cssin = open(output_dir + '/styles.css')
    output += cssin.read()
    output += """</style>
        </head>

        <body>
        """
    return output


def gen_help(md_file: str, output_dir: str, version: str) -> None:
    output = gen_header(output_dir)

    menu = open(output_dir + '/help-menu.html')
    output += menu.read()
    output += "<p>" + version + "</p>"
    output += """
    
    <div class="tip" style="margin-left:25%;padding:1px 16px;height:1000px;">
    """
    mkin = open(md_file)
    output += markdown.markdown(mkin.read())
    output += "<p>-- Helper for TablePackager v" + version + " --</p>"
    output += """
    </div>
    </body>
    </html>
    """

    output = output.replace('packager/images/', '../images/')  # change image path for html file
    outfile = open(output_dir + '/help.html', 'w')
    outfile.write(output)
    outfile.close()


def gen_about(md_file: str, output_dir: str, version: str) -> None:
    output = gen_header(output_dir)

    mkin = open(md_file)
    output += markdown.markdown(mkin.read())

    output = output.replace('$RELEASE$',
                            'version: '+version+ ' build: ' + time.strftime("%y/%m/%d %H:%M", time.localtime(time.time())))
    output += """
    </body>
    </html>
    """

    output = output.replace('packager/images/', '../images/')  # change image path for html file
    outfile = open(output_dir + '/about.html', 'w')
    outfile.write(output)
    outfile.close()
