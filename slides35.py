#!/usr/bin/env python

""" Roadmap
Change number in one SVG file in Python
Change image in one SVG file
Make a list of JPG files sorted by date
Make SVG files from JPG files with adequate numbering and file naming
"""
import pdb

SLIDES35_DEFAULT_SVG_TEMPLATE = "templates/36x24mmNumbered.svg"

from pathlib import Path
from xml.dom import minidom
import argparse
import os
import subprocess
import tempfile


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
        rootElem.getElementsByTagName("image")[0].attributes[
            "xlink:href"
        ].value = self._picture
        rootElem.getElementsByTagName("text")[0].firstChild.firstChild.nodeValue = str(
            self._id
        ).center(3)
        return rootElem.toxml()

    def png(self):
        pass

    def __eq__(self, other):
        return (
            self._template == other._template
            and self._id == other._id
            and self._comment == other._comment
            and self._picture == other._picture
        )


SLIDES35_CLI_DEFAULT_CONVERT_PNG_DENSITY_DPI = 500


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--picture", help="path to picture to embed")
    parser.add_argument(
        "--pictures-dir", nargs="?", help="Path to directory of pictures to embed"
    )
    parser.add_argument("--id", help="ID of the new slide")
    parser.add_argument(
        "--template",
        default=SLIDES35_DEFAULT_SVG_TEMPLATE,
        help="SVG template to use (default:{})".format(SLIDES35_DEFAULT_SVG_TEMPLATE),
    )
    parser.add_argument(
        "--stdout",
        help="Output SVG to STDOUT instead of a file. Only for SVG output (ie. without --output or with --output providing a .svg-ending filename).",
        action="store_true",
    )
    parser.add_argument(
        "--output",
        nargs="?",
        help="Output file name (or file name --picture-dir is used). If omitted, result is printed.",
    )
    parser.add_argument("--output-dir", nargs="?", help="Output file directory")
    parser.add_argument(
        "--dpi",
        nargs="?",
        default=SLIDES35_CLI_DEFAULT_CONVERT_PNG_DENSITY_DPI,
        help="DPI dots-per-inch density for PNG output (default:{})".format(
            SLIDES35_CLI_DEFAULT_CONVERT_PNG_DENSITY_DPI
        ),
    )

    args = parser.parse_args()

    if not args.picture and not args.pictures_dir:
        print("No --picture or --pictures-dir provided. Exitting")
        exit(1)

    if args.picture and args.pictures_dir:
        print("Provide either --picture or --pictures-dir, not both. Exitting")
        exit(1)

    if args.pictures_dir:
        print("Not implemented yet. Exitting")
        exit(1)

    if not args.id:
        print("No --id provided. Exitting")
        exit(1)

    export_to_png = False
    output_filename = args.output
    if args.output and output_filename.lower().endswith(".png"):
        export_to_png = True

    s = Slide(args.template).picture(args.picture).id(args.id)
    if args.stdout:
        if export_to_png:
            print(
                "The --stdout SVG-outputting option cannot be used with .png output (see the suffix of your --output argument)"
            )
            exit(1)
        else:
            print(s.svg())
    else:
        if args.output_dir:
            if not Path(args.output_dir).exists():
                os.makedirs(args.output_dir, exist_ok=True)
            output_filename = Path(args.output_dir) / Path(output_filename)
        if export_to_png:
            svg_handle, svg_output_filename = tempfile.mkstemp(".svg")
            with open(svg_handle, "w") as f:
                f.write(s.svg())
        else:
            svg_output_filename = output_filename
            with open(svg_output_filename, "w") as f:
                f.write(s.svg())
        if export_to_png:
            dpi = args.dpi if args.dpi else SLIDES35_CLI_DEFAULT_CONVERT_PNG_DENSITY_DPI
            subprocess.run(
                ["convert", "-density", str(dpi), svg_output_filename, output_filename]
            )
            os.unlink(svg_output_filename)


if __name__ == "__main__":
    main()
