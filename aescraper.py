from scraper import Scraper
from PRODUCT_DATA import *

class AEScraper(Scraper):
	"""
	This is a scraper for American Eagle Outfitters.
	"""
	def image_extract(self, element):
		result = str(element.get_attribute('srcset'))
		# cleanup string
		return result.split()[0]

	def __init__(self):
		super(AEScraper, self).__init__()
		self.urls = ['https://www.ae.com/men-s-clearance/web/s-cat/6470582']
		self.product_selector = '.product-details-container'
		self.product_data_selectors[P_NAME] = '.product-name span'
		self.product_data_selectors[P_CURRENT_PRICE] = '.product-saleprice+ .product-saleprice'
		self.product_data_selectors[P_ORIGINAL_PRICE] = '.product-listprice+ .product-listprice'
		self.product_data_selectors[P_IMAGE] = '.lazyloaded'
		self.product_data_selectors[P_LINK] = '.product-info a'

		self.product_data_autofill[P_BRAND] = lambda x: 'American Eagle Outfitters'