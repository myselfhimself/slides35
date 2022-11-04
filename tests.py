from slides35 import Slide
from xml.dom import minidom
import pytest

def test_methods_chaining():
    s = Slide().template("a.svg").id(1).comment("Tour simple").picture("01.jpg")
    assert isinstance(s, Slide)

def test_xml_validity():
    s = Slide().template("./templates/blank_diapositive_24x36mm_numbered.svg").id(1).comment("Tour simple").picture("01.jpg")
    minidom.parseString(s.svg()) 

def test_template_setters():
    assert Slide("i.svg") == Slide().template("i.svg")

def test_template_lookup_on_svg_output():
    with pytest.raises(FileNotFoundError):
        Slide("i.svg").svg()

    assert isinstance(Slide("./templates/blank_diapositive_24x36mm_numbered.svg").svg(), str)
