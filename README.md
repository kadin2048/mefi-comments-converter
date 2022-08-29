# mefi-comments-converter

A little Python utility to convert the massive text file produced by
Metafilter's 'Export Your Comments' feature into a variety of
structured formats.

Currently converts to HTML, JSON, or Unix-style MBOX (mailbox) format.

Currently it allows you to convert your comments export file into
HTML, JSON, or MBOX formats:

* HTML mode is meant for casually reading through comments, and
  produces a single large file that's (probably) HTML5-compliant. Each
  comment entry is wrapped in a <div class="comment">, and the post
  text itself in <div class="comment-text">, so you can style it with
  CSS if you want. Out-of-the-box, comments are pretty readable, with
  the only exception being tables constructed using <pre> tags, which
  are ugly.
* JSON mode is for people who want to engage in further nerdery with
  their contributions, and outputs a single array containing all
  comments, with each comment represented as an object with date, url,
  and html keys. Double quotes are escaped with leading
  forward-slashes, and Unicode entities are represented in ASCII, as
  per the JSON spec. I'm not really sure what the use case is for this
  one, but it was easy to implement, so there you go. Maybe feed it
  into an AI and shitpost forever from beyond the grave?
* Unix Mailbox (mbox) mode is sort of my personal favorite, and
  converts each comment into a valid MIME multipart/mixed message
  containing the HTML content, and the original URL in a
  pseudo-signature block. Date/time posted is stored in the message
  Date header, which corresponds to the "Date Sent" in most email
  programs. The Message-ID is constructed from the Mefi subdomain
  (www, ask, metatalk, etc.), the post ID, and the comment ID in a way
  that's predictable, to allow for duplicate filtering. The References
  header is populated by a value unique to the post only, allowing
  multiple comments in the same discussion to be grouped, if your mail
  program supports it. It should also, in theory, allow comments from
  multiple people to be combined together and sorted correctly. The
  resulting mbox file seems to work fine when dumped directly into my
  Dovecot mailserver's mail boxes directory and viewed with Apple
  Mail.

Conversion of my comments (all 10,964 of 'em) takes just under one
second to either HTML or JSON. MBOX conversion is significantly
slower, taking about 20s to complete. It has been written for and
tested on Python 3.9.1, and uses only standard libraries.

It's meant to be run from the command line, and should work on Mac,
Linux, or Windows (as long as you have Python 3 installed). Usage is
fairly simple, just specify the input filename and output filename you
want to create. The processing mode is determined by the file
extension specified on the output. Valid extensions are "json",
"html", or "mbox".

Example: `python3 mefi_parser.py my-mefi-comments.txt my-mefi-comments.json`  
will convert the file "my-mefi-comments.txt" to JSON, and write to
"my-mefi-comments.json".

Comments, suggestions, etc. are welcome; feel free to fork and modify
on Github if that's your thing.
