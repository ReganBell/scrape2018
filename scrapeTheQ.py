from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from spiders.QSpiders import DepartmentSpider, CourseIdSpider, ReportSpider
from scrapy.utils.project import get_project_settings
from Parsing.cookie import parseCookie
import sys

if len(sys.argv) != 2:
	print 'Must provide cookieString as command line argument'
cookie = parseCookie(sys.argv[1])

runner = CrawlerRunner(get_project_settings())

@defer.inlineCallbacks
def crawl():
    yield runner.crawl(DepartmentSpider, cookie)
    yield runner.crawl(CourseIdSpider, cookie)
    yield runner.crawl(ReportSpider, cookie)
    reactor.stop()

crawl()
reactor.run()