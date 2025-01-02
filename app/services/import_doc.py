import tempfile
import os
from typing import List
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.utils.translation import gettext as _
from pathlib import Path
import subprocess
import sys
import regex as re
from bs4 import BeautifulSoup, NavigableString
from cssutils import parseStyle

class Block:
    def __init__(self, content: str):
        self.content = content

    def to_html(self):
        pass

    def to_doc(self):
        pass

class Paragraph(Block):
    def to_html(self):
        tag = BeautifulSoup(self.content, 'lxml').body.contents[0]
        return tag

    def to_doc(self):
        tag = BeautifulSoup(self.content, 'lxml').body.contents[0]
        tag['style'] = 'text-indent:24pt; line-height:20pt; font-size:12pt; margin:12pt 0 0 0'
        return tag

class Remark(Block):
    def to_html(self):
        tag = BeautifulSoup(self.content, 'lxml').p
        tag.class_ = 'remark'
        return tag

    def to_doc(self):
        tag = BeautifulSoup(self.content, 'lxml').p
        del tag['class']
        tag['style'] = 'text-indent:24pt; line-height:20pt; font-size:11pt; margin:12pt 0 0 0'
        return tag

class Subtitle(Block):
    def to_html(self):
        tag = BeautifulSoup('<h2></h2>', 'lxml').h2
        tag.string = self.content
        return tag

    def to_doc(self):
        tag = BeautifulSoup('<p style="line-height:20pt; font-size:12pt; margin:12pt 0 0 0; text-decoration:underline"></p>', 'lxml').p
        tag.string = self.content
        return tag

class Document:
    def __init__(self, title: str, author: str, contents: List[Block]):
        self.title = title
        self.author = author
        self.contents = contents

    def to_html(self):
        root = BeautifulSoup('<div></div>', 'lxml').div

        for block in self.contents:
            root.append(block.to_html())

        return root.decode_contents()

    def to_doc(self, url: str, year: str):
        root = BeautifulSoup('<div></div>', 'lxml')

        # title
        tag = root.new_tag('p', style='line-height:20pt; font-size:14pt; margin:12pt 0 0 0; text-align:center; font-weight:bold;')
        tag.string = self.title
        root.append(tag)

        #empty paragraph
        tag = root.new_tag('p', style='line-height:20pt; font-size:12pt; margin:12pt 0 0 0')
        root.append(tag)

        #author
        tag = root.new_tag('p', style='line-height:20pt; font-size:12pt; margin:0; text-align:right;')
        tag.string = self.author
        root.append(tag)

        for i, block in enumerate(self.contents):
            if i > 0 and isinstance(block, Subtitle):
                tag = root.new_tag('p', style='line-height:20pt; font-size:12pt; margin:12pt 0 0 0')
                br = root.new_tag('br')
                tag.append(br)
                root.append(tag)
            root.append(block.to_doc())

        # ended
        tag = root.new_tag('p', style='line-height:20pt; font-size:12pt; margin:12pt 0 0 0; text-align:center')
        tag.string = _('完')
        root.append(tag)

        # copyright
        tag = root.new_tag('p', style='line-height:20pt; font-size:11pt; margin:0')
        tag.string = _('© %(year)s LOGOS福音網。版權所有。') % { 'year': year }
        root.append(tag)

        # distribution
        tag = root.new_tag('p', style='line-height:20pt; font-size:11pt; margin:0')
        tag.string = _('歡迎轉載，但須註明出處及鏈接 (URL) 並保持信息完整。')
        root.append(tag)

        # refer
        tag = root.new_tag('p', style='line-height:20pt; font-size:11pt; margin:0')
        tag.string = _('鏈接：')
        a = root.new_tag('a', href=url, target='_blank')
        a.string = url
        tag.append(a)
        root.append(tag)

        return str(root)

def import_doc(file: UploadedFile) -> str | None:
    ext = Path(file.name).suffix
    with tempfile.NamedTemporaryFile(suffix=ext, dir=settings.FILE_UPLOAD_TEMP_DIR) as input_file:
        for chunk in file.chunks():
            input_file.write(chunk)
        fd, output_file_name = tempfile.mkstemp(suffix='.html', dir=settings.FILE_UPLOAD_TEMP_DIR, text=True)
        os.close(fd)
        try:
            res = subprocess.run(['abiword', '-t', 'html', '-o', output_file_name, input_file.name], stdout=sys.stdout, stderr=sys.stderr)
            if res.returncode != 0:
                return None
            with open(output_file_name) as output_file:
                html = output_file.read()
                return html
        finally:
            os.unlink(output_file_name)

_html_regexp_filters = [
    (re.compile(r'>\s+<'), r'><'),
    (re.compile(r'^.*(<html.*</html>).*$', flags=re.MULTILINE|re.DOTALL), r'\1'),
    (re.compile(r'&nbsp;'), r' '),
    (re.compile(r'[﹐]'), r'，'),
    (re.compile(r'[︔﹔]'), r'；'),
    (re.compile(r'[︖﹖]'), r'？'),
    (re.compile(r'[ꜝ︕﹗]'), r'！'),
    (re.compile(r'[˸܃܄꞉︓﹕：]'), r'：'),
    (re.compile(r'[﹒．｡]'), r'。'),
    (re.compile(r'[﹒．｡]'), r'。'),
    (re.compile(r'\s*[⁽₍❨❪﴾﹙（]'), r' ('),
    (re.compile(r'[⁾₎❩❫﴿﹚）]\s*'), r') '),
    (re.compile(r'[­ᐨ᠆‐-―⎯─━⸺⸻﹘﹣－]'), r'⎯'),
]

_content_regexp_filters = [
    (re.compile(r'(\p{Han}[^a-zA-Z0-9\s\p{Han}]*)\s*,\s*'), r'\1，'),
    (re.compile(r'(\p{Han}[^a-zA-Z0-9\s\p{Han}]*)\s*;\s*'), r'\1；'),
    (re.compile(r'(\p{Han}[^a-zA-Z0-9\s\p{Han}]*)\s*\?\s*'), r'\1？'),
    (re.compile(r'(\p{Han}[^a-zA-Z0-9\s\p{Han}]*)\s*!\s*'), r'\1！'),
    (re.compile(r'(\p{Han}[^a-zA-Z0-9\s\p{Han}]*)\s*:\s*'), r'\1：'),
]

def _apply_regex_filters(filters, html: str) -> str:
    for (regex, replaced) in filters:
        html = regex.sub(replaced, html)
    return html

def process_doc(html: str) -> Document:
    html = _apply_regex_filters(_html_regexp_filters, html)

    def is_author(el, index):
        if el.name != 'p':
            return False
        if index >= 3:
            return False
        text = el.get_text()
        return '主講' in text or '主讲' in text or '筆者' in text or '笔者' in text

    def is_title(el, index):
        if el.name != 'p':
            return False
        if index >= 4:
            return False
        bold, total = 0, 0
        for child in el.contents:
            text_len = len(child.get_text().strip())
            total += text_len
            if not isinstance(child, NavigableString) and child.has_attr('style'):
                style = parseStyle(child['style'])
                font_weight = style.getProperty('font-weight')
                if font_weight and font_weight.value == 'bold':
                    bold += text_len

        return bold / text_len > 0.8

    def is_subtitle(el, index):
        if el.name == 'h2':
            return True
        if el.name != 'p':
            return False
        underline, total = 0, 0
        for child in el.contents:
            text_len = len(child.get_text().strip())
            total += text_len
            if not isinstance(child, NavigableString) and child.has_attr('style'):
                style = parseStyle(child['style'])
                text_decoration = style.getProperty('text-decoration')
                if text_decoration and text_decoration.value == 'underline':
                    underline += text_len

        return underline / text_len > 0.8

    def is_remark(el, index):
        if el.name != 'p':
            return False
        text = el.get_text().strip()
        return re.match(r'^\[.*\]$', text) is not None

    def is_end(text):
        return '完' in text and len(text) < 6

    def is_copyright(text):
        return ('版權所有' in text or '版权所有' in text) and len(text) < 30

    def is_distribution(text):
        return ('歡迎轉載' in text or '欢迎转载' in text) and len(text) < 35

    def is_reference(text):
        return ('鏈接' in text or '链接' in text) and ('http://' in text or 'https://' in text)

    def is_footer(el, index):
        if el.name != 'p':
            return False
        text = el.get_text().strip()
        return is_end(text) or is_copyright(text) or is_distribution(text) or is_reference(text)

    def to_string(el):
        if el.name == 'p' and el.has_attr('style'):
            del el['style']
        return str(el)

    root = BeautifulSoup(html, 'lxml')
    body = root.body
    if not body:
        return Document(title='', author='', contents=[])
    if len(body.contents) == 1:
        body = body.contents[0]

    # clean doc
    for x in body.find_all():
        if len(x.get_text(strip=True)) == 0:
            x.decompose()
            continue

        if x.has_attr('class'):
            del x['class']

        if x.has_attr('style'):
            style = parseStyle(x['style'])
            style.removeProperty('font-family')
            style.removeProperty('font-size')
            style.removeProperty('padding')
            style.removeProperty('padding-top')
            style.removeProperty('padding-bottom')
            style.removeProperty('padding-left')
            style.removeProperty('padding-right')
            style.removeProperty('margin')
            style.removeProperty('margin-top')
            style.removeProperty('margin-bottom')
            style.removeProperty('margin-left')
            style.removeProperty('margin-right')
            style.removeProperty('color')
            style.removeProperty('background')
            style.removeProperty('background-color')
            style.removeProperty('text-indent')
            style.removeProperty('line-height')
            css = style.cssText
            if css:
                x['style'] = css.replace('\n', ' ')
            else:
                del x['style']

    for x in body.find_all('span'):
        if not x.has_attr('style'):
            x.unwrap()

    for x in body.find_all('span'):
        prev = x.previous_sibling
        if prev and prev.name == 'span' and x['style'] == prev['style']:
            prev.extend(x.contents)
            x.decompose()

    for x in body.find_all('a'):
        x['target'] = '_blank'

    author = ''
    title = ''
    contents = []

    for index, child in enumerate(body.contents):
        if isinstance(child, NavigableString):
            continue
        if is_author(child, index):
            author = child.get_text().strip()
        elif is_title(child, index):
            title = child.get_text().strip()
        elif is_subtitle(child, index):
            contents.append(Subtitle(_apply_regex_filters(_content_regexp_filters, child.get_text().strip())))
        elif is_remark(child, index):
            contents.append(Remark(_apply_regex_filters(_content_regexp_filters, to_string(child))))
        elif not is_footer(child, index):
            contents.append(Paragraph(_apply_regex_filters(_content_regexp_filters, to_string(child))))

    return Document(title=title, author=author, contents=contents)
