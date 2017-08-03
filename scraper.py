from datetime import datetime
import json
import logging
import os
from PRODUCT_DATA import *
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import shutil

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


		# make sure there is a temp directory and a log directory
		if not os.path.exists(os.path.join(os.getcwd(), 'temp')):
			os.makedirs(os.path.join(os.getcwd(), 'temp'))

		if not os.path.exists(os.path.join(os.getcwd(), 'logs')):
			os.makedirs(os.path.join(os.getcwd(), 'logs'))

		# set up the logger
		self.logger = logging.getLogger(__name__)
		log_file_name = os.path.join(os.getcwd(), 'logs', datetime.now().strftime("%d_%m_%Y.log"))
		self.logger.setLevel(logging.DEBUG)
		handler = logging.FileHandler(log_file_name)
		handler.setLevel(logging.DEBUG)
		formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		handler.setFormatter(formatter)
		self.logger.addHandler(handler)


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
									self.logger.debug('Did not find ' + attr + ' for product#' + str(i))
				filename = str(i) + '-' + ''.join(x for x in result['name'] if x.isalnum()) + '.json'
				with open(os.path.join(os.getcwd(), 'temp', filename), 'w') as outfile:
					json.dump(result, outfile)
		self.analyze_and_log()

	def analyze_and_log(self):
		total_values = 0.0
		valid_values = 0.0
		directory = os.path.join(os.getcwd(), 'temp')
		number_of_entries = len(os.listdir(directory))
		for filename in os.listdir(directory):
			with open(os.path.join(directory, filename)) as json_data:
				data = json.load(json_data)
				total_values += len(data.values())
				for v in data.values():
					if v is not None:
						valid_values += 1

		self.logger.info('Accuracy of ' + str(valid_values/total_values) + ' across ' + str(number_of_entries) + ' products')