from __future__ import unicode_literals
from __future__ import absolute_import

from future import standard_library
standard_library.install_aliases()
from builtins import range
from builtins import object
from .utils import _get_search_url, get_html
from bs4 import BeautifulSoup
import urllib.parse
from urllib.parse import unquote, parse_qs, urlparse
from unidecode import unidecode
from re import match, findall


class GoogleResult(object):

    """Represents a google search result."""

    def __init__(self):
        self.name = None  # The title of the link
        self.link = None  # The external link
        self.google_link = None  # The google link
        self.description = None  # The description of the link
        self.thumb = None  # Thumbnail link of website (NOT implemented yet)
        self.cached = None  # Cached version link of page
        self.page = None  # Results page this one was on
        self.index = None  # What index on this page it was on
        self.number_of_results = None # The total number of results the query returned

    def __repr__(self):
        name = self._limit_str_size(self.name, 55)
        description = self._limit_str_size(self.description, 49)

        list_google = ["GoogleResult(",
                       "name={}".format(name), "\n", " " * 13,
                       "description={}".format(description)]

        return "".join(list_google)

    def _limit_str_size(self, str_element, size_limit):
        """Limit the characters of the string, adding .. at the end."""
        if not str_element:
            return None

        elif len(str_element) > size_limit:
            return unidecode(str_element[:size_limit]) + ".."

        else:
            return unidecode(str_element)


# PUBLIC
def search(query, pages=1, lang='en', area='com', ncr=False, void=True, time_period=False, sort_by_date=False, first_page=0):
    """Returns a list of GoogleResult.

    Args:
        query: String to search in google.
        pages: Number of pages where results must be taken.
        area : Area of google homepages.
        first_page : First page.

    TODO: add support to get the google results.
    Returns:
        A GoogleResult object."""

    results = []
    for i in range(first_page, first_page + pages):
        url = _get_search_url(query, i, lang=lang, area=area, ncr=ncr, time_period=time_period, sort_by_date=sort_by_date)
        html = get_html(url)

        if html:
            soup = BeautifulSoup(html, "html.parser")
            divs = soup.findAll("div", attrs={"class": "g"})

            results_div = soup.find("div", attrs={"id": "resultStats"})
            number_of_results = _get_number_of_results(results_div)

            j = 0
            for li in divs:
                res = GoogleResult()

                res.page = i
                res.index = j

                res.name = _get_name(li)
                res.link = _get_link(li)
                res.google_link = _get_google_link(li)
                res.description = _get_description(li)
                res.thumb = _get_thumb()
                res.cached = _get_cached(li)
                res.number_of_results = number_of_results

                if void is True:
                    if res.description is None:
                        continue
                results.append(res)
                j += 1
    return results


# PRIVATE
def _get_name(li):
    """Return the name of a google search."""
    a = li.find("a")
    # return a.text.encode("utf-8").strip()
    if a is not None:
        return a.text.strip()
    return None


def _filter_link(link):
    '''Filter links found in the Google result pages HTML code.
    Returns None if the link doesn't yield a valid result.
    '''
    try:
        # Valid results are absolute URLs not pointing to a Google domain
        # like images.google.com or googleusercontent.com
        o = urlparse(link, 'http')
        # link type-1
        # >>> "https://www.gitbook.com/book/ljalphabeta/python-"
        if o.netloc and 'google' not in o.netloc:
            return link
        # link type-2
        # >>> "http://www.google.com/url?url=http://python.jobbole.com/84108/&rct=j&frm=1&q=&esrc=s&sa=U&ved=0ahUKEwj3quDH-Y7UAhWG6oMKHdQ-BQMQFggUMAA&usg=AFQjCNHPws5Buru5Z71wooRLHT6mpvnZlA"
        if o.netloc and o.path.startswith('/url'):
            try:
                link = parse_qs(o.query)['url'][0]
                o = urlparse(link, 'http')
                if o.netloc and 'google' not in o.netloc:
                    return link
            except KeyError:
                pass
        # Decode hidden URLs.
        if link.startswith('/url?'):
            try:
                # link type-3
                # >>> "/url?q=http://python.jobbole.com/84108/&sa=U&ved=0ahUKEwjFw6Txg4_UAhVI5IMKHfqVAykQFggUMAA&usg=AFQjCNFOTLpmpfqctpIn0sAfaj5U5gAU9A"
                link = parse_qs(o.query)['q'][0]
                # Valid results are absolute URLs not pointing to a Google domain
                # like images.google.com or googleusercontent.com
                o = urlparse(link, 'http')
                if o.netloc and 'google' not in o.netloc:
                    return link
            except KeyError:
                # link type-4
                # >>> "/url?url=https://machine-learning-python.kspax.io/&rct=j&frm=1&q=&esrc=s&sa=U&ved=0ahUKEwj3quDH-Y7UAhWG6oMKHdQ-BQMQFggfMAI&usg=AFQjCNEfkUI0RP_RlwD3eI22rSfqbYM_nA"
                link = parse_qs(o.query)['url'][0]
                o = urlparse(link, 'http')
                if o.netloc and 'google' not in o.netloc:
                    return link

    # Otherwise, or on error, return None.
    except Exception:
        pass
    return None


def _get_link(li):
    """Return external link from a search."""
    try:
        a = li.find("a")
        link = a["href"]
    except Exception:
        return None
    return _filter_link(link)


def _get_google_link(li):
    """Return google link from a search."""
    try:
        a = li.find("a")
        link = a["href"]
    except Exception:
        return None

    if link.startswith("/url?") or link.startswith("/search?"):
        return urllib.parse.urljoin("http://www.google.com", link)

    else:
        return None


def _get_description(li):
    """Return the description of a google search.

    TODO: There are some text encoding problems to resolve."""

    sdiv = li.find("div", attrs={"class": "s"})
    if sdiv:
        stspan = sdiv.find("span", attrs={"class": "st"})
        if stspan is not None:
            # return stspan.text.encode("utf-8").strip()
            return stspan.text.strip()
    else:
        return None


def _get_thumb():
    """Return the link to a thumbnail of the website."""
    pass


def _get_cached(li):
    """Return a link to the cached version of the page."""
    links = li.find_all("a")
    if len(links) > 1 and links[1].text == "Cached":
        link = links[1]["href"]
        if link.startswith("/url?") or link.startswith("/search?"):
            return urllib.parse.urljoin("http://www.google.com", link)
    return None

def _get_number_of_results(results_div):
    """Return the total number of results of the google search.
    Note that the returned value will be the same for all the GoogleResult
    objects from a specific query."""
    try:
        results_div_text = results_div.get_text()
        if results_div_text:
            regex = r"((?:\d+[,\.])*\d+)"
            m = findall(regex, results_div_text)

            # Clean up the number.
            num = m[0].replace(",", "").replace(".", "")

            results = int(num)
            return results
    except Exception as e:
        return 0
