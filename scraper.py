
from PRODUCT_DATA import *
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import json
import os

class Scraper(object):
	"""
	A class that serves as a base for each scraper that is specialized to a 
	particular website. It should contain all data that will need to be customized 
	to scrape from a website. The purpose for this class is that, should a website 
	be updated, simple changes can be made here without disrupting the logic of the 
	scraping process itself.
	"""
	# Methods to extract product data from Selenium elements
	def text_extract(self, element):
		return str(element.text)

	def link_extract(self, element):
		return str(element.get_attribute('href'))

	def image_extract(self, element):
		return str(element.get_attribute('src'))

	def __init__(self):		
		# List of URLs to scrape products from. 
		# These may have to be updated if the site undergoes changes.
		self.urls = []
		# String representing CSS selector to get product entries on page. 
		# The product details are extracted from these parent entries.
		self.product_entry_selector = ''
		# CSS selectors to obtain Selenium elements containing product data. 
		# These may have to be updated if the site undergoes changes.
		self.product_data_selectors = P_DATA.copy()

		# A collection of methods to extract individual pieces of product data 
		self.product_data_extractors = P_DATA.copy()
		self.product_data_extractors[P_LINK] = self.link_extract
		self.product_data_extractors[P_IMAGE] = self.image_extract
		
		for key, value in self.product_data_extractors.iteritems():
			if value is None:
				self.product_data_extractors[key] = self.text_extract

	# Main method. Should not be overridden.
	RETRY_LIMIT = 10
	def execute(self):
		driver = webdriver.Chrome()
		for url in self.urls:
			driver.get(url)
			prods = driver.find_elements_by_css_selector(self.product_selector)
			i = 0
			for p in prods:
				i+=1
				result = P_DATA.copy()
				for attr, sel in self.product_data_selectors.iteritems():
					if sel is not None:
						for x in range(self.RETRY_LIMIT):
							try:
								extractor = self.product_data_extractors[attr]
								result[attr] = \
									extractor(p.find_element_by_css_selector(sel))
								break
							except NoSuchElementException:
								""" If the element is lazily loaded, the product
								may need to be scrolled into view to be 
								accessed """
								if (x + 1 < self.RETRY_LIMIT):
									driver.execute_script("arguments[0].scrollIntoView();", p)
								else:
									print('Did not find ' + attr + ' for product#' + str(i))
				filename = str(i) + '-' + ''.join(x for x in result['name'] if x.isalnum()) + '.json'
				with open(os.path.join(os.getcwd(), 'temp', filename), 'w') as outfile:
					json.dump(result, outfile)
