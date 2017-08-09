"""
This file simply provides a dictionary template and keywords to organize objects and methods correlating to product data.
"""
P_NAME = 'name'
P_CURRENT_PRICE = 'current_price'
P_ORIGINAL_PRICE = 'original_price'
P_MARKDOWN = 'markdown'
P_IMAGE = 'image'
P_LINK = 'link'
P_BRAND = 'brand'
P_DEPT = 'department'

# This dictionary can be copied to provide a place to collect functions or objects corresponding to product data
P_DATA = {
	P_NAME : None,
	P_CURRENT_PRICE : None,
	P_ORIGINAL_PRICE : None,
	P_MARKDOWN : None,
	P_IMAGE : None,
	P_LINK : None,
	P_BRAND : None,
	P_DEPT : None
}

# These are the constant keywords for different departments products may belong to
D_MEN = "MEN'S"
D_WOMEN = "WOMEN'S"