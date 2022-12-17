#!/usr/bin/env python

""" Roadmap
Change number in one SVG file in Python
Change image in one SVG file
Make a list of JPG files sorted by date
Make SVG files from JPG files with adequate numbering and file naming
"""

SLIDES35_DEFAULT_SVG_TEMPLATE = "templates/36x24mmNumbered.svg"
SLIDES35_DEFAULT_OUTPUT_DPI = 500
SLIDES35_DEFAULT_OUTPUT_PREFIX = "slide_"
SLIDES35_DEFAULT_OUTPUT_FILENAME_ZFILL_COUNT = 3
SLIDES35_DEFAULT_SVG_TO_PNG_CONVERTER = "convert"
SLIDES35_SUPPORTED_CONVERTERS = ("inkscape", "convert")

from pathlib import Path
from xml.dom import minidom
import argparse
import os
import subprocess
import shutil
import tempfile


class Slide:
    _id = None
    _comment = None
    _picture = None
    _template = None
    _prefix = None
    _verbose = None
    _converter = None

    def __init__(
        self,
        template=None,
        verbose=False,
        converter=SLIDES35_DEFAULT_SVG_TO_PNG_CONVERTER,
    ):
        self.template(template)
        self.verbose(verbose)
        self.converter(converter)

    def template(self, template=None):
        if not template:
            return self._template
        else:
            if not Path(template).exists():
                raise FileNotFoundError("Could not find template: {}".format(template))
            self._template = str(Path(template))
            return self

    def converter(self, converter=None):
        if not converter:
            return self._converter
        else:
            if type(converter) is not str:
                raise TypeError("converter must be a str")
            if converter not in SLIDES35_SUPPORTED_CONVERTERS:
                raise ValueError(
                    "converter must be one {}".format(SLIDES35_SUPPORTED_CONVERTERS)
                )
            self._converter = converter
        return self

    def verbose(self, verbose=None):
        if verbose is None:
            return self._verbose
        else:
            if type(verbose) is not bool:
                raise TypeError("verbose flag must be a boolean")
            self._verbose = verbose
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

            self._picture = str(Path(picture).resolve())
            return self

    def prefix(self, prefix=None):
        if not prefix:
            return self._prefix
        else:
            self._prefix = str(prefix)
            return self

    def svg(self, output_path=None):
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
        if output_path:
            if self._verbose:
                print(
                    "{} -> {} (id: {}) -> {}".format(
                        self._picture, self._template, self._id, output_path
                    )
                )
            with open(output_path, "w") as f:
                f.write(rootElem.toxml())
            return self
        else:
            return rootElem.toxml()

    def png(
        self,
        output_path,
        dpi=SLIDES35_DEFAULT_OUTPUT_DPI,
    ):
        if not shutil.which(self._converter):
            print("Cannot find executable path for converter '{}'".format(self._converter))
            exit(1)

        svg_handle, svg_output_filename = tempfile.mkstemp(".svg")
        self.svg(svg_output_filename)
        dpi = dpi if dpi else SLIDES35_DEFAULT_OUTPUT_DPI
        if self._verbose:
            print("{} -> {}".format(svg_output_filename, output_path))

        if self._converter == "convert":
            command_to_run = [
                "convert",
                "-density",
                str(dpi),
                "-resample",
                str(dpi),
                svg_output_filename,
                output_path,
            ]
        elif self._converter == "inkscape":
            command_to_run = [
                "inkscape",
                svg_output_filename,
                "--export-dpi",
                str(dpi),
                "--export-filename",
                output_path,
            ]

        if self._verbose:
            print(command_to_run)

        subprocess.run(command_to_run)

        os.unlink(svg_output_filename)

        return self

    def __eq__(self, other):
        return (
            self._template == other._template
            and self._id == other._id
            and self._comment == other._comment
            and self._picture == other._picture
        )


def do_slide(
    template,
    picture,
    identifier,
    output_dir=".",
    stdout=False,
    output_filename=None,
    output_as="svg",
    output_prefix=SLIDES35_DEFAULT_OUTPUT_PREFIX,
    dpi=SLIDES35_DEFAULT_OUTPUT_DPI,
    converter=SLIDES35_DEFAULT_SVG_TO_PNG_CONVERTER,
    verbose=False,
):
    if output_as not in ("svg", "png"):
        raise ValueError(
            "output_as parameter must be 'svg' or 'png' but '{}' was provided"
        )
    if not output_filename:
        output_path = "{}{}.{}".format(
            output_prefix,
            (str(identifier).zfill(SLIDES35_DEFAULT_OUTPUT_FILENAME_ZFILL_COUNT)),
            output_as,
        )
    else:
        output_path = output_filename
    output_path = Path(output_dir) / output_path
    s = (
        Slide(template)
        .picture(picture)
        .id(identifier)
        .verbose(verbose)
        .converter(converter)
    )
    if output_as == "svg":
        if not stdout:
            s.svg(output_path)
        else:
            print(s.svg())
    else:
        s.png(output_path=output_path, dpi=dpi)
    return output_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--picture", help="path to picture to embed")
    parser.add_argument(
        "-I", "--pictures-dir", nargs="?", help="Path to directory of pictures to embed"
    )
    parser.add_argument("-n", "--id", help="ID of the new slide")
    parser.add_argument(
        "-t",
        "--template",
        default=SLIDES35_DEFAULT_SVG_TEMPLATE,
        help="SVG template to use (default:{}).".format(SLIDES35_DEFAULT_SVG_TEMPLATE),
    )
    parser.add_argument(
        "-0",
        "--stdout",
        help="Output SVG to STDOUT instead of a file. Only for SVG output (ie. without --output or with --output providing a .svg-ending filename).",
        action="store_true",
    )
    parser.add_argument(
        "-o",
        "--output",
        nargs="?",
        help="Output file name (or file name --picture-dir is used). If omitted, result is printed. This cannot be used with --output-prefix.",
    )
    parser.add_argument(
        "-c",
        "--converter",
        nargs="?",
        default=SLIDES35_DEFAULT_SVG_TO_PNG_CONVERTER,
        help="Executable to use to convert temporary SVG files to PNG (default:{}).".format(
            SLIDES35_DEFAULT_SVG_TO_PNG_CONVERTER
        ),
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enabled verbose output."
    )
    parser.add_argument(
        "-p",
        "--output-prefix",
        nargs="?",
        help="Output file name prefix, which will be suffixed with a 3-digits integer (using --identifier or not if --pictures-dir is used). This option cannot be used with --output.",
    )
    parser.add_argument("-d", "--output-dir", nargs="?", help="Output file directory")
    parser.add_argument(
        "--dpi",
        nargs="?",
        default=SLIDES35_DEFAULT_OUTPUT_DPI,
        help="DPI dots-per-inch density for PNG output (default:{})".format(
            SLIDES35_DEFAULT_OUTPUT_DPI
        ),
    )

    args = parser.parse_args()

    if not args.picture and not args.pictures_dir:
        print("No --picture or --pictures-dir provided. Exitting")
        exit(1)

    if args.picture and args.pictures_dir:
        print("Provide either --picture or --pictures-dir, not both. Exitting")
        exit(1)

    if not args.id and not args.pictures_dir:
        print(
            "No --id provided (while not in a --pictures-dir input files situation). Exitting"
        )
        exit(1)

    if args.output_prefix and args.output:
        print("You cannot use --output-prefix and --output together")
        exit(1)

    if args.stdout and args.output:
        print("You cannot use --output (filename) and --stdout together")
        exit(1)

    if args.output_dir:
        if not Path(args.output_dir).exists():
            os.makedirs(args.output_dir, exist_ok=True)

    output_dir = Path(args.output_dir if args.output_dir else ".")

    if args.pictures_dir:
        if args.stdout:
            print("--pictures-dir cannot be used with --stdout. Exitting")
            exit(1)
        pic_dir = Path(args.pictures_dir)
        if not pic_dir.exists():
            print(
                "--pictures-dir directory {} does not exist. Exitting".format(pic_dir)
            )
            exit(1)
        img_id = 1

        for img in sorted(os.listdir(pic_dir)):
            img_path = (Path(pic_dir) / Path(img)).resolve()
            output_prefix = (
                args.output_prefix
                if args.output_prefix
                else SLIDES35_DEFAULT_OUTPUT_PREFIX
            )
            do_slide(
                template=args.template,
                picture=img_path,
                identifier=img_id,
                output_dir=output_dir,
                output_as="png",
                output_prefix=output_prefix,
                verbose=args.verbose,
                converter=args.converter,
            )
            img_id += 1
        exit(0)

    export_to_png = False
    output_filename = args.output
    if args.output and output_filename.lower().endswith(".png"):
        export_to_png = True

    picture = Path(args.picture).resolve()

    if args.stdout:
        if export_to_png:
            print(
                "The --stdout SVG-outputting option cannot be used with .png output (see the suffix of your --output argument)"
            )
            exit(1)
        else:
            do_slide(
                template=args.template,
                picture=picture,
                stdout=True,
                identifier=args.id,
                verbose=args.verbose,
            )
    else:
        output_file_format = "png" if export_to_png else "svg"
        do_slide(
            template=args.template,
            picture=picture,
            identifier=args.id,
            output_filename=output_filename,
            output_dir=output_dir,
            output_as=output_file_format,
            dpi=args.dpi,
            verbose=args.verbose,
            converter=args.converter,
        )


if __name__ == "__main__":
    main()
