# -*- coding: utf-8 -*-
import scrapy
from scrapy.shell import inspect_response
import urllib
import json
import time
from scrapy.http.cookies import CookieJar
import datetime
import os
from utilities import fix_xml, latestJSON

fall = '1'
spring = '2'
terms = [fall]
years = ['2016']
# Uncomment below to scrape everything
terms = [fall, spring]
years = ['2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016']

class DepartmentSpider(scrapy.Spider):
	name = "QDepartments"
	base = 'https://webapps.fas.harvard.edu/course_evaluation_reports/fas/list?'
	departments = latestJSON('Q Departments')
	cookie = {}

	def __init__(self, cookie):
		self.cookie = cookie

	def start_requests(self):
		requests = []
		for term in terms:
			for year in years:
				if year + '_' + term in self.departments:
					continue
				else:
					request = scrapy.Request(self.base + 'yearterm=' + year + '_' + term, cookies=self.cookie, callback=self.got_term)
					request.meta['term'] = term
					request.meta['year'] = year
					requests.append(request)
		return requests    	

	def got_term(self, response):
		abbreviations = response.xpath('//span[@class="course-block-title"]/@title_abbrev').extract()
		self.departments[response.meta['year'] + '_' + response.meta['term']] = abbreviations		

class CourseIdSpider(scrapy.Spider):
	name = "courseIds"
	safetyValve = {}
	base = 'https://webapps.fas.harvard.edu/course_evaluation_reports/fas/'
	departments = {}
	courseIds = latestJSON('Q Course Ids')
	origins = {}	
	cookie = {}

	def __init__(self, cookie):
		self.cookie = cookie

	def start_requests(self):
		requests = []
		deptNamesDict = latestJSON('Q Departments')
		for term in terms:
			for year in years:
				if year + '_' + term in self.courseIds:
					continue
				else:
					for dept in deptNamesDict[year + '_' + term]:
						request = scrapy.Request(self.base + 'guide_dept?dept=' + dept + '&term=' + term + '&year=' + year, callback=self.got_ids, cookies=self.cookie)
						request.meta['dept'] = dept
						request.meta['term'] = term
						request.meta['year'] = year
						self.courseIds[year + '_' + term] = {dept: []}
						requests.append(request)
		return requests

	def got_ids(self, response):
		response = fix_xml(response)
		ids = [link.replace('course_summary.html?course_id=', '') for link in response.xpath('//li[@class="course"]/a/@href').extract()]
		term = response.meta['term']
		year = response.meta['year']
		dept = response.meta['dept']    		
		self.courseIds[year + '_' + term][dept] = ids

class ReportSpider(scrapy.Spider):
	name = "QReports"
	base = 'https://webapps.fas.harvard.edu/course_evaluation_reports/fas/'
	failedIds = {}
	records = {}
	coursesToScrape = 0
	coursesScraped = 0
	cookie = {}

	def __init__(self, cookie):
		self.cookie = cookie	

	def request(self, url, callback, courseId):
		request = scrapy.Request(self.base + url, callback=callback, cookies=self.cookie)
		request.meta['courseId'] = courseId
		return request

	def start_requests(self):
		requests = []
		courseIdsDict = latestJSON('Q Course Ids')
		for term in terms:
			for year in years:
				for dept, ids in courseIdsDict[year + '_' + term].iteritems():
					for courseId in ids:
						requests.append(self.request('course_summary.html?course_id=' + courseId, self.got_course, courseId))
						self.coursesToScrape += 1
		# requests = requests[0:20]
		return requests

	def error(self, string, response):
		self.failedIds[response.meta['courseId']] = string

	def scrapeResponses(self, response):
		responses = {}
		graphTables = response.xpath('//table[@class="graphReport"]')
		for index in [0, 1, 2]:
			if index >= len(graphTables): 
				break
			table = graphTables[index]
			names = table.xpath('.//strong/text()').extract()
			values = table.xpath('.//div/img/@alt').extract()
			respondents = table.xpath('.//td[3]/text()').extract()
			if len(names) != len(respondents):
				self.error('Response table: len(names) != len(respondents)', response)
				return
			if len(names) != len(values):
				newNames = []
				for name, count in zip(names, respondents):
					if count != '0':
						newNames.append(name)
				names = newNames
			for name, value in zip(names, values):
				responses[name] = value
		return responses

	def got_comments(self, response):
		comments = [c.strip() for c in response.xpath('//div[@class = "response"]/p/text()').extract()]
		courseId = response.meta['courseId']
		self.records[courseId]['comments'] = comments
		self.coursesScraped += 1
		print 'Scraped', self.coursesScraped, 'of', self.coursesToScrape

	def got_course(self, response):
		course = {}
		courseId = response.meta['courseId']
		titleList = response.xpath('//h1/text()').extract()
		if len(titleList) == 0:
			self.error("Title was empty", response)
			return
		course['summaryStats'] = response.xpath('//div[@id = "summaryStats"]/text()').extract()
		course['title'] = titleList[0]
		course['responses'] = self.scrapeResponses(response)
		if len(response.xpath('//table')) > 0:
			course['enrollmentReasons'] = response.xpath('//table')[-1].xpath('.//img/@alt').extract()
		else:
			self.error('Missing tables', response)
		facultyRequest = self.request('inst-tf_summary.html?course_id=' + courseId, self.got_faculty_initial, courseId)
		commentRequest = self.request('view_comments.html?course_id=' + courseId + '&qid=1487&sect_num=', self.got_comments, courseId)
		self.records[courseId] = course
		return [commentRequest, facultyRequest]

	def got_faculty_initial(self, response):
		self.got_faculty(response)
		profLinks = response.xpath('//ul[@class = "instructorSelect"]//option/@value').extract()
		requests = []
		if len(profLinks) > 1:
			for link in profLinks[1:]:
				prefix = 'inst-tf_summary.html?current_instructor_or_tf_huid_param='
				suffix = '&course_id=' + response.meta['courseId'] + '&current_tab=2&benchmark_type=Division&benchmark_range=single_term&sect_num='
				requests.append(self.request(prefix + link + suffix, self.got_faculty, response.meta['courseId']))
		return requests

	def got_faculty(self, response):
		courseId = response.meta['courseId']
		nameList = response.xpath('//h3[@class = "instructor"]/text()').extract()
		if len(nameList) == 0:
			self.error("Error getting instructor", response)
		else:
			entry = {nameList[0]: self.scrapeResponses(response)}
			if 'faculty' in self.records[courseId]:
				self.records[courseId]['faculty'].append(entry)
			else:
				self.records[courseId]['faculty'] = [entry]	 