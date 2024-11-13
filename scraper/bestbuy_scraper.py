import asyncio
import aiohttp
from scrapy.http import HtmlResponse

class BestbuyScraper:

    def __init__(self) -> None:
        self.input_url = input('Enter bestbuy.com Product URL: ')
        self.input_zipcode = input('Enter US Zipcode (If blank then default zipcode 96939):')
        
        if not self.input_zipcode:
            self.input_zipcode=96939

        self.cookies = {
            'intl_splash': 'false',
            'locDestZip': str(self.input_zipcode),
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

    async def spider(self):
        try:
            # Use aiohttp for async requests
            async with aiohttp.ClientSession() as session:
                async with session.get(self.input_url, headers=self.headers, cookies=self.cookies) as response:
                    content = await response.text()
                    print("Status:", response.status)
                    xpath=HtmlResponse(url='',body=content,encoding='utf-8')
                    product_name=xpath.xpath('//h1/text()').get('').strip()
                    pickup=xpath.xpath('//*[contains(text()," Selected")]/../div//button[1]/@aria-label').get('').strip()
                    shipping=xpath.xpath('//*[contains(text()," Selected")]/../div//button[2]/@aria-label').get('').strip()
                    
                    return print({"product name":product_name,"pickup":pickup,"shipping":shipping})
        except Exception as e:
            print(f"Error fetching {self.input_url}: {e}")
            return None

if __name__ == '__main__':
    crawl = BestbuyScraper()
    
    asyncio.run(crawl.spider())

    # print(data)
