import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from xml.dom import minidom

import numpy
from PIL import Image
import pytest
import imagesize

from slides35 import (
    Slide,
    do_slide,
    SLIDES35_DEFAULT_SVG_TEMPLATE,
    SLIDES35_DEFAULT_OUTPUT_DPI,
)


DEFAULT_SLIDE_TEMPLATE = SLIDES35_DEFAULT_SVG_TEMPLATE
DEFAULT_NON_EXISTING_TEMPLATE = "missingTemplate.svg"
DEFAULT_PICTURE = str(Path("./templates/24x36mmImage.png"))
DEFAULT_NON_EXISTING_PICTURE = "missingPicture.png"
DEFAULT_COMMENT = "Tour simple"
EXECUTABLE_UNDER_TEST = "slides35.py"


def _normalize_xml(xml_string):
    return minidom.parseString(xml_string).toxml()


def test_methods_chaining():
    s = (
        Slide()
        .template(DEFAULT_SLIDE_TEMPLATE)
        .id(1)
        .comment(DEFAULT_COMMENT)
        .picture(DEFAULT_PICTURE)
    )
    assert isinstance(s, Slide)


def test_xml_validity():
    s = (
        Slide()
        .template(DEFAULT_SLIDE_TEMPLATE)
        .id(1)
        .comment(DEFAULT_COMMENT)
        .picture(DEFAULT_PICTURE)
    )
    minidom.parseString(s.svg())


def test_template_setters():
    assert Slide(DEFAULT_SLIDE_TEMPLATE) == Slide().template(DEFAULT_SLIDE_TEMPLATE)


def test_template_lookup_on_svg_output():
    with pytest.raises(FileNotFoundError):
        Slide(DEFAULT_NON_EXISTING_TEMPLATE)

    assert isinstance(
        Slide(DEFAULT_SLIDE_TEMPLATE).id(1).picture(DEFAULT_PICTURE).svg(), str
    )


def test_picture_setter_getter():
    assert Slide().picture(DEFAULT_PICTURE).picture() == DEFAULT_PICTURE
    with pytest.raises(FileNotFoundError):
        Slide().picture(DEFAULT_NON_EXISTING_PICTURE)


def test_command_stdout_svg_output():
    command_output = subprocess.check_output(
        [
            "python",
            EXECUTABLE_UNDER_TEST,
            "--id",
            "1",
            "--picture",
            DEFAULT_PICTURE,
            "--stdout",
        ]
    )
    assert _normalize_xml(command_output) == _normalize_xml(
        Slide(DEFAULT_SLIDE_TEMPLATE).id(1).picture(DEFAULT_PICTURE).svg()
    )

    output_png = Path(tempfile.gettempdir()) / Path("something.png")
    result = subprocess.run(
        [
            "python",
            EXECUTABLE_UNDER_TEST,
            "--id",
            "1",
            "--picture",
            DEFAULT_PICTURE,
            "--output",
            output_png,
            "--stdout",
        ],
        capture_output=True,
    )
    assert result.returncode != 0
    assert "--stdout" in str(result.stdout)


def test_command_file_svg_output():
    output_svg_path = "test1.svg"
    subprocess.run(
        [
            "python",
            EXECUTABLE_UNDER_TEST,
            "--id",
            "1",
            "--picture",
            DEFAULT_PICTURE,
            "--output",
            output_svg_path,
        ]
    )
    with open(output_svg_path) as f:
        output_svg_string = f.read()
    assert _normalize_xml(output_svg_string) == _normalize_xml(
        Slide(DEFAULT_SLIDE_TEMPLATE).id(1).picture(DEFAULT_PICTURE).svg()
    )
    os.unlink(output_svg_path)  # tear down


def test_command_file_png_output():
    output_png_path = "test1.png"
    output_must_not_exist_svg_path = "test1.svg"
    dpi = 400
    assert (
        dpi != SLIDES35_DEFAULT_OUTPUT_DPI
    )  # avoid false positive because of same value as default
    subprocess.run(
        [
            "python",
            EXECUTABLE_UNDER_TEST,
            "--id",
            "1",
            "--picture",
            DEFAULT_PICTURE,
            "--output",
            output_png_path,
            "--dpi",
            str(dpi),
        ]
    )
    assert False == Path(output_must_not_exist_svg_path).exists()
    assert Path(output_png_path).exists()
    svg_w, svg_h = imagesize.get(DEFAULT_SLIDE_TEMPLATE)
    w, h = imagesize.get(output_png_path)
    ratio = w / h
    svg_ratio = w / h
    assert ratio == svg_ratio
    assert w >= svg_w
    assert h >= svg_h
    assert imagesize.getDPI(output_png_path)[0] == dpi
    os.unlink(output_png_path)


def test_command_file_png_output_dir():
    output_dir = Path(tempfile.gettempdir()) / Path("any") / Path("thing")
    output_png_filename = "test2.png"
    output_must_not_exist_svg_path = "test2.svg"
    output_png_path = output_dir / Path(output_png_filename)
    subprocess.run(
        [
            "python",
            EXECUTABLE_UNDER_TEST,
            "--id",
            "1",
            "--picture",
            DEFAULT_PICTURE,
            "--output",
            output_png_filename,
            "--output-dir",
            output_dir,
        ]
    )
    assert False == Path(output_must_not_exist_svg_path).exists()
    assert Path(output_png_path).exists()
    svg_w, svg_h = imagesize.get(DEFAULT_SLIDE_TEMPLATE)
    w, h = imagesize.get(output_png_path)
    ratio = w / h
    svg_ratio = w / h
    assert ratio == svg_ratio
    assert w >= svg_w
    assert h >= svg_h
    shutil.rmtree(output_dir.parent)


def test_command_file_png_output_default_density():
    output_png_path = "test1.png"
    dpi = 320
    assert dpi != SLIDES35_DEFAULT_OUTPUT_DPI
    subprocess.run(
        [
            "python",
            EXECUTABLE_UNDER_TEST,
            "--id",
            "1",
            "--picture",
            DEFAULT_PICTURE,
            "--output",
            output_png_path,
            "--dpi",
            str(dpi),
        ]
    )
    assert imagesize.getDPI(output_png_path)[0] == dpi
    os.unlink(output_png_path)
    subprocess.run(
        [
            "python",
            EXECUTABLE_UNDER_TEST,
            "--id",
            "1",
            "--picture",
            DEFAULT_PICTURE,
            "--output",
            output_png_path,
        ]
    )
    assert imagesize.getDPI(output_png_path)[0] == SLIDES35_DEFAULT_OUTPUT_DPI
    os.unlink(output_png_path)


def test_command_pictures_dir_not_exists():
    result = subprocess.run(
        [
            "python",
            EXECUTABLE_UNDER_TEST,
            "--id",
            "1",
            "--pictures-dir",
            "non-existing-dir",
        ],
        capture_output=True,
    )
    assert result.returncode != 0
    assert "not exist" in str(result.stdout)


def test_command_pictures_impossible_with_stdout():
    with tempfile.TemporaryDirectory() as tmpdirname:
        for n in range(10):
            a = numpy.random.rand(30, 30, 3) * 255
            im_out = Image.fromarray(a.astype("uint8")).convert("RGB")
            im_out.save(Path(tmpdirname) / Path("out%000d.jpg" % n))
        result = subprocess.run(
            [
                "python",
                EXECUTABLE_UNDER_TEST,
                "--id",
                "1",
                "--pictures-dir",
                tmpdirname,
                "--stdout",
            ],
            capture_output=True,
        )
        assert result.returncode == 1
        assert "--pictures-dir cannot be used with --stdout." in str(result.stdout)


def test_do_slide_wrong_output_as_value():
    with pytest.raises(ValueError) as e:
        do_slide(DEFAULT_SLIDE_TEMPLATE, DEFAULT_PICTURE, 1, output_as="bad_extension")
    assert "output_as parameter must be" in e.value.args[0]
