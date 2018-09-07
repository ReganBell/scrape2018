# -*- coding: utf-8 -*-
import scrapy
from scrapy.shell import inspect_response
import urllib
import json
import time
from collections import defaultdict
from datetime import datetime
import glob
import os
from utilities import fix_xml, latestJSON

class MyHarvardNavSpider(scrapy.Spider):
    name = 'myHarvardNav'
    searches = []

    def start_requests(self):
        url = 'https://courses.my.harvard.edu/psc/courses/EMPLOYEE/EMPL/s/WEBLIB_HU_SB.ISCRIPT1.FieldFormula.IScript_BuildSearchBrowser'
        yield scrapy.Request(url, callback=self.got_search_page, dont_filter=True)

    def got_search_page(self, response):
        data = json.loads(response.body)
        for school in data:
            for category in school['HU_SB_CFG_CT_VW']:
                for searchDict in category['HU_SB_CFG_SC_VW']:
                    search = searchDict['HU_SB_SRCH_DEFN']
                    if 'PARENT_NODE_NAME' not in search:
                        self.searches.append(search)                    

avgPagesPerRequest = 2

def timeLeftString(seconds):
    timeLeft = divmod(seconds / 60, 60)
    hours = timeLeft[0]
    minutes = timeLeft[1]
    seconds = (minutes - round(minutes, 0)) * 60

    comps = []

    def sIfPlural(number):
        return '' if round(number, 0) < 1.01 and round(number, 0) > 0.99 else 's'
    def addIfNotZero(number, label):
        if number >= 1:
            comps.append(("%.0f " % number) + label + sIfPlural(number))

    for interval, label in [(hours, 'hour'), (minutes, 'minute'), (seconds, 'second')]:
        addIfNotZero(interval, label)
    comps.append('remaining')

    return ' '.join(comps)

class MyHarvardSpider(scrapy.Spider):
    name = "myHarvard"
    safetyValve = {}
    searches = defaultdict(list)
    pageEstimate = 0
    pagesScraped = 0
    startTime = datetime.now()

    def start_requests(self):
        allSearches = latestJSON('my.harvard Nav')
        # allSearches = allSearches[3:5]
        self.pageEstimate = len(allSearches) * avgPagesPerRequest
        return [self.course_list_request(search, 1) for search in allSearches]

    def course_list_request(self, searchText, pageNumber):
        searchText = searchText.replace('General Education:', 'CRSE_ATTR_VALUE_HU_GE_ATTR:') 
        if pageNumber == 1:
            self.safetyValve[searchText] = 0
        dictionary = {
                      "PageNumber": pageNumber,
                      "PageSize": "",
                      "SortOrder":["IS_SCL_SUBJ_CAT"],
                      "Facets":[],
                      "Category": "HU_SCL_SCHEDULED_BRACKETED_COURSES",
                      "SearchPropertiesInResults": True,
                      "FacetsInResults": True,
                      "SaveRecent": False,
                      "TopN": "",
                      "SearchText": searchText
                      }
        body_string = 'SearchReqJSON=' + urllib.quote_plus(json.dumps(dictionary))
        return scrapy.Request('https://courses.my.harvard.edu/psc/courses/EMPLOYEE/EMPL/s/WEBLIB_IS_SCL.ISCRIPT1.FieldFormula.IScript_Search',
                             method='POST',
                             callback=self.got_courses_page,
                             body=body_string,
                             meta={'searchText': searchText},
                             headers={'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'}) 

    def got_courses_page(self, response):
        data = json.loads(response.body)
        searchProps = data[2]
        pageNumber = searchProps['PageNumber']
        totalPages = searchProps['TotalPages']
        searchText = searchProps['SearchText']

        if pageNumber == 1:
            self.pageEstimate -= avgPagesPerRequest
            self.pageEstimate += totalPages

        self.pagesScraped += 1
        delta = datetime.now() - self.startTime
        secondsLeft = (delta.total_seconds() / self.pagesScraped) * (self.pageEstimate - self.pagesScraped)
        print 'Scraped page', str(self.pagesScraped), 'of', str(self.pageEstimate) + ';', timeLeftString(secondsLeft)

        label = str(pageNumber), 'of', str(totalPages), searchText
        count = len(data[0]['ResultsCollection']) if 'ResultsCollection' in data[0] else -1
        self.searches[searchText].append({'label': label, 'data': data, 'count': count})

        if pageNumber != totalPages:
            if self.safetyValve[searchText] < totalPages:
                self.safetyValve[searchText] += 1
                yield self.course_list_request(searchText, pageNumber + 1)
            else:
                print "Safety valve exceeded", pageNumber, "of", totalPages, searchText


