#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import cookielib
import getpass
import HTMLParser
import json
import os
import random
import re
import string
import urllib  
import urllib2  
import thread
import Queue

filename = 'cookie'
cookie = cookielib.MozillaCookieJar(filename)
if os.path.exists(filename):
  cookie.load(filename, ignore_discard=True, ignore_expires=True)
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
htmlParser = HTMLParser.HTMLParser()

def login():
  print 'login first'
  username = raw_input('username:');
  password = getpass.getpass('password:');

  postdata = urllib.urlencode({
             'nextpage': 'http://community.topcoder.com/tc',
             'module': 'Login',
             'username': username,
             'password': password
             })
  getpage('/tc', postdata)
  cookie.save(ignore_discard=True, ignore_expires=True)

def getpage(url, postData = None):
  url = htmlParser.unescape(url)
  print 'request: ', url 
  url = 'https://community.topcoder.com' + url
  while True:
    try:
      request = opener.open(url, postData, 10)
      ret = request.read()
    except:
      print 'request timeout (10s), send another one'
      continue
    return ret;

def read_from_file(file):
  h = open(file)
  content = h.read()
  h.close()
  return content

def write_to_file(file, content):
  h = open(file, 'w')
  h.write(content)
  h.close()

# page type: (url, prefix)
def crawl_contest(page):
  def crawl(html, prefix, builder):
    if (len(builder) == 0):
      pass
    else:
      next_pages = builder[0](html, prefix)
      next_pages = map(lambda x: (x[0], prefix + [x[1]]), next_pages)
      for page in next_pages:
        crawl(getpage(page[0]), page[1], builder[1:])


  chatser = string.digits + string.letters + ' '
  def validate_filename(name, postfix):
    return filter(lambda x: x in chatser, name).replace(' ', '_') + '.' + postfix

  def strip_html(html):
    ret = re.search(r'<!-- BEGIN BODY -->([\S\s]*?)<!-- END BODY -->', html)
    return ret.group(1).replace('BGCOLOR="#001B35"', '') if ret else html

  def builder_overview(html, prefix):
    return re.findall(r'<A HREF="(/stat\?c=problem_statement&pm=\d+&rd=\d+)" class="statText">(.*?)</A>', html)

  def builder_problem(html, prefix):
    write_to_file(validate_filename('Problem Statement ' + prefix[-1], 'html'), strip_html(html))
    return re.findall(r'<a href="(/tc\?module=ProblemDetail&rd=\d+&pm=\d+)">(.*?)</a>', html)

  def builder_detail(html, prefix):
    sols = re.findall(r'<a href="(/stat\?c=problem_solution&amp;cr=\d+&amp;rd=\d+&amp;pm=\d+)" class="statText">view</a>', html)
    return [(sols[-1], 'solution')] if len(sols) else []

  def builder_solution(html, prefix):
    write_to_file(validate_filename(prefix[-2] + ' ' + prefix[-3], 'html'), strip_html(html))
    return []

  crawl(getpage(page[0]), [page[1]], [builder_overview, builder_problem, builder_detail, builder_solution])

if __name__ == '__main__':
  page_overview = getpage('/stat?c=round_overview');
  all_contests = re.findall(r'<OPTION value="(/stat\?c=round_overview&er=\d+&rd=\d+)">(.*?)</OPTION>', page_overview)
  crawl_contest(all_contests[0])
