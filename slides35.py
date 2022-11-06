#!/usr/bin/env python

""" Roadmap
Change number in one SVG file in Python
Change image in one SVG file
Make a list of JPG files sorted by date
Make SVG files from JPG files with adequate numbering and file naming
"""
import pdb

SLIDES35_DEFAULT_SVG_TEMPLATE = 'templates/36x24mmNumbered.svg'

from pathlib import Path
from xml.dom import minidom
import argparse

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
            if not Path(template).exists():
                raise FileNotFoundError("Could not find template: {}".format(template))
            self._template = str(Path(template))
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
            if not Path(picture).exists():
                raise FileNotFoundError("Could not find picture: {}".format(picture))

            self._picture = str(Path(picture))
            return self

    def svg(self):
        if not self._template or not Path(self._template).exists():
            raise FileNotFoundError("Set the SVG template first")
        if not self._id:
            raise ValueError("Set the .id() value first")
        if not self._picture:
            raise ValueError("Set the .picture() value first")
        rootElem = minidom.parse(self._template)
        rootElem.getElementsByTagName('image')[0].attributes['xlink:href'].value = self._picture
        rootElem.getElementsByTagName('text')[0].firstChild.firstChild.nodeValue = str(self._id).center(3)
        return rootElem.toxml()

    def png(self):
        pass

    def __eq__(self, other):
        return self._template == other._template \
            and self._id == other._id \
            and self._comment == other._comment \
            and self._picture == other._picture

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
      '--picture',
      help='path to picture to embed'
    )
    parser.add_argument(
      '--id',
      help='id of the new slide'
    )
    parser.add_argument(
      '--template',
      default=SLIDES35_DEFAULT_SVG_TEMPLATE,
      help='SVG template to use (default:{})'.format(SLIDES35_DEFAULT_SVG_TEMPLATE)
    )

    args = parser.parse_args()
    
    if not args.picture:
        print("no --picture provided. Exitting")
        exit(1)
 
    if not args.id:
        print("no --id provided. Exitting")
        exit(1)

    s = Slide(args.template)
    s.picture(args.picture).id(args.id)
    print(s.svg())

if __name__ == "__main__":
    main()
