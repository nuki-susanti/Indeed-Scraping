import scrapy
from urllib.parse import urlencode


class IndeedScraper(scrapy.Spider):
    name = "indeed_scraper"

    def get_url(self, keyword, location, offset=0):
        parameters = {
            "q": keyword,
            "l": location,
            "filter": 0,
            "start": offset
        }
        return "https://de.indeed.com/jobs?" + urlencode(parameters)

    def start_requests(self):
        keyword_list = ["data analyst"]
        location_list = ["deutschland"]

        for keyword in keyword_list:
            for location in location_list:
                indeed_url = self.get_url(keyword, location)

                yield scrapy.Request(url=indeed_url, callback=self.parse_front, meta={'keyword': keyword, 'location': location, 'offset': 0})

    def parse_front(self, response):

        links = response.xpath(
            '//div[@id="mosaic-provider-jobcards"]//td[@class="resultContent"]/div/h2/a/@href')
        links_to_follow = links.extract()

        for url in links_to_follow:
            url_to_follow = "https://de.indeed.com" + url
            yield response.follow(url=url_to_follow, callback=self.parse_page)

        # Paginate Through Jobs Pages
        next_page = response.xpath('//a[@aria-label="Next Page"]/@href').get()

        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(url=next_page_url, callback=self.parse_front)

    def parse_page(self, response):

        job_title_ext = response.xpath('//h1/span[@role="text"]/text()').extract_first()

        company_name_ext = response.xpath('//div[@data-company-name="true"]/a/text()').extract_first()

        location_ext = response.xpath('//*[contains(@class,"jobsearch-JobInfoHeader-subtitle")]/div[2]/div[1]/text()').extract_first()

        status_ext = response.xpath('//*[@id="salaryInfoAndJobType"]/span/text()').extract_first()
        
        description = response.xpath('//div[@id="jobDescriptionText"]//descendant::*/text()')
        description_ext = description.extract()
        desc = ''.join(x.strip() for x in description_ext)

        yield {
            'title': job_title_ext,
            'company': company_name_ext,
            'location': location_ext,
            'status': status_ext,
            'jobdesc': desc
        }
