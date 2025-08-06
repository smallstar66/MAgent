# scrapy crawl caixin -O caixin_data.jso
import scrapy
import re

class CaixinSpider(scrapy.Spider):
    name = "caixin"
    allowed_domains = ["caixin.com"]
    start_urls = ["https://www.caixin.com/finance/"]
    seen_urls = set()

    def parse(self, response):
        # 抓取所有可能的文章链接
        links = response.css("a::attr(href)").getall()

        # 筛选文章链接（根据 URL 结构）
        article_links = [
            link for link in links
            if re.match(r"^https?://.*caixin\.com/\d{4}-\d{2}-\d{2}/.*\.html", link)
        ]
        article_links = list(set(article_links))

        for link in article_links:
            if link not in self.seen_urls:
                self.seen_urls.add(link)
                yield scrapy.Request(url=link, callback=self.parse_detail)

    def parse_detail(self, response):
        self.logger.info(f"正在解析文章页: {response.url}")

        title = response.css("div#conTit h1::text").get(default="").strip()

        # 用精确 XPath 提取发布时间
        pub_date = response.xpath("//*[@id='artInfo']/text()").getall()[3].strip()
        # if pub_date:
        #     pub_date = pub_date.strip()
        print(f'提取到的时间:{pub_date}')
        # 提取正文内容
        paragraphs = response.css("div#Main_Content_Val p::text").getall()
        body = "\n".join([p.strip() for p in paragraphs if p.strip()])

        yield {
            "title": title,
            "pub_date": pub_date,
            "body": body,
            "url": response.url,
        }

'''
class CaixinSpider(scrapy.Spider):
    name = "caixin1"
    allowed_domains = ["caixin.com"]
    start_urls = ["https://www.caixin.com/finance/"]
    seen_urls = set()  # 全局变量用于去重

    def parse(self, response):
        links = response.css("a::attr(href)").getall()
        article_links = [
            link for link in links
            if re.match(r"^https?://.*caixin\.com/\d{4}-\d{2}-\d{2}/.*\.html", link)
        ]
        article_links = list(set(article_links))

        for link in article_links:
            if link not in self.seen_urls:
                self.seen_urls.add(link)
                yield scrapy.Request(url=link, callback=self.parse_detail)

    def parse_detail(self, response):
        title = response.css("h1::text").get(default="").strip()
        pub_date = response.css("span.time::text").get(default="").strip()
        body = " ".join(p.strip() for p in response.css("div.txt_con p::text").getall())

        yield {
            "title": title,
            "pub_date": pub_date,
            "body": body,
            "url": response.url,
        }
'''