# -*- coding: utf-8 -*-
import scrapy, time
from scrapy import Request
from collections import OrderedDict


class coolstuffinc_comSpider(scrapy.Spider):

	name = "amazon_spider"

	use_selenium = True
	total_count = 0
	categories_data = None
	result_data_list = []

	# --------------- Get list of proxy-----------------------#
	# proxy_text = requests.get('https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list.txt').text
	# list_proxy_temp = proxy_text.split('\n')
	# list_proxy = []
	# for line in list_proxy_temp:
	# 	if line.strip() !='' and (line.strip()[-1] == '+' or line.strip()[-1] == '-'):
	# 		ip = line.strip().split(':')[0].replace(' ', '')
	# 		port = line.split(':')[-1].split(' ')[0]
	# 		list_proxy.append('http://'+ip+':'+port)
    #
	# pass
	########################################################

	# custom_settings = {
	#     'CONCURRENT_REQUESTS': 2,
	#     'DOWNLOAD_DELAY': 0.5,
	#     'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
	#     'CONCURRENT_REQUESTS_PER_IP': 2
	# }

	# headers = ['PageUrl', 'ProductLink', 'ImageLink', 'Rarity', 'ProductTitle', 'NewQty', 'NewPrice', 'NewContent', 'NearMintQty', 'NearMintPrice', 'NearMintContent',
	# 		   'FoilNearMintQty', 'FoilNearMintPrice', 'FoilNearMintContent',
	# 		   'PlayedQty', 'PlayedPrice', 'PlayedContent', 'FoilPlayedQty', 'FoilPlayedPrice', 'FoilPlayedContent', 'SetName']


###########################################################

	def __init__(self, *args, **kwargs):
		super(coolstuffinc_comSpider, self).__init__(*args, **kwargs)
###########################################################

	def start_requests(self):
		filename = "basic_data/categories.txt"
		with open(filename, 'U') as f:
			for category_url in f.readlines():
				# time.sleep(0.5)
				yield scrapy.Request(
					url=category_url.strip(),
					callback=self.parse_list, meta={'category_url': category_url}, dont_filter=True)
				# break


	def parse_list(self, response):
		products_link = response.xpath('.//a[@class="a-link-normal a-text-normal"]/@href').extract()
		pro_link_list = []
		for p in products_link:
			if 'https://www.amazon.com' not in p:
				continue
			if p in pro_link_list:
				continue
			pro_link_list.append(p)
		print('product count: {}'.format(str(len(pro_link_list))))
		print '\n----------------------------'
		print response.url
		# print response.body
		print '-----------------------------------------\n'
		for product_link in pro_link_list:
			# time.sleep(0.5)
			# product_link = product.xpath('.//a[@class="a-link-normal a-text-normal"]/@href').extract_first()
			yield scrapy.Request( url=response.urljoin(product_link), callback=self.parseProduct, dont_filter=True, meta=response.meta)
			# return

		next_page = response.xpath('//a[@id="pagnNextLink"]/@href').extract_first()
		if next_page:
			response.meta['category_url'] = response.urljoin(next_page)
			yield scrapy.Request( url=response.urljoin(next_page), callback=self.parse_list, dont_filter=True, meta=response.meta)



	def parseProduct(self, response):
		item = OrderedDict()

		item['PageUrl'] = response.meta['category_url']
		item['ProductLink'] = response.url
		if response.xpath('//div[@id="titleSection"]//span[@id="productTitle"]/text()').extract_first():
			item['ProductTitle'] = response.xpath('//div[@id="titleSection"]//span[@id="productTitle"]/text()').extract_first().strip()
			item['Manufacture'] = response.xpath('//div[@id="bylineInfo_feature_div"]//a[@id="bylineInfo"]/text()').extract_first()

			price = response.xpath('.//span[@id="priceblock_pospromoprice"]/text()').extract_first()
			item['Image Url'] = response.xpath('.//*[@id="imgTagWrapperId"]/img/@data-old-hires').extract_first()
			if not price:
				price = response.xpath('.//span[@id="priceblock_ourprice"]/text()').extract_first()
				if not price:
					prices = response.xpath('//div[@class="a-section a-spacing-small a-spacing-top-small"]//b[text()="Used"]/parent::a/text()').re(r'[$\d.,]+')
					if prices:
						price = prices[0]
			item['ProductPrice'] = price

			item['ASIN'] = ''
			detailBullets_feature_div_lis = response.xpath('.//*[@id="detailBullets_feature_div"]/ul/li')
			for detailBullets_feature_div in detailBullets_feature_div_lis:
				s = ''.join(detailBullets_feature_div.xpath('./span//text()').extract())
				if 'ASIN:' in s:
					s = s.split('ASIN:')[-1].strip()
					item['ASIN'] = s



			descs = response.xpath('.//*[@id="productDescription"]//text()').extract()
			item['Description'] = ''
			desc_str = ''
			for d in descs:
				d = d.strip()
				if d:
					desc_str += d
			item['Description'] = desc_str

			specs = response.xpath('//*[@id="technicalSpecifications_section_1"]//tr')

			item['Extra Description'] = ''

			e_desc = ''
			for ed_path in specs:
				names = ed_path.xpath('./th/text()').extract_first()

				if not isinstance(names, list):
					name = names.strip()
				else:
					name = ''
					for s in names:
						s = s.strip()
						if not s:
							continue
						name = s.strip().encode('utf-8')
						break

				if name:
					name = name.strip().encode('utf-8')
				else:
					continue
				val = ed_path.xpath('./td/text()').extract_first()
				if val:
					val = val.strip().encode('utf-8')
				else:
					val = ''

				e_desc += '{}:{}\n'.format(name, val)
			item['Extra Description'] = e_desc

			self.total_count += 1
			print('total count : ' + str(self.total_count))
			self.result_data_list.append(item)
			# yield item
