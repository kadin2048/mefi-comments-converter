#!/usr/bin/env python3
#
# Script to convert Metafilter comments export to other formats
#
# JSON: mefi_parser.py inputfile.txt outputfile.json
# HTML: mefi_parser.py inputfile.txt outputfile.html
# MBOX: mefi_parser.py inputfile.txt outputfile.mbox

import sys
import json
import time
from datetime import datetime
import mailbox
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

debug = True  # Set to False to suppress debug output

def main(args):
    try:
        args[1]
    except IndexError:
        print("Input filename not specified. Exiting.")
        return 1
    try:
        args[2]
    except IndexError:
        print("Output filename not specified. Exiting.")
        return 1
    
    with open(args[1]) as input:
        debug_message("Reading from " + args[1])
        commentdicts = parse_comments(input)
    
    outtype = args[2].split('.')[-1]  # Get file extension
    
    if outtype == 'mbox':
        mbox = mailbox.mbox(args[2], create=True)  # This will append if file exists!
        messages = convert_to_messages(commentdicts)
        for msg in messages:
            mbox.add(msg)
        return 0
    
    if outtype == 'json':
        outputkeys = ['date', 'url', 'html']  # Fields to include
        for commentdict in commentdicts:
            for key in list(commentdict.keys()):
                if key not in outputkeys:
                    del commentdict[key]
        with open(args[2], 'w') as output:
            json.dump(commentdicts, output, indent=2)
        return 0
    
    if outtype == 'html':
        with open(args[2], 'w') as output:
            output.write(convert_to_html(commentdicts))
        return 0
    
    else:
        print("Unrecognized output file type.")
        return 1


def parse_comments(commentfile):  # Parse export file to list of dicts
    allcomments = []
    comment = []
    for line in commentfile:
        if line == "-----\n":
            allcomments.append(comment)
            comment = []
        else:
            comment.append(line)
    
    debug_message("Parsing found " + str(len(allcomments)) + " comments total")
    
    commentdicts = []
    for comment in allcomments:
        commentdict = {}
        commentdict['date'] = comment[0].strip()
        commentdict['datetimeobj'] = datetime.strptime(commentdict['date'].split('.')[0], '%Y-%m-%d %H:%M:%S')
        commentdict['url'] = comment[1].strip()
        commentdict['id'] = commentdict['url'].split('/')[2].split('.')[0] + '.' + commentdict['url'].split('/')[-2] + '.' + commentdict['url'].split('#')[-1]
        commentdict['postid'] = commentdict['url'].split('/')[2].split('.')[0] + '.' + commentdict['url'].split('/')[-2]
        commentdict['html'] = ' '.join(comment[2:]).replace('\n','')
        commentdicts.append(commentdict)
    
    return commentdicts  # Returns list of comment dictionary objects


def convert_to_messages(commentdicts):
    messages = []
    for commentdict in commentdicts:
        msg = MIMEMultipart('mixed')
        msg['From'] = "Metafilter Comment Export <archive@metafilter.invalid>"
        msg['Subject'] = '[' + commentdict['url'].split('/')[2].split('.')[0] + '] ' + commentdict['url'].split('/')[-1].replace('-',' ').replace('#',': ')
        msg['Date'] = commentdict['datetimeobj'].strftime('%a, %d %b %Y %H:%M:%S' + ' -0700')  # Pacific Time
        msg['Message-ID'] = '<' + commentdict['id'] + '@' + 'metafilter.invalid' + '>'
        msg['References'] = '<' + commentdict['postid'] + '@' + 'metafilter.invalid' + '>'
        msg['X-Originating-URL'] = commentdict['url']
        msg['X-Converted-On'] = time.strftime('%a, %d %b %Y %H:%M:%S %z')
        msg.attach(MIMEText(commentdict['html'], 'html'))  # Attach the HTML payload
        msg.attach(MIMEText('\n-- \n' + commentdict['url'], 'plain')) # Attach URL as separate MIME part
        messages.append(msg)
    debug_message("Converted " + str(len(messages)) + " comments to messages")
    return messages


def convert_to_html(commentdicts):  # Generate single HTML5 file of all comments
    debug_message("Beginning HTML5 generation")
    htmltitle = "Metafilter Comment Export"  # Set as desired
    lines = []
    lines.append("<!doctype html>")
    lines.append("<html lang=en>")
    lines.append("<head>")
    lines.append("<title>" + htmltitle + "</title>")
    lines.append("</head>")
    lines.append("<body>")
    lines.append("<h1>" + htmltitle + "</h1>")
    lines.append("<p>Converted on " + time.strftime('%Y-%m-%d %T') + "</p>")
    lines.append("<hr>")
    for commentdict in commentdicts:
        lines.append('<div class="comment">\n<h3><a href="' + commentdict['url'] + '">' + commentdict['date'] + '</a></h3>')
        lines.append('<div class="comment-text">' + commentdict['html'] + "</div>\n</div>")
    lines.append("</body>\n</html>")
    debug_message("Generated " + str(len(lines)) + " lines of HTML")
    return ("\n").join(lines)


def debug_message(msg):
    if debug:
        print("DEBUG:", msg)  # Change to log file if desired; be sure to add \n


if __name__ == "__main__":
    start = time.process_time()  # For performance measurements
    exitval = main(sys.argv)
    debug_message("Completed in " + str((time.process_time() - start)) + " seconds")
    sys.exit(exitval)
