from __future__ import unicode_literals
from __future__ import absolute_import
from builtins import object
from unidecode import unidecode

from .utils import get_html_from_dynamic_site
from .utils import _get_search_url
from bs4 import BeautifulSoup


class CalculatorResult(object):

    """Represents a result returned from google calculator."""

    def __init__(self):
        self.value = None  # Result value (eg. 157300.0)
        self.from_value = None  # Initial value (eg. 157.3)
        self.unit = None  # Result unit (eg. u'grams') (NOT implemented yet)
        # Initial unit (eg. u'kilograms') (NOT implemented yet)
        self.from_unit = None
        # Initial expression (eg. u'157.3 grams') (NOT implemented yet)
        self.expr = None
        # Result expression  (eg. u'157300 kilograms') (NOT implemented yet)
        self.result = None
        # Complete expression (eg. u'157.3 kilograms = 157300 grams') (NOT
        # implemented yet)
        self.fullstring = None

    def __repr__(self):
        return unidecode(self.value)


# PUBLIC
def calculate(expr):
    """Search for a calculation expression in google.

    Attempts to search google calculator for the result of an expression.
    Returns a `CalculatorResult` if successful or `None` if it fails.

    Args:
        expr: Calculation expression (eg. "cos(25 pi) / 17.4" or
            "157.3kg in grams")

    Returns:
        CalculatorResult object."""

    url = _get_search_url(expr)
    html = get_html_from_dynamic_site(url)
    bs = BeautifulSoup(html)

    cr = CalculatorResult()
    cr.value = _get_to_value(bs)
    cr.from_value = _get_from_value(bs)
    cr.unit = _get_to_unit(bs)
    cr.from_unit = _get_from_unit(bs)
    cr.expr = _get_expr(bs)
    cr.result = _get_result(bs)
    cr.fullstring = _get_fullstring(bs)

    return cr


# PRIVATE
def _get_to_value(bs):
    input_node = bs.find("div", {"id": "_Cif"})
    return float(input_node.find("input")["value"])


def _get_from_value(bs):
    input_node = bs.find("div", {"id": "_Aif"})
    return float(input_node.find("input")["value"])


def _get_to_unit(bs):
    return None


def _get_from_unit(bs):
    return None


def _get_expr(bs):
    return None


def _get_result(bs):
    return None


def _get_fullstring(bs):
    return None
