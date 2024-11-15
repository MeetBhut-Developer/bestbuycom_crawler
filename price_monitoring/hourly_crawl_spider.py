import asyncio
import os
import json
import re
import aiohttp
from multiprocessing import Pool, cpu_count
from scrapy.http import HtmlResponse
import sqlite3

class BestbuySpider:
    def __init__(self, ids_urls):
        self.ids_urls = ids_urls
        self.connection = None
        self.cookies = {
            'intl_splash': 'false',
            'locDestZip': '96939',
            'locStoreId': '852',
        }

        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'priority': 'u=0, i',
            'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        }

    def db_connect(self):
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(script_dir, '..', 'database', 'bestbuy.db')
            db_path = os.path.abspath(db_path)
            self.connection = sqlite3.connect(db_path)
        except ConnectionError as err:
            print(err)
            self.connection = None

    def fetch_urls_from_db(self):
        self.db_connect()
        cursor = self.connection.cursor()
        cursor.execute("SELECT product_id, product_url FROM master_products;")
        ids_urls = cursor.fetchall()
        self.db_close()
        return ids_urls

    def start_end_finder(self, data, start, end):
        r = re.findall(re.escape(start) + "(.+?)" + re.escape(end), data, re.DOTALL)
        return r[0] if r else None

    async def crawl_data(self, session, id_url):
        id, url = id_url
        try:
            async with session.get(url, headers=self.headers, cookies=self.cookies) as response:
                content = await response.text()
                print("Status:", response.status)
                xpath = HtmlResponse(url='', body=content, encoding='utf-8')
                
                price=xpath.xpath('//*[@data-testid="customer-price"]/span/text()').get('').replace(',','').replace('$','').strip()
                discount=self.start_end_finder(content, 'priceChangeTotalSavingsAmount":', ',"').strip()
                pickup=xpath.xpath('//*[contains(text()," Selected")]/../div//button[1]/@aria-label').get('').strip()
                if 'Unavailable' in pickup:availability='No'
                else:availability='Yes'

                raw_data = xpath.xpath('//*[@id="product-schema"]/text()').get('').strip()
                json_data=json.loads(raw_data)
                
                ratingvalue=json_data['aggregateRating']['ratingValue']
                reviewcount=json_data['aggregateRating']['reviewCount']
                
                top_reviews=json_data['reviews']
                dict_review_1={"ratingValue":top_reviews[0]['reviewRating']['ratingValue'],"reviewTitle":top_reviews[0]['name'],"reviewBody":top_reviews[0]['reviewBody'].replace('\n','').strip()}
                dict_review_2={"ratingValue":top_reviews[0]['reviewRating']['ratingValue'],"reviewTitle":top_reviews[0]['name'],"reviewBody":top_reviews[0]['reviewBody'].replace('\n','').strip()}
                dict_review_3={"ratingValue":top_reviews[0]['reviewRating']['ratingValue'],"reviewTitle":top_reviews[0]['name'],"reviewBody":top_reviews[0]['reviewBody'].replace('\n','').strip()}
                
                
                self.db_connect()
                cursor = self.connection.cursor()
                cursor.execute(
                    f"INSERT INTO products_2024_11_14 (product_id, price, availability, discount, rating_value, review_count, reviewer_1, reviewer_2, reviewer_3) VALUES (?, ?, ?, ?,?, ?, ?, ?,?);",
                    (id, float(price), availability, float(discount), float(ratingvalue),int(reviewcount) , json.dumps(dict_review_1), json.dumps(dict_review_2), json.dumps(dict_review_3))
                )
                print('Data Inserted!')
                self.connection.commit()
                self.db_close()
                print('***' * 10)

        except Exception as e:
            print(f"Error fetching {url}: {e}")

    async def crawl_urls(self):
        async with aiohttp.ClientSession() as session:
            tasks = [self.crawl_data(session, id_url) for id_url in self.ids_urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

    def run(self):
        return asyncio.run(self.crawl_urls())

    def db_close(self):
        if self.connection:
            self.connection.close()


class URLManager:
    def __init__(self):
        self.num_cores = cpu_count()

    def fetch_urls_for_crawling(self):
        spider = BestbuySpider([])
        return spider.fetch_urls_from_db()

    def split_urls(self, ids_urls):
        return [ids_urls[i::self.num_cores] for i in range(self.num_cores)]

    def run_crawlers(self):
        ids_urls = self.fetch_urls_for_crawling()
        urls_split = self.split_urls(ids_urls)

        with Pool(self.num_cores) as pool:
            results = pool.map(self._run_single_crawler, urls_split)

        all_results = [item for sublist in results for item in sublist]
        print("Crawling completed for all URLs.")
        return all_results

    @staticmethod
    def _run_single_crawler(ids_urls):
        crawler = BestbuySpider(ids_urls)
        return crawler.run()


def main():
    url_manager = URLManager()
    all_results = url_manager.run_crawlers()
    return all_results


if __name__ == "__main__":
    results = main()
