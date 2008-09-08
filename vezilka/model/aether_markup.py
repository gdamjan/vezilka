import re, sys, random

this_module = sys.modules[__name__]

def _split_command(thing):
    """ (markup helper function) """
    # ugliness because everything in html

    match = re.search('(\s|\<p\>)', thing)
    if match == None:
        command = thing
        text = u''
    else:
        command = thing[:match.start()]
        text = thing[match.end():]

    command = command.replace('-','_').lower()

    return command, text


def markup(text, meta=None, outermost=True):
    """ Markup language translator.
        Markup language is less ugly than html, a la wiki. 
        Returns html text, modifies meta if given.

        If the result will be used by another call to markup with
        the same meta, set outermost to False.
        (necessary to get postprocessing step right)

        Special characters: [ ] \
        Escaping: \[ \] \\

        [blah some text]  results in a call to a function called markup_blah
    """

    if meta is None: meta = { }

    chunks = re.split(ur'(\[|\]|\\\[|\\\]|\\\\)', text)

    stack = [ u'' ]
    context_stack = [ { } ]

    for chunk in chunks:
        if chunk == '[':
            stack.append(u'')
            context_stack.append({ })
        elif chunk == ']' and len(stack) >= 2:
            thing = stack.pop(-1)
            thing_context = context_stack.pop(-1)

            command, text = _split_command(thing)
            
            if len(stack) >= 2:
                context = u'context_' + _split_command(stack[-1])[0]
                context = getattr(this_module, context, [ ])
            else:
                context = [ ]

            if command in context:
                context_stack[-1][str(command)] = text 
                text = u''
            elif command + u'*' in context:
                context_stack[-1][str(command)] = \
                    context_stack[-1].get(str(command),[ ]) + [ text ] 
                text = u''
            else:
                try:
                    text = getattr(this_module, 'markup_'+command)(text, meta, **thing_context)
                except:
                    import StringIO, traceback
                    string_file = StringIO.StringIO()
                    traceback.print_exc(file=string_file)
                    text = u'<b><pre>'+quote_html(string_file.getvalue())+u'</pre></b>'
                
            stack[-1] = stack[-1] + text
        else:
            if chunk in (u'\\]',u'\\[',u'\\\\'):
                chunk = chunk[1]
                
            stack[-1] = stack[-1] + quote_html(chunk, True)

    # should only be one item on stack, but don't freak if there's more
    result = u''.join(stack)

    if outermost:
        for mark, callback in meta.get('_callbacks',[]):
            value = callback()
            result = result.replace(mark, value)

    return result

_callback_counter = 0xe000 # Unicode private use area
def make_callback_mark(meta, callback):
    """ Utility for markup_ functions:
        Return a special unicode character indicating that
        the result of callback() should be inserted here.
        
        The callback will be called *after* all markup has occured. 
        This allows inserting variables that have not been set yet,
        and such. """

    global _callback_counter
    mark = unichr(_callback_counter)
    _callback_counter += 1

    meta['_callbacks'] = meta.get('_callbacks',[]) + [(mark, callback)]
    return mark

def markup__insert(text, meta):
    return quote_html(meta.get(text.strip(), u''))


def markup__insert_html(text, meta):
    return meta.get(text.strip(), u'')


def markup__insert_later(text, meta):
    def callback():
        return quote_html(meta.get(text.strip(), u''))

    return make_callback_mark(meta, callback)


def markup__insert_html_later(text, meta):
    def callback():
        return meta.get(text.strip(), u'')

    return make_callback_mark(meta, callback)


def markup_html(text, meta):
    """ Insert some HTML tags.
    
        Example:
          [html <b>hello</b> ]"""

    return unquote_html(text)


def markup_style(text, meta):
    """ Add to the HTML style sheet.

        Example:
            [style
              body { background: #88f }
            ] """

    meta['_head_extra'] = meta.get('_head_extra',u'') + u'<style>' + \
                          unquote_html(text) + u'</style>'
    return u''


def correct_case(s):
    return s

def _resolve_url(text, meta, url, page, file, must_be_file=False):
    """ Helper for markup_link, markup_image

        url, page, file are html
        
        returns url as text, link-text as html"""
        
    text = text.strip()

    if page != None:
        page = page.strip()
        correct_page = correct_case( unquote_html(page) )

    if file != None: 
        file = file.strip()
    
    if url != None: 
        url = url.strip()
        url = unquote_html(url)
    else:
        if page != None and file != None:
            url = attachment_to_url(correct_page, unquote_html(file))
            if not text: text = file

        elif file != None:
            url = attachment_to_url(meta['name'], unquote_html(file))
            if not text: text = file

        elif page != None and not must_be_file:
            url = name_to_url(correct_page)
            if not text: text = page

        elif not must_be_file:
            url = unquote_html(text)
            if re.match(u'[A-Za-z]+:', url) is None:
                url = name_to_url( correct_case(url) )

        else:
            return None
    
    if not text: text = quote_html(url)

    return text, url


context_link = ['url','page','file']
def markup_link(text, meta, url=None, page=None, file=None):
    """ Insert a link.
    
        Examples:
           [link somepage]    
           (or [link [page somepage]] )
               - link to page called somepage

           [link This is the page. [page somepage]]    
               - link with text different to page name

           [link [file myfile.pdf]]
               - link to file attached to this page

           [link [page otherpage] [file otherfile.pdf]]
               - link to file attached to another page

           [link [url http://some.url.org]]
           (or [link http://some.url.org] )
               - link to a url
               
    """

    text, url = _resolve_url(text, meta, url, page, file)

    return u'<a href="' + quote_html(url) + u'">' + text + '</a>'


context_image = ['url','page','file','title']
def markup_image(text, meta, url=None, page=None, file=None, title=None):
    """ Insert an image.

        Parameters as per [link]. """
    
    text, url = _resolve_url(text, meta, url, page, file, True)

    if title == None:
        title = u''
    else:
        title = u' title="' + quote_html(title) + '"'

    return u'<img src="' + quote_html(url) + '"' + title + u'>'


def markup_heading(text, meta):
    """ Heading.

        Example:
           [heading Introduction] """

    meta['_headings'] = meta.get('_headings',[]) + [ text ]
           
    return u'<h2><a name="' + str(len(meta['_headings'])) + u'">' + \
           text + u'</a></h2>'


def markup_subheading(text, meta):
    """ Sub-heading.

        Example:
           [subheading Implementation details] """

    return u'<h3>'+text+u'</h3>'


def markup_toc(text, meta):
    """ Table of contents.

        List all [heading]s. """

    def callback():
        result = [ ]
        headings = meta.get('_headings',[ ])
        for i in xrange(len(headings)):
            result.append(
                u'<a href="' + quote_html(name_to_url(meta['name'])) + u'#' +
                str(i+1) + u'"># ' + headings[i] + '</a>'
            )

        return u'<br>'.join(result)

    return make_callback_mark(meta, callback)

def markup_line(text, meta):
    """ Display text on separate line.

        Example:
           One must consider:

           [line 1. What?]
           [line 2. Where?]
           [line 3. Why?] """

    return u'<br>'+text


def markup_rule(text, meta):
    """ Draw a horizontal line.

        Example:
           [rule] """

    return u'<hr>'+text


def markup_bullet(text, meta):
    """ Bullet point.

        Example:
           [bullet New nation]
           [bullet Civil war]
           [bullet Dedicate field]
           [bullet Dedicated to unfinished work]
           [bullet New birth of freedom]
           [bullet Government not perish] """

    return u'<ul><li>'+text+u'</li></ul>'


def markup_small(text, meta):
    """ Smaller font size.

        Example:
           [right [small It's an interesting fact that in... ]] """
           
    return u'<font size=-2>'+text+u'</font>'


def markup_bold(text, meta):
    """ Bold text.

        Example:
           Well, that was [bold startling]! """
           
    return u'<b>'+text+u'</b>'


def markup_mono(text, meta):
    """ Monospaced text. All formatting will be preserved.
    
        Example:
           Here is some code to mark up [mono italic] text:
           
           [mono
              def markup_italic(text, meta):
                  return u'<i>'+text+u'</i>'
           ] """

    # Remove <p>s, <br>s inserted by quote_html
    text = text.replace(u'<p>', u'')
    text = text.replace(u'<br>', u'')
    
    # Workaround for mozilla bug
    text = re.sub(ur'(\n\r?)', ur'\1 ', text)

    return u'<span class="mono">'+text+u'</span>'


def markup_sans(text, meta):
    """ Sans-serif text.

        Example:
           [sans [link Home [page home]]] """

    return u'<font face="Sans-Serif">'+text+u'</font>'


def markup_indent(text, meta):
    """ Indent text.

        Example:
           Douglas Adams once wrote:
           
           [indent Anyone who is capable of getting themselves made President 
           should on no account be allowed to do the job.] """
            
    return u'<span class=indent>'+text+u'</span>'


def markup_italic(text, meta):
    """ Italic text.

        Example:
           A [italic non-linear causal predictor] was used. """
           
    return u'<i>'+text+u'</i>'


context_span = [ 'style' ]
def markup_span(text, meta, style=u''):
    """ Generic markup tag:
        A span of text with different CSS style.

        Example:
           [span I'm floating! [style float: right]] 
           [span I'm huge! [style font-size: 300%]] 
           [span I'm both! [style float: right; font-size: 300%]] """

    return u'<span style="' + style + u'">' + text.strip() + u'</span>'


def markup_title(text, meta):
    """ Specify the title of the page.

        Example:
           [title Home] """
    text = unquote_html(text)
    meta['title'] = text
    return u'<h1>%s</h1>' % text


def markup_summary(text, meta):
    """ Mark a range of text as a summary or abstract. When used in a blog
        entry, only the summary will appear on the main blog page. This tag
        does not affect the appearance of the actual page.

        Example:
           [summary Python is a remarkable language.]

           It has a number of useful features. """

    meta['summary'] = text
    return text


def _border_helper(border, text, meta, prepend=None, append=None):
    if prepend != None:
        meta[border] = text + meta.get(border, u'')
    elif append != None:
        meta[border] = meta.get(border, u'') + text
    else:
        meta[border] = text


context_top = [ 'prepend', 'append' ]
def markup_top(text, meta, **options):
    """ Specify text for top of page. Options as per [left]. """

    _border_helper('_top', text, meta, **options)
    return u''


context_left = [ 'prepend', 'append' ]
def markup_left(text, meta, **options):
    """ Specify text for left of page. 
    
        By default, replaces any previously specified text,
        use the flags [prepend] or [append] to override this.

        I suggest using [left] as a menu bar for navigating your site.

        Examples:
           [left Menu bar...]

           [left [append] See also in this site...]

           [left [prepend] Table of contents...] """

    _border_helper('_left', text, meta, **options)
    return u''


context_right = [ 'prepend', 'append' ]
def markup_right(text, meta, **options):
    """ Specify text for right of page. Options as per [left]. 
    
        I suggest using [right] for footnotes and links to
        related external links of your site. """

    _border_helper('_right', text, meta, **options)
    return u''


context_bottom = [ 'prepend', 'append' ]
def markup_bottom(text, meta, **options):
    """ Specify text for the bottom of page. Options as per [left]. 
    
        I suggest using [bottom] for copyright notices and disclaimers. """

    _border_helper('_bottom', text, meta, **options)
    return u''



context_include = ['default']
def markup_include(text, meta, default=u''):
    # Insert one page into another.
    # (i'm still thinking about how to do this well, eg inserting only part of
    #  a page...)

    name = text.strip()

    old_name = meta.get('name', None)
    older_name = meta.get('outer_name', None)

    if old_name == None:
        if 'outer_name' in meta: del meta['outer_name']
    else:
        meta['outer_name'] = old_name

    meta['name'] = name

    try:
        result = markup(load(name), meta, False)
    except Error:
        result = default

    if old_name == None:
        if 'name' in meta: del meta['name']
    else:
        meta['name'] = old_name

    if older_name == None:
        if 'outer_name' in meta: del meta['outer_name']
    else:
        meta['outer_name'] = older_name

    return result

def markup_keyword(text, meta):
    """ Associate a keyword with a page.

        It is possible to create a blog that displays only blog entries
        with certain keywords (see [blog]).

        Example:
            [title My exciting holiday]
            [keyword hamster] [keyword bandages] """

    meta['keywords'] = meta.get('keywords',[ ]) + [ unquote_html(text).strip() ]
    return u''

def markup_sup(text, meta):
    """Superscript"""
    return u'<sup>%s</sup>' % text

def markup_sub(text, meta):
    """Subscript"""
    return u'<sub>%s</sub>' % text

def markup_strike(text, meta):
    """Strikethrough"""
    return u'<strike>%s</strike>' % text

def markup_code(text, meta):
    """Preformated code"""
    return u'<pre class="code">%s</pre>' % unquote_html(text)

def markup_underline(text, meta):
    """Underline"""
    return u'<u>%s</u>' % text

context_abbr = ('title')
def markup_abbr(text, meta, title=""):
    """Abbreviation

    Example:
        [abbr ODF[title OpenDocumentFormat]]"""

    return u'<abbr title="%s">%s</abbr>' % (title,text)

context_random = ('num')
def markup_random(text, meta, num=1):
    """Random text

    Example:
        [random text1||text2||text3||text4 [num 2]]"""

    num = int(num)
    population = text.split('||')
    return u"".join(random.sample(population, num))

# Quoting ---------------------------------------------------------------------

html_quote_sequence = [
    (u'&', u'&amp;'),
    (u'<', u'&lt;'),
    (u'>', u'&gt;'),
    (u'"', u'&quot;')
]

html_unquote_sequence = html_quote_sequence[:]
html_unquote_sequence.reverse()


def quote_html(text, markup_newlines=False):
    """ Convert special HTML characters to &xyz; form. 
        If <markup_newlines>, convert newlines into <p> tags, etc. """

    for a, b in html_quote_sequence:
        text = text.replace(a, b)

    if markup_newlines:
        text = re.sub(ur'\n[ \r\t]*(\n[ \r\t]*)+', 
            lambda match: 
                match.group(0) +
                u'<p>' + u'<br>'*(match.group(0).count(u'\n')-2),
            text)

    return text


def unquote_html(text):
    """ Precisely undo quote_html. 
    
        Also strips HTML tags. """

    text = re.sub(u'<[^>]*>', u'', text)

    for a, b in html_unquote_sequence:
        text = text.replace(b, a)

    return text


def quote_markup(text):
    """ Escape special characters used by Aether markup language. """
    text = re.sub(ur'([\\\[\]])', ur'\\\1', text)
    return text


def unquote_markup(text):
    """ Precisely undo changes made by quote_markup. """
    text = re.sub(ur'\\([\\\[\]])', ur'\1', text)
    return text


# Urls -----------------------------------------------------------------------

def name_to_url(name):
    """ URL of page named <name> """
    return name # FIXME
    return host_url + page_base + u'/' + name


def attachment_to_url(name, filename):
    """ URL of file <filename> attached to page <name> """
    return host_url + file_base + u'/' + name + u'/' + filename

