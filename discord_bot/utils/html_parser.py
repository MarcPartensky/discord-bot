import html.parser
import requests


class Parser(html.parser.HTMLParser):
    """Modified HTMLParser that isolates a tag with the specified id"""

    def __init__(
        self, tag, key, value, fetched_tags=["p", "li", "a"], new_line_tags=["p", "li"]
    ):
        super().__init__()
        self.tag = tag
        self.key = key
        self.value = value
        self.result = ""
        self.fetching = None
        self.depth = 0
        self.count = 0
        self.tags = {}
        self.fetched_tags = fetched_tags
        self.new_line_tags = new_line_tags

    def load(self, html):
        self.html = html
        self.feed(html)
        self.close()

    def handle_starttag(self, tag, attrs):
        if not tag in self.tags:
            self.tags[tag] = 1
        else:
            self.tags[tag] += 1

        attrs = dict(attrs)
        if self.fetching:
            if self.tag == tag:
                self.depth += 1
        else:
            if self.tag == tag:
                if self.key in attrs:
                    if self.value == attrs[self.key]:
                        if self.count == 0:
                            self.fetching = True
                            self.depth = 1

    def handle_endtag(self, tag):
        self.tags[tag] -= 1
        if self.fetching:
            if self.tag == tag:
                self.depth -= 1
                if self.depth == 0:
                    self.fetching = False
                    self.count += 1

            if tag in self.new_line_tags:
                self.result += "\n"
            else:
                if len(self.result) > 1:
                    if not self.result[-1] == " ":
                        self.result += " "

    def handle_data(self, data):
        if self.fetching:
            for tag in self.fetched_tags:
                if tag in self.tags:
                    if self.tags[tag]:
                        self.result += data
                        break


if __name__ == "__main__":
    resp = requests.get("https://fr.wikipedia.org/wiki/Esclave")
    parser = Parser("div", "class", "mw-parser-output", fetched_tags=["p", "li", "a"])
    parser.load(resp.text)
    print(parser.result)
