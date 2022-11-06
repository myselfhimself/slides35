from slides35 import Slide, SLIDES35_DEFAULT_SVG_TEMPLATE
from xml.dom import minidom
import pytest
from pathlib import Path

DEFAULT_SLIDE_TEMPLATE=SLIDES35_DEFAULT_SVG_TEMPLATE
DEFAULT_NON_EXISTING_TEMPLATE="missingTemplate.svg"
DEFAULT_PICTURE=str(Path("./templates/24x36mmImage.png"))
DEFAULT_NON_EXISTING_PICTURE="missingPicture.png"
DEFAULT_COMMENT="Tour simple"
EXECUTABLE_UNDER_TEST="slides35.py"

def test_methods_chaining():
    s = Slide().template(DEFAULT_SLIDE_TEMPLATE).id(1).comment(DEFAULT_COMMENT).picture(DEFAULT_PICTURE)
    assert isinstance(s, Slide)

def test_xml_validity():
    s = Slide().template(DEFAULT_SLIDE_TEMPLATE).id(1).comment(DEFAULT_COMMENT).picture(DEFAULT_PICTURE)
    minidom.parseString(s.svg()) 

def test_template_setters():
    assert Slide(DEFAULT_SLIDE_TEMPLATE) == Slide().template(DEFAULT_SLIDE_TEMPLATE)

def test_template_lookup_on_svg_output():
    with pytest.raises(FileNotFoundError):
        Slide(DEFAULT_NON_EXISTING_TEMPLATE)

    assert isinstance(Slide(DEFAULT_SLIDE_TEMPLATE).id(1).picture(DEFAULT_PICTURE).svg(), str)

def test_picture_setter_getter():
    assert Slide().picture(DEFAULT_PICTURE).picture() == DEFAULT_PICTURE
    with pytest.raises(FileNotFoundError):
        Slide().picture(DEFAULT_NON_EXISTING_PICTURE)

def test_command(capsys):
    import subprocess
    command_output = subprocess.check_output(["python", "slides35.py", "--id", "1", "--picture", "templates/24x36mmImage.png"])
    assert minidom.parseString(command_output).toxml() == minidom.parseString(Slide(DEFAULT_SLIDE_TEMPLATE).id(1).picture(DEFAULT_PICTURE).svg()).toxml()
