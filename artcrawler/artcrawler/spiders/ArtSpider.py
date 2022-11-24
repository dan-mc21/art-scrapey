import regex as re
import scrapy

class ArtSpider (scrapy.Spider):
    name = "arty"
    allowed_domains = ['bearspace.co.uk']
    page = 1
    start_urls = ["https://www.bearspace.co.uk/purchase"]
    
    def parse(self, response):
        load_more = response.xpath('//div/section[@aria-label="Product Gallery"]/div/button[contains(., "Load More")]').extract_first()
        #### auto increment pagination until load more button no longer present #####
        if load_more:
            self.page +=1
            next_page = f'{"https://www.bearspace.co.uk/purchase"}{"?page="}{self.page}'
            yield response.follow(next_page, callback=self.parse)
        else:
            for page in response.xpath('//div/ul[@class="S4WbK_ c2Zj9x"]/li/div/a/@href'):
                yield response.follow(page.get(),callback=self.parse_product)
    
    def parse_product(self,response):
        ######## get all product details and filter for media and price, if no match, none #####
        pattern = re.compile(r"^(?![0-9])(?!Artist:|Photo credit:|£|Edition|Image credit:|Set| | ).{10,70}.(?<!cm|CM)(?<![0-9])$")
        details = response.xpath('//section[@class="_2RbVQ"]/div//p[string-length(text()) > 0]/text()|//section[@class="_2RbVQ"]/div//p/span[string-length(text()) > 0]/text()').getall()
        try:
            descr = [i for i in details if pattern.match(i)][0]
        except IndexError as e:
            descr =  None
        
        dim_pat = re.compile(r"^.*(cm|CM|cms|\xa0diam\xa0|[0-9])$")
        try:
            dims = [i for i in details if dim_pat.match(i)][0]
            dim = re.findall(r"(\d{1,}[.,]?\d{1,}|[1-9]|.?diam)",dims)
            h = dim[0]
            w = dim[1]
            if "diam" in w:
                w = h
        except Exception as e:
            h = None
            w = None

        yield {
            "url" : response.request.url,
            "title" : response.xpath('//div[@class="_12vNY"]/section/div/h1/text()').get(),
            "media" : descr,
            "height_cm" : h,
            "width_cm" : w,
            "price_gbp": float(str(response.xpath('//div[@class="_26qxh"]/span/text()').get()[1:]).replace(',',''))
        }




        
