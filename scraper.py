from datetime import datetime
import json
import logging
import os
from PRODUCT_DATA import *
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import shutil
import pdb

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
		if element:
			raw = element.text
			if raw:
				return raw.encode('utf-8')

	def link_extract(self, element):
		if element:
			raw = element.get_attribute('href')
			if raw:
				return raw.encode('utf-8')

	def image_extract(self, element):
		if element:
			raw = element.get_attribute('src')
			if raw:
				return raw.encode('utf-8')

	def price_extract(self, element):
		if element:
			raw = element.text
			if raw:
				rawenc = raw.encode('utf-8')
				return float(''.join([c for c in rawenc if c.isdigit() or c == '.']))

	# Methods to autofill product data for which there may not be a selector
	def calculate_markdown(self, product_data):
		# calculate the markdown, assuming the current price and original price exist
		if product_data[P_CURRENT_PRICE] and product_data[P_ORIGINAL_PRICE]:
			curr = product_data[P_CURRENT_PRICE]
			og = product_data[P_ORIGINAL_PRICE]
			return 1.0 - curr/og
		else:
			# if one is missing, the scraper only found one price, so return 0
			return 0.0
	
	def fill_original_price(self, product_data):
		# if the scraper could not find the original price, assume it's the current one
		return product_data[P_CURRENT_PRICE]


	def fill_current_price(self, product_data):
		# if the scraper could not find the current price, assume it's the original one
		return product_data[P_ORIGINAL_PRICE]


	def __init__(self):
		# Dictonary of URL lists to scrape products from, keyed by department
		# These may have to be updated if the site undergoes changes.
		self.departments = {
			D_MEN : [],
			D_WOMEN : []
		}
		# String representing CSS selector to get product entries on page. 
		# The product details are extracted from these parent entries.
		self.product_selector = ''
		# Some stores have multiple pages for products rather than one page or infinite scrolling
		# If this is the case, set a selector for the 'next page' link here
		self.next_page_selector = ''
		# CSS selectors to obtain Selenium elements containing product data. 
		# These may have to be updated if the site undergoes changes.
		self.product_data_selectors = P_DATA.copy()

		# A collection of methods to extract individual pieces of product data 
		self.product_data_extractors = P_DATA.copy()
		self.product_data_extractors[P_LINK] = self.link_extract
		self.product_data_extractors[P_IMAGE] = self.image_extract
		self.product_data_extractors[P_CURRENT_PRICE] = self.price_extract
		self.product_data_extractors[P_ORIGINAL_PRICE] = self.price_extract
		
		for key, value in self.product_data_extractors.iteritems():
			if value is None:
				self.product_data_extractors[key] = self.text_extract

		# A collection of methods to autofill product data
		# A corresponding method is needed here if data has no selector
		self.product_data_autofill = P_DATA.copy()
		self.product_data_autofill[P_MARKDOWN] = self.calculate_markdown
		self.product_data_autofill[P_ORIGINAL_PRICE] = self.fill_original_price
		self.product_data_autofill[P_CURRENT_PRICE] = self.fill_current_price


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
		for dept, urls in self.departments.iteritems():
			# iterate through the department urls
			for url in urls:
				driver.get(url)
				remaining_page = True
				while remaining_page:
					prods = driver.find_elements_by_css_selector(self.product_selector)
					i = 0
					""" Iterate through the products on the page. If the products are lazily loaded, hopefully
					this will detect that they are present, but the elements contained within the div may not
					be accessible until they are scrolled into view. """
					for p in prods:
						i+=1
						result = P_DATA.copy()
						""" This next line assumes that one can view products by department on a site.
						If for some reason this is not the case, the key in the departments dict
						can be set to None, and an autofill method can be written for P_DEPT """
						result[P_DEPT] = dept
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
						# if result is missing any values, try to autofill them if possible
						for attr, value in result.iteritems():
							if value is None:
								if self.product_data_autofill[attr]:
									self.logger.debug('Attempting to autofill ' + attr + 'for product#' + str(i))
									result[attr] = self.product_data_autofill[attr](result)
								else:
									self.logger.debug('Could not autofill ' + attr + 'for product#' + str(i))
						filename = str(i) + '-' + ''.join(x for x in result['name'] if x.isalnum()) + '.json'
						with open(os.path.join(os.getcwd(), 'temp', filename), 'w') as outfile:
							json.dump(result, outfile)
					# go to next page if applicable
					remaining_page = self.get_next_page(driver)
			
		self.analyze_and_log()

	def get_next_page(self, driver):
		"""If product results are paginated, get the next page with the driver and return True.
			If products are not paginated or there are no more pages, return False."""
		if not self.next_page_selector:
			# not paginated
			return False
		else:
			try: 
				link = driver.find_element_by_css_selector(self.next_page_selector)
				link.click()
				return True
			except NoSuchElementException:
				return False

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