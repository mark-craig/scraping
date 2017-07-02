
from PRODUCT_DATA import *
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import json
import os

class Scraper:
	"""
	A class that serves as a base for each scraper that is specialized to a 
	particular website. It should contain all data that will need to be customized 
	to scrape from a website. The purpose for this class is that, should a website 
	be updated, simple changes can be made here without disrupting the logic of the 
	scraping process itself.
	"""

	# List of URLs to scrape products from. 
	# These may have to be updated if the site undergoes changes.
	urls = []
	# String representing CSS selector to get product entries on page. 
	# The product details are extracted from these parent entries.
	product_entry_selector = ''
	# CSS selectors to obtain Selenium elements containing product data. 
	# These may have to be updated if the site undergoes changes.
	product_data_selectors = P_DATA.copy()

	# Methods to extract product data from Selenium elements
	def default_extract(element):
		return str(element.text)

	def link_extract(element):
		return str(element.get_attribute('href'))

	# A collection of methods to extract individual pieces of product data 
	product_data_extractors = P_DATA.copy()
	product_data_extractors[P_LINK] = link_extract
	
	for key, value in product_data_extractors.iteritems():
		if value is None:
			product_data_extractors[key] = default_extract



	# Main method. Should not be overridden.
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
						try:
							extractor = self.product_data_extractors[attr]
							result[attr] = \
								extractor(p.find_element_by_css_selector(sel))
						except NoSuchElementException:
							print('Did not find ' + attr + ' for product#' + str(i))
				filename = str(i) + '-' + ''.join(x for x in result['name'] if x.isalnum()) + '.json'
				with open(os.path.join(os.getcwd(), 'temp', filename), 'w') as outfile:
					json.dump(result, outfile)
