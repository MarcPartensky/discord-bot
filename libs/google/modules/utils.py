from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division

from future import standard_library
standard_library.install_aliases()
from builtins import range
from past.utils import old_div
import time
from selenium import webdriver
import urllib.request
import urllib.error
import urllib.parse
from functools import wraps
# import requests
from urllib.parse import urlencode
from fake_useragent import UserAgent
import sys

class AreaError(KeyError):
    pass


def measure_time(fn):

    def decorator(*args, **kwargs):
        start = time.time()

        res = fn(*args, **kwargs)

        elapsed = time.time() - start
        print(fn.__name__, "took", elapsed, "seconds")

        return res

    return decorator


def normalize_query(query):
    return query.strip().replace(":", "%3A").replace("+", "%2B").replace("&", "%26").replace(" ", "+")


def _get_search_url(query, page=0, per_page=10, lang='en', area='com', ncr=False, time_period=False, sort_by_date=False):
    # note: num per page might not be supported by google anymore (because of
    # google instant)

    params = {
        'nl': lang,
        'q': query.encode('utf8'),
        'start': page * per_page,
        'num': per_page
    }

    time_mapping = {
        'hour': 'qdr:h',
        'week': 'qdr:w',
        'month': 'qdr:m',
        'year': 'qdr:y'
    }


    tbs_param = []
    # Set time period for query if given
    if time_period and time_period in time_mapping:
        tbs_param.append(time_mapping[time_period])

    if sort_by_date:
        tbs_param.append('sbd:1')
    params['tbs'] = ','.join(tbs_param)

    # This will allow to search Google with No Country Redirect
    if ncr:
        params['gl'] = 'us' # Geographic Location: US
        params['pws'] = '0' # 'pws' = '0' disables personalised search
        params['gws_rd'] = 'cr' # Google Web Server ReDirect: CountRy.

    params = urlencode(params)

    url = u"https://www.google.com/search?" + params

    # @author JuaniFilardo:
    # Workaround to switch between http and https, since this maneuver
    # seems to avoid the 503 error when performing a lot of queries.
    # Weird, but it works.
    # You may also wanna wait some time between queries, say, randint(50,65)
    # between each query, and randint(180,240) every 100 queries, which is
    # what I found useful.
    https = int(time.time()) % 2 == 0
    bare_url = u"https://www.google.com/search?" if https else u"http://www.google.com/search?"
    url = bare_url + params

    # return u"http://www.google.com/search?hl=%s&q=%s&start=%i&num=%i" %
    # (lang, normalize_query(query), page * per_page, per_page)
    if not ncr:
        if area == 'com':
            url = u"http://www.google.com/search?"
        elif area == 'is':
            url = 'http://www.google.is/search?'
        elif area == 'dk':
            url = 'http://www.google.dk/search?'
        elif area == 'no':
            url = 'http://www.google.no/search?'
        elif area == 'se':
            url = 'http://www.google.se/search?'
        elif area == 'fi':
            url = 'http://www.google.fi/search?'
        elif area == 'ee':
            url = 'http://www.google.ee/search?'
        elif area == 'lv':
            url = 'http://www.google.lv/search?'
        elif area == 'lt':
            url = 'http://www.google.lt/search?'
        elif area == 'ie':
            url = 'http://www.google.ie/search?'
        elif area == 'uk':
            url = 'http://www.google.co.uk/search?'
        elif area == 'gg':
            url = 'http://www.google.gg/search?'
        elif area == 'je':
            url = 'http://www.google.je/search?'
        elif area == 'im':
            url = 'http://www.google.im/search?'
        elif area == 'fr':
            url = 'http://www.google.fr/search?'
        elif area == 'nl':
            url = 'http://www.google.nl/search?'
        elif area == 'be':
            url = 'http://www.google.be/search?'
        elif area == 'lu':
            url = 'http://www.google.lu/search?'
        elif area == 'de':
            url = 'http://www.google.de/search?'
        elif area == 'at':
            url = 'http://www.google.at/search?'
        elif area == 'ch':
            url = 'http://www.google.ch/search?'
        elif area == 'li':
            url = 'http://www.google.li/search?'
        elif area == 'pt':
            url = 'http://www.google.pt/search?'
        elif area == 'es':
            url = 'http://www.google.es/search?'
        elif area == 'gi':
            url = 'http://www.google.com.gi/search?'
        elif area == 'ad':
            url = 'http://www.google.ad/search?'
        elif area == 'it':
            url = 'http://www.google.it/search?'
        elif area == 'mt':
            url = 'http://www.google.com.mt/search?'
        elif area == 'sm':
            url = 'http://www.google.sm/search?'
        elif area == 'gr':
            url = 'http://www.google.gr/search?'
        elif area == 'ru':
            url = 'http://www.google.ru/search?'
        elif area == 'by':
            url = 'http://www.google.com.by/search?'
        elif area == 'ua':
            url = 'http://www.google.com.ua/search?'
        elif area == 'pl':
            url = 'http://www.google.pl/search?'
        elif area == 'cz':
            url = 'http://www.google.cz/search?'
        elif area == 'sk':
            url = 'http://www.google.sk/search?'
        elif area == 'hu':
            url = 'http://www.google.hu/search?'
        elif area == 'si':
            url = 'http://www.google.si/search?'
        elif area == 'hr':
            url = 'http://www.google.hr/search?'
        elif area == 'ba':
            url = 'http://www.google.ba/search?'
        elif area == 'me':
            url = 'http://www.google.me/search?'
        elif area == 'rs':
            url = 'http://www.google.rs/search?'
        elif area == 'mk':
            url = 'http://www.google.mk/search?'
        elif area == 'bg':
            url = 'http://www.google.bg/search?'
        elif area == 'ro':
            url = 'http://www.google.ro/search?'
        elif area == 'md':
            url = 'http://www.google.md/search?'
        elif area == 'hk':
            url = 'http://www.google.com.hk/search?'
        elif area == 'mn':
            url = 'http://www.google.mn/search?'
        elif area == 'kr':
            url = 'http://www.google.co.kr/search?'
        elif area == 'jp':
            url = 'http://www.google.co.jp/search?'
        elif area == 'vn':
            url = 'http://www.google.com.vn/search?'
        elif area == 'la':
            url = 'http://www.google.la/search?'
        elif area == 'kh':
            url = 'http://www.google.com.kh/search?'
        elif area == 'th':
            url = 'http://www.google.co.th/search?'
        elif area == 'my':
            url = 'http://www.google.com.my/search?'
        elif area == 'sg':
            url = 'http://www.google.com.sg/search?'
        elif area == 'bn':
            url = 'http://www.google.com.bn/search?'
        elif area == 'ph':
            url = 'http://www.google.com.ph/search?'
        elif area == 'id':
            url = 'http://www.google.co.id/search?'
        elif area == 'tp':
            url = 'http://www.google.tp/search?'
        elif area == 'kz':
            url = 'http://www.google.kz/search?'
        elif area == 'kg':
            url = 'http://www.google.kg/search?'
        elif area == 'tj':
            url = 'http://www.google.com.tj/search?'
        elif area == 'uz':
            url = 'http://www.google.co.uz/search?'
        elif area == 'tm':
            url = 'http://www.google.tm/search?'
        elif area == 'af':
            url = 'http://www.google.com.af/search?'
        elif area == 'pk':
            url = 'http://www.google.com.pk/search?'
        elif area == 'np':
            url = 'http://www.google.com.np/search?'
        elif area == 'in':
            url = 'http://www.google.co.in/search?'
        elif area == 'bd':
            url = 'http://www.google.com.bd/search?'
        elif area == 'lk':
            url = 'http://www.google.lk/search?'
        elif area == 'mv':
            url = 'http://www.google.mv/search?'
        elif area == 'kw':
            url = 'http://www.google.com.kw/search?'
        elif area == 'sa':
            url = 'http://www.google.com.sa/search?'
        elif area == 'bh':
            url = 'http://www.google.com.bh/search?'
        elif area == 'ae':
            url = 'http://www.google.ae/search?'
        elif area == 'om':
            url = 'http://www.google.com.om/search?'
        elif area == 'jo':
            url = 'http://www.google.jo/search?'
        elif area == 'il':
            url = 'http://www.google.co.il/search?'
        elif area == 'lb':
            url = 'http://www.google.com.lb/search?'
        elif area == 'tr':
            url = 'http://www.google.com.tr/search?'
        elif area == 'az':
            url = 'http://www.google.az/search?'
        elif area == 'am':
            url = 'http://www.google.am/search?'
        elif area == 'ls':
            url = 'http://www.google.co.ls/search?'
        elif area == 'eg':
            url = 'http://www.google.com.eg/search?'
        elif area == 'ly':
            url = 'http://www.google.com.ly/search?'
        elif area == 'dz':
            url = 'http://www.google.dz/search?'
        elif area == 'ma':
            url = 'http://www.google.co.ma/search?'
        elif area == 'sn':
            url = 'http://www.google.sn/search?'
        elif area == 'gm':
            url = 'http://www.google.gm/search?'
        elif area == 'ml':
            url = 'http://www.google.ml/search?'
        elif area == 'bf':
            url = 'http://www.google.bf/search?'
        elif area == 'sl':
            url = 'http://www.google.com.sl/search?'
        elif area == 'ci':
            url = 'http://www.google.ci/search?'
        elif area == 'gh':
            url = 'http://www.google.com.gh/search?'
        elif area == 'tg':
            url = 'http://www.google.tg/search?'
        elif area == 'bj':
            url = 'http://www.google.bj/search?'
        elif area == 'ne':
            url = 'http://www.google.ne/search?'
        elif area == 'ng':
            url = 'http://www.google.com.ng/search?'
        elif area == 'sh':
            url = 'http://www.google.sh/search?'
        elif area == 'cm':
            url = 'http://www.google.cm/search?'
        elif area == 'td':
            url = 'http://www.google.td/search?'
        elif area == 'cf':
            url = 'http://www.google.cf/search?'
        elif area == 'ga':
            url = 'http://www.google.ga/search?'
        elif area == 'cg':
            url = 'http://www.google.cg/search?'
        elif area == 'cd':
            url = 'http://www.google.cd/search?'
        elif area == 'ao':
            url = 'http://www.google.it.ao/search?'
        elif area == 'et':
            url = 'http://www.google.com.et/search?'
        elif area == 'dj':
            url = 'http://www.google.dj/search?'
        elif area == 'ke':
            url = 'http://www.google.co.ke/search?'
        elif area == 'ug':
            url = 'http://www.google.co.ug/search?'
        elif area == 'tz':
            url = 'http://www.google.co.tz/search?'
        elif area == 'rw':
            url = 'http://www.google.rw/search?'
        elif area == 'bi':
            url = 'http://www.google.bi/search?'
        elif area == 'mw':
            url = 'http://www.google.mw/search?'
        elif area == 'mz':
            url = 'http://www.google.co.mz/search?'
        elif area == 'mg':
            url = 'http://www.google.mg/search?'
        elif area == 'sc':
            url = 'http://www.google.sc/search?'
        elif area == 'mu':
            url = 'http://www.google.mu/search?'
        elif area == 'zm':
            url = 'http://www.google.co.zm/search?'
        elif area == 'zw':
            url = 'http://www.google.co.zw/search?'
        elif area == 'bw':
            url = 'http://www.google.co.bw/search?'
        elif area == 'na':
            url = 'http://www.google.com.na/search?'
        elif area == 'za':
            url = 'http://www.google.co.za/search?'
        elif area == 'au':
            url = 'http://www.google.com.au/search?'
        elif area == 'nf':
            url = 'http://www.google.com.nf/search?'
        elif area == 'nz':
            url = 'http://www.google.co.nz/search?'
        elif area == 'sb':
            url = 'http://www.google.com.sb/search?'
        elif area == 'fj':
            url = 'http://www.google.com.fj/search?'
        elif area == 'fm':
            url = 'http://www.google.fm/search?'
        elif area == 'ki':
            url = 'http://www.google.ki/search?'
        elif area == 'nr':
            url = 'http://www.google.nr/search?'
        elif area == 'tk':
            url = 'http://www.google.tk/search?'
        elif area == 'ws':
            url = 'http://www.google.ws/search?'
        elif area == 'as':
            url = 'http://www.google.as/search?'
        elif area == 'to':
            url = 'http://www.google.to/search?'
        elif area == 'nu':
            url = 'http://www.google.nu/search?'
        elif area == 'ck':
            url = 'http://www.google.co.ck/search?'
        elif area == 'do':
            url = 'http://www.google.com.do/search?'
        elif area == 'tt':
            url = 'http://www.google.tt/search?'
        elif area == 'co':
            url = 'http://www.google.com.co/search?'
        elif area == 'ec':
            url = 'http://www.google.com.ec/search?'
        elif area == 've':
            url = 'http://www.google.co.ve/search?'
        elif area == 'gy':
            url = 'http://www.google.gy/search?'
        elif area == 'pe':
            url = 'http://www.google.com.pe/search?'
        elif area == 'bo':
            url = 'http://www.google.com.bo/search?'
        elif area == 'py':
            url = 'http://www.google.com.py/search?'
        elif area == 'br':
            url = 'http://www.google.com.br/search?'
        elif area == 'uy':
            url = 'http://www.google.com.uy/search?'
        elif area == 'ar':
            url = 'http://www.google.com.ar/search?'
        elif area == 'cl':
            url = 'http://www.google.cl/search?'
        elif area == 'gl':
            url = 'http://www.google.gl/search?'
        elif area == 'ca':
            url = 'http://www.google.ca/search?'
        elif area == 'mx':
            url = 'http://www.google.com.mx/search?'
        elif area == 'gt':
            url = 'http://www.google.com.gt/search?'
        elif area == 'bz':
            url = 'http://www.google.com.bz/search?'
        elif area == 'sv':
            url = 'http://www.google.com.sv/search?'
        elif area == 'hn':
            url = 'http://www.google.hn/search?'
        elif area == 'ni':
            url = 'http://www.google.com.ni/search?'
        elif area == 'cr':
            url = 'http://www.google.co.cr/search?'
        elif area == 'pa':
            url = 'http://www.google.com.pa/search?'
        elif area == 'bs':
            url = 'http://www.google.bs/search?'
        elif area == 'cu':
            url = 'http://www.google.com.cu/search?'
        elif area == 'jm':
            url = 'http://www.google.com.jm/search?'
        elif area == 'ht':
            url = 'http://www.google.ht/search?'
        else:
            raise AreaError('invalid  name,  no area found')
        url += params
    return url


def get_html(url):
    ua = UserAgent()
    header = ua.random

    try:
        request = urllib.request.Request(url)
        request.add_header("User-Agent", header)
        html = urllib.request.urlopen(request).read()
        return html
    except urllib.error.HTTPError as e:
        print("Error accessing:", url)
        print(e)
        if e.code == 503 and 'CaptchaRedirect' in e.read():
            print("Google is requiring a Captcha. "
                  "For more information check: 'https://support.google.com/websearch/answer/86640'")
        if e.code == 503:
            sys.exit("503 Error: service is currently unavailable. Program will exit.")
        return None
    except Exception as e:
        print("Error accessing:", url)
        print(e)
        return None


def write_html_to_file(html, filename):
    of = open(filename, "w")
    of.write(html.encode("utf-8"))
    # of.flush()
    of.close()


def get_browser_with_url(url, timeout=120, driver="firefox"):
    """Returns an open browser with a given url."""

    # choose a browser
    if driver == "firefox":
        browser = webdriver.Firefox()
    elif driver == "ie":
        browser = webdriver.Ie()
    elif driver == "chrome":
        browser = webdriver.Chrome()
    else:
        print("Driver choosen is not recognized")

    # set maximum load time
    browser.set_page_load_timeout(timeout)

    # open a browser with given url
    browser.get(url)

    time.sleep(0.5)

    return browser


def get_html_from_dynamic_site(url, timeout=120,
                               driver="firefox", attempts=10):
    """Returns html from a dynamic site, opening it in a browser."""

    RV = ""

    # try several attempts
    for i in range(attempts):
        try:
            # load browser
            browser = get_browser_with_url(url, timeout, driver)

            # get html
            time.sleep(2)
            content = browser.page_source

            # try again if there is no content
            if not content:
                browser.quit()
                raise Exception("No content!")

            # if there is content gets out
            browser.quit()
            RV = content
            break

        except:
            print("\nTry ", i, " of ", attempts, "\n")
            time.sleep(5)

    return RV


def timeit(func=None, loops=1, verbose=False):
    if func:
        def inner(*args, **kwargs):

            sums = 0.0
            mins = 1.7976931348623157e+308
            maxs = 0.0
            print('====%s Timing====' % func.__name__)
            for i in range(0, loops):
                t0 = time.time()
                result = func(*args, **kwargs)
                dt = time.time() - t0
                mins = dt if dt < mins else mins
                maxs = dt if dt > maxs else maxs
                sums += dt
                if verbose:
                    print('\t%r ran in %2.9f sec on run %s' %
                          (func.__name__, dt, i))
            print('%r min run time was %2.9f sec' % (func.__name__, mins))
            print('%r max run time was %2.9f sec' % (func.__name__, maxs))
            print('%r avg run time was %2.9f sec in %s runs' %
                  (func.__name__, old_div(sums, loops), loops))
            print('==== end ====')
            return result

        return inner
    else:
        def partial_inner(func):
            return timeit(func, loops, verbose)
        return partial_inner


def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()
        print('func:%r args:[%r, %r] took: %2.4f sec' %
              (f.__name__, args, kw, te - ts))
        return result
    return wrap
