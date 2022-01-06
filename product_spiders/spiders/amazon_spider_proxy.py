# -*- coding: utf-8 -*-
import scrapy, requests, random, time
from scrapy import Request
from collections import OrderedDict


class coolstuffinc_comSpider(scrapy.Spider):

	name = "amazon_spider_proxy"

	use_selenium = True
	total_count = 0
	categories_data = None
	result_data_list = {}

	# --------------- Get list of proxy-----------------------#
	proxy_text = requests.get('https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list.txt').text
	list_proxy_temp = proxy_text.split('\n')
	list_proxy = []
	for line in list_proxy_temp:
		if line.strip() !='' and (line.strip()[-1] == '+' or line.strip()[-1] == '-'):
			ip = line.strip().split(':')[0].replace(' ', '')
			port = line.split(':')[-1].split(' ')[0]
			list_proxy.append('http://'+ip+':'+port)

	pass
	########################################################

	# custom_settings = {
	#     'CONCURRENT_REQUESTS': 10,
	#     'DOWNLOAD_DELAY': 1,
	#     'CONCURRENT_REQUESTS_PER_DOMAIN': 4,
	#     'CONCURRENT_REQUESTS_PER_IP': 4
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
				# time.sleep(1)
				proxy = random.choice(self.list_proxy)
				print 'proxy: ' + proxy
				yield scrapy.Request(
					url=category_url.strip(),
					callback=self.parse_list, meta={'category_url': category_url, 'proxy': proxy}, dont_filter=True,
					errback=self.errCall)


	def parse_list(self, response):
		products_link = response.xpath('.//a[@class="a-link-normal a-text-normal"]/@href').extract()
		pro_link_list = []

		if len(products_link) == 0:

			proxy = random.choice(self.list_proxy)
			print 'proxy: ' + proxy
			yield scrapy.Request( response.url, callback=self.parse_list, dont_filter=True, meta={'category_url': response.url, 'proxy': proxy}, errback=self.errCall)

		else:
			# del response.meta['proxy']
			for p in products_link:

				if 'https://www.amazon.com' not in p:
					continue
				if p in pro_link_list:
					continue
				pro_link_list.append(p)
			print('product count: {}'.format(str(len(pro_link_list))))
			print '\n----------------------------'
			# print response.body
			print '-----------------------------------------\n'
			for product_link in pro_link_list:
				# time.sleep(0.5)
				# if 'proxy' in response.meta.keys():
				# 	del response.meta['proxy']
				# product_link = product.xpath('.//a[@class="a-link-normal a-text-normal"]/@href').extract_first()
				yield scrapy.Request( url=response.urljoin(product_link), callback=self.parseProduct, dont_filter=True, meta={'category_url': response.meta['category_url'],
																															  'proxy': response.meta['proxy']}, errback=self.errCallProduct)

			next_page = response.xpath('//a[@id="pagnNextLink"]/@href').extract_first()
			if next_page:
				response.meta['category_url'] = response.urljoin(next_page)
				proxy = random.choice(self.list_proxy)
				print 'proxy: ' + proxy
				yield scrapy.Request( url=response.urljoin(next_page), callback=self.parse_list, dont_filter=True, meta={'category_url': response.urljoin(next_page),
																															  'proxy': proxy}, errback=self.errCall)

		# test= 'https://www.amazon.com/ESQ-Quartz-Stainless-Casual-Silver-Toned/dp/B078C4ZJRM/ref=sr_1_2234?s=apparel&rps=1&ie=UTF8&qid=1530657478&sr=1-2234&nodeID=6358540011&psd=1&refinements=p_85%3A2470955011%2Cp_36%3A20000-30000'
		# yield scrapy.Request( url=response.urljoin(test), callback=self.parseProduct, dont_filter=True, meta=response.meta)
			####------------- test ----------------###
			# if subcategory_url == 'https://www.coolstuffinc.com/page/449':#?&resultsperpage=25&page=2':
			# 	yield scrapy.Request( url=subcategory_url, callback=self.parseProductList, meta={'set_name': set_name } )
			#####################################################

	def get_proxies(self):
		proxy_text = requests.get('https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list.txt').text
		list_proxy_temp = proxy_text.split('\n')
		list_proxy1 = []
		for line in list_proxy_temp:
			if line.strip() !='' and (line.strip()[-1] == '+' or line.strip()[-1] == '-'):
				ip = line.strip().split(':')[0].replace(' ', '')
				port = line.split(':')[-1].split(' ')[0]
				list_proxy1.append('http://'+ip+':'+port)
		self.list_proxy = list_proxy1

	def errCall(self, response):
		ban_proxy = response.request.meta['proxy']
		# self.get_proxies()
		if ban_proxy in self.list_proxy:
			self.list_proxy.remove(ban_proxy)
		else:
			pass
		proxy = random.choice(self.list_proxy)
		# if ban_proxy == proxy:
		# 	index_ban = self.list_proxy.index(ban_proxy)
		# 	if index_ban == 0 :
		# 		index_ban +=1
		# 	else:
		# 		index_ban -=1
		# 	proxy = self.list_proxy[index_ban]
		response.request.meta['proxy'] = proxy

		print 'err proxy: ' + proxy
		yield Request(response.request.meta['category_url'],
					  callback=self.parse_list,
					  meta={'category_url': response.request.meta['category_url'], 'proxy': proxy},
					  dont_filter=True,
					  errback=self.errCall)

	def errCallProduct(self, response):
		ban_proxy = response.request.meta['proxy']
		# self.get_proxies()
		if ban_proxy in self.list_proxy:
			self.list_proxy.remove(ban_proxy)
		else:
			pass
		# self.list_proxy.remove(ban_proxy)
		proxy = random.choice(self.list_proxy)

		print 'err proxy: ' + proxy
		yield Request(response.request.url,
					  callback=self.parse_list,
					  meta={'category_url': response.request.meta['category_url'], 'proxy': proxy},
					  dont_filter=True,
					  errback=self.errCallProduct)

	def again(self, response):
		ban_proxy = response.meta['proxy']

		# self.get_proxies()

		proxy = random.choice(self.list_proxy)
		if ban_proxy == proxy:
			index_ban = self.list_proxy.index(ban_proxy)
			if index_ban == 0 :
				index_ban +=1
			else:
				index_ban -=1
			proxy = self.list_proxy[index_ban]
			# self.list_proxy.remove(ban_proxy)
		response.meta['proxy'] = proxy
		print 'again proxy: ' + proxy
		yield Request(response.meta['category_url'],
					  callback=self.parse_list,
					  meta=response.meta,
					  dont_filter=True,
					  errback=self.errCall)


	def parseProduct(self, response):
		item = OrderedDict()

		item['PageUrl'] = response.meta['category_url']
		item['ProductLink'] = response.url
		if response.xpath('//div[@id="titleSection"]//span[@id="productTitle"]/text()').extract_first():
			item['ProductTitle'] = response.xpath('//div[@id="titleSection"]//span[@id="productTitle"]/text()').extract_first().strip()
			item['Manufacture'] = response.xpath('//div[@id="bylineInfo_feature_div"]//a[@id="bylineInfo"]/text()').extract_first().strip()
			price = response.xpath('.//span[@id="priceblock_pospromoprice"]/text()').extract_first()
			item['Image Url'] = response.xpath('.//*[@id="imgTagWrapperId"]/img/@data-old-hires').extract_first()
			if not price:
				price = response.xpath('.//span[@id="priceblock_ourprice"]/text()').extract_first()
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
				names = ed_path.xpath('./th//text()').extract()
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
			print 'total count : ' + str(self.total_count)
			yield item
