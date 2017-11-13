from hmscraper import HMScraper
from PRODUCT_DATA import *

hms = HMScraper()
hms.departments = {D_MEN: ['http://www.hm.com/us/products/sale/men/trousers']} # this should provide a couple pages of items
hms.execute()