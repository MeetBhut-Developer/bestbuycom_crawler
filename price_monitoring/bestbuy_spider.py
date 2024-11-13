import asyncio
import re
import aiohttp  # type: ignore
from multiprocessing import Pool, cpu_count
from scrapy.http import HtmlResponse

class BestbuySpider:
    def __init__(self, urls):
        self.urls = urls
        self.cookies = {
            'intl_splash': 'false',
            'locDestZip':'96939',
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

    def start_end_finder(self, data, start, end):
        r = re.findall(re.escape(start) + "(.+?)" + re.escape(end), data, re.DOTALL)
        return r[0] if r else None

    async def crawl_data(self, session, url):
        try:
            async with session.get(url, headers=self.headers, cookies=self.cookies) as response:
                content = await response.text()
                print("Status:", response.status)
                xpath=HtmlResponse(url='',body=content,encoding='utf-8')
                product_name=xpath.xpath('//h1/text()').get('').strip()
                description=self.start_end_finder(content, 'plainText', '"}').replace('\\','').lstrip('":"').strip()
                price=xpath.xpath('//*[@data-testid="customer-price"]/span/text()').get('').replace(',','').replace('$','').strip()
                print(price)
                discount=self.start_end_finder(content, 'priceChangeTotalSavingsAmount":', ',"').strip()
                print('discount:',discount)
                pickup=xpath.xpath('//*[contains(text()," Selected")]/../div//button[1]/@aria-label').get('').strip()
                if 'Unavailable' in pickup:availability='No'
                else:availability='Yes'
                review_star=xpath.xpath('//h2[contains(text(),"Reviews")]/../div//span[contains(@class,"overall-rating")]/text()[2]').get('').strip()
                if not review_star:
                    review_star=xpath.xpath('//span[@class="ugc-c-review-average font-weight-medium order-1"]/text()').get('').strip()
                review_count=xpath.xpath('//div[@class="review-count"]/text()').get('').strip()
                if not review_count:
                    review_count=xpath.xpath('//span[@class="c-reviews order-2"]/text()').get('').split(' ')[0].replace('(','').strip()
                print(url)
                print('review_star:',review_star,'---','review_count:',review_count)
                print('availability:',availability)
                print('***'*10)



                # return print(raw_desc)
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    async def crawl_urls(self):
        async with aiohttp.ClientSession() as session:
            tasks = [self.crawl_data(session, url) for url in self.urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

    def run(self):
        return asyncio.run(self.crawl_urls())


class URLManager:
    """Get urls and manage crawling using CPU cores"""
    def __init__(self, urls):
        self.urls = urls
        self.num_cores = cpu_count()

    def split_urls(self):
        return [self.urls[i::self.num_cores] for i in range(self.num_cores)]

    def run_crawlers(self):
        urls_split = self.split_urls()
        
        with Pool(self.num_cores) as pool:
            results = pool.map(self._run_single_crawler, urls_split)
        
        all_results = [item for sublist in results for item in sublist]
        print("Crawling completed for all URLs.")
        return all_results

    @staticmethod
    def _run_single_crawler(urls):
        """Helper"""
        crawler = BestbuySpider(urls)
        return crawler.run()


def main():
    # List of URLs to crawl
    urls = [
        "https://www.bestbuy.com/site/samsung-75-class-du6950-series-crystal-uhd-4k-smart-tizen-tv-2024/6594898.p?skuId=6594898",
        "https://www.bestbuy.com/site/lg-65-class-g4-series-oled-evo-4k-uhd-smart-webos-tv-2024/6578150.p?skuId=6578150",
        "https://www.bestbuy.com/site/tcl-55-class-q5-series-4k-uhd-hdr-pro-qled-smart-fire-tv-2024/6593218.p?skuId=6593218",
        "https://www.bestbuy.com/site/lg-65-class-ut70-series-led-4k-uhd-smart-webos-tv-2024/6593578.p?skuId=6593578",
        "https://www.bestbuy.com/site/samsung-65-class-s90c-oled-4k-uhd-smart-tizen-tv-2023/6536964.p?skuId=6536964",
        "https://www.bestbuy.com/site/samsung-50-class-du6900-series-crystal-uhd-4k-smart-tizen-tv-2024/6584869.p?skuId=6584869",
        "https://www.bestbuy.com/site/hisense-85-class-qd6-series-qled-4k-uhd-smart-google-tv-2024/6594982.p?skuId=6594982",
        "https://www.bestbuy.com/site/insignia-65-class-f30-series-led-4k-uhd-smart-fire-tv/6492966.p?skuId=6492966",
        "https://www.bestbuy.com/site/sony-75-class-bravia-xr-x90l-led-4k-uhd-smart-google-tv-2023/6544735.p?skuId=6544735",
        "https://www.bestbuy.com/site/lg-43-class-ut70-series-led-4k-uhd-smart-webos-tv-2024/6593577.p?skuId=6593577",
        "https://www.bestbuy.com/site/samsung-55-class-ls03d-the-frame-series-qled-4k-with-anti-reflection-and-slim-fit-wall-mount-included-2024/6576585.p?skuId=6576585",
        "https://www.bestbuy.com/site/toshiba-43-class-c350-series-led-4k-uhd-smart-fire-tv/6532119.p?skuId=6532119",
        "https://www.bestbuy.com/site/samsung-85-class-qn85d-series-neo-qled-4k-smart-tizen-tv-2024/6576433.p?skuId=6576433",
        "https://www.bestbuy.com/site/insignia-42-class-f20-series-led-full-hd-smart-fire-tv/6495088.p?skuId=6495088",
        "https://www.bestbuy.com/site/samsung-55-class-du6900-series-crystal-uhd-4k-smart-tizen-tv-2024/6593856.p?skuId=6593856",
        "https://www.bestbuy.com/site/sony-65-class-bravia-8-oled-4k-uhd-smart-google-tv-2024/6578577.p?skuId=6578577",
    ]

    # start crawling process
    url_manager = URLManager(urls)
    all_results = url_manager.run_crawlers()
    return all_results


if __name__ == "__main__":
    results = main()
