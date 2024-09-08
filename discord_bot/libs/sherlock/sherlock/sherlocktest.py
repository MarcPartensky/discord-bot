from .notify import QueryNotifyPrint
from .sites import SitesInformation

from . import sherlock as sh

sites = SitesInformation(None)

# Create original dictionary from SitesInformation() object.
# Eventually, the rest of the code will be updated to use the new object
# directly, but this will glue the two pieces together.
site_data_all = {}
for site in sites:
    site_data_all[site.name] = site.information

site_data = site_data_all

# print(site_data)

# Create notify object for query results.
query_notify = QueryNotifyPrint()


def search(username):
    return sh.sherlock(username, site_data, query_notify)


if __name__ == "__main__":
    results = search("mazex")
    print(results["tracr.co"])
