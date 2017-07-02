from scraper import Scraper
from PRODUCT_DATA import *

class AEScraper(Scraper):
	"""
	This is a scraper for American Eagle Outfitters.
	"""
	urls = ['https://www.ae.com/men-s-clearance/web/s-cat/6470582']
	
	product_selector = '.product-details-container'
	
	product_data_selectors = P_DATA.copy()
	product_data_selectors[P_NAME] = '.product-name span'
	product_data_selectors[P_CURRENT_PRICE] = '.product-saleprice+ .product-saleprice'
	product_data_selectors[P_ORIGINAL_PRICE] = '.product-listprice+ .product-listprice'
	product_data_selectors[P_LINK] = '.product-info a'