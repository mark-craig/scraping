from scraper import Scraper
from PRODUCT_DATA import *

class HMScraper(Scraper):
	"""
	This is a scraper for Uniqlo.
	"""
	def __init__(self):
		super(HMScraper, self).__init__()
		self.departments = {D_MEN : ['http://www.hm.com/us/products/sale/men']}
		self.product_selector = '.product-list-item'
		self.next_page_selector = '.load-more-btn'
		self.product_data_selectors[P_NAME] = '.product-title'
		self.product_data_selectors[P_CURRENT_PRICE] = '.price'
		self.product_data_selectors[P_ORIGINAL_PRICE] = '.old-price'
		self.product_data_selectors[P_IMAGE] = '.product-image'
		self.product_data_selectors[P_LINK] = '.product-url'

		self.product_data_autofill[P_BRAND] = lambda x: 'H&M'