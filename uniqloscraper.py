from scraper import Scraper
from PRODUCT_DATA import *

class UniqloScraper(Scraper):
	"""
	This is a scraper for Uniqlo.
	"""
	def __init__(self):
		super(UniqloScraper, self).__init__()
		self.departments = {D_MEN : ['https://www.uniqlo.com/us/en/men/sale'], D_WOMEN : ['https://www.uniqlo.com/us/en/women/sale']}
		self.product_selector = '.grid-tile'
		self.product_data_selectors[P_NAME] = '.name-link'
		self.product_data_selectors[P_CURRENT_PRICE] = '.product-sales-price'
		self.product_data_selectors[P_ORIGINAL_PRICE] = '.product-standard-price'
		self.product_data_selectors[P_IMAGE] = '.thumb-link img'
		self.product_data_selectors[P_LINK] = '.name-link'

		self.product_data_autofill[P_BRAND] = lambda x: 'Uniqlo'