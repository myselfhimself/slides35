#!/usr/bin/env python

""" Roadmap
Change number in one SVG file in Python
Change image in one SVG file
Make a list of JPG files sorted by date
Make SVG files from JPG files with adequate numbering and file naming
"""

from pathlib import Path
from xml.dom import minidom

class Slide:
    _id = None
    _comment = None
    _picture = None
    _template = None

    def __init__(self, template=None):
        self.template(template)

    def template(self, template=None):
        if not template:
            return self._template
        else:
            self._template = template
            return self

    def id(self, page_id=None):
        if not page_id:
            return self._id
        else:
            self._id = page_id
            return self

    def comment(self, comment=None):
        if not comment:
            return self._comment
        else:
            self._comment = comment
            return self

    def picture(self, picture=None):
        if not picture:
            return self._picture
        else:
            self._picture = picture
            return self

    def svg(self):
        if not self._template or not Path(self._template).exists():
            raise FileNotFoundError("set the SVG template first")
        # TODO modify fields
        return minidom.parse(self._template).toxml()

    def png(self):
        pass

    def __eq__(self, other):
        return self._template == other._template \
            and self._id == other._id \
            and self._comment == other._comment \
            and self._picture == other._picture
