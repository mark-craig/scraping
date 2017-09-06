from aescraper import AEScraper
from uniqloscraper import UniqloScraper
from hmscraper import HMScraper

for scraper in [AEScraper, UniqloScraper, HMScraper]:
	s = scraper()
	try:
		s.execute()
	except Exception as e:
		s.log_crash()