import asyncio
import os
import json
import re
import aiohttp  # type: ignore
from multiprocessing import Pool, cpu_count
from scrapy.http import HtmlResponse
import aiosqlite
from datetime import datetime

class BestbuySpider:
    def __init__(self, urls):
        self.urls = urls
        self.db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database', 'bestbuy.db'))
        self.cookies = {
            'intl_splash': 'false',
            'locDestZip': '96939',
            'locStoreId': '852',
        }
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'sec-fetch-dest': 'document',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        }

    async def insert_master_data(self, conn, product_name, description):
        query = 'INSERT INTO master_products (product_name, description) VALUES (?, ?)'
        await conn.execute(query, (product_name, description))

    async def insert_hourly_data(self, price, discount, rating_value, review_count, reviewer_1, reviewer_2, reviewer_3):
        query = '''
            INSERT INTO products_2024_11_14 (
                price, discount, rating_value, review_count,
                reviewer_1, reviewer_2, reviewer_3, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        '''
        print((price, discount, rating_value, review_count, 
                                          json.dumps(reviewer_1), json.dumps(reviewer_2), json.dumps(reviewer_3)))
        await self.cursor.execute(query, (price, discount, rating_value, review_count, 
                                          json.dumps(reviewer_1), json.dumps(reviewer_2), json.dumps(reviewer_3)))
        await self.connection.commit()

    async def crawl_data(self, session, url):
        try:
            async with session.get(url, headers=self.headers, cookies=self.cookies) as response:
                # print(response)
                content = await response.text()
                xpath = HtmlResponse(url='', body=content, encoding='utf-8')
                # Crawling xpath adding
                price=xpath.xpath('//*[@data-testid="customer-price"]/span/text()').get('').replace(',','').replace('$','').strip()
                # print(price)
                discount=self.start_end_finder(content, 'priceChangeTotalSavingsAmount":', ',"').strip()
                # print('discount:',discount)
                pickup=xpath.xpath('//*[contains(text()," Selected")]/../div//button[1]/@aria-label').get('').strip()
                if 'Unavailable' in pickup:availability='No'
                else:availability='Yes'

                raw_data = xpath.xpath('//*[@id="product-schema"]/text()').get('').strip()
                json_data=json.loads(raw_data)
                product_name=json_data['name']
                # print('product_name:',product_name)
                description=json_data['description']
                # print('description:',description)
                ratingvalue=json_data['aggregateRating']['ratingValue']
                reviewcount=json_data['aggregateRating']['reviewCount']
                
                top_reviews=json_data['reviews']
                dict_review_1={"ratingValue":top_reviews[0]['reviewRating']['ratingValue'],"reviewTitle":top_reviews[0]['name'],"reviewBody":top_reviews[0]['reviewBody'].replace('\n','').strip()}
                dict_review_2={"ratingValue":top_reviews[0]['reviewRating']['ratingValue'],"reviewTitle":top_reviews[0]['name'],"reviewBody":top_reviews[0]['reviewBody'].replace('\n','').strip()}
                dict_review_3={"ratingValue":top_reviews[0]['reviewRating']['ratingValue'],"reviewTitle":top_reviews[0]['name'],"reviewBody":top_reviews[0]['reviewBody'].replace('\n','').strip()}
                
                self.save_to_database(product_name, description, price, discount,availability, ratingvalue, reviewcount, dict_review_1,dict_review_2,dict_review_3)
        except Exception as e:
            print(f"Error fetching {url}: {e}")

    def start_end_finder(self, data, start, end):
        r = re.findall(re.escape(start) + "(.+?)" + re.escape(end), data, re.DOTALL)
        return r[0] if r else None

    async def crawl_urls(self):
        async with aiohttp.ClientSession() as session:
            tasks = [self.crawl_data(session, url) for url in self.urls]
            await asyncio.gather(*tasks)

    def run(self):
        return asyncio.run(self.crawl_urls())

class URLManager:
    def __init__(self, urls):
        self.urls = urls
        self.num_cores = cpu_count()

    def split_urls(self):
        return [self.urls[i::self.num_cores] for i in range(self.num_cores)]

    def run_crawlers(self):
        urls_split = self.split_urls()
        
        with Pool(self.num_cores) as pool:
            results = pool.map(self._run_single_crawler, urls_split)
        return results

    @staticmethod
    def _run_single_crawler(urls):
        crawler = BestbuySpider(urls)
        return crawler.run()

def main():
    urls = ["https://www.bestbuy.com/site/sony-65-class-bravia-8-oled-4k-uhd-smart-google-tv-2024/6578577.p?skuId=6578577"]  # Add the URLs to crawl
    url_manager = URLManager(urls)
    url_manager.run_crawlers()

if __name__ == "__main__":
    main()
