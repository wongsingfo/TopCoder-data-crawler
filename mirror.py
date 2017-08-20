#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import cookielib
import getpass
import HTMLParser
import json
import os
import Queue
import random
import re
import string
import sys
import threading
import time
import urllib  
import urllib2

filename = 'cookie'
cookie = cookielib.MozillaCookieJar(filename)
if os.path.exists(filename):
  cookie.load(filename, ignore_discard=True, ignore_expires=True)
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
htmlParser = HTMLParser.HTMLParser()

loginLock = threading.Lock()
infoLock = threading.Lock()

def info(type, *msg):
  infoLock.acquire()
  print '#' + type + ':\t' + ' '.join(map(str, msg))
  infoLock.release()

def login():
  if loginLock.locked():
    loginLock.acquire()
    loginLock.release()
  else :
    loginLock.acquire()
    print 'In order to continue, you must provide your user name and password.'
    infoLock.acquire()
    username = raw_input('username:');
    password = getpass.getpass('password:');
    infoLock.release()

    postdata = urllib.urlencode({
               'nextpage': 'http://community.topcoder.com/tc',
               'module': 'Login',
               'username': username,
               'password': password
               })
    getpage('/tc', postdata)
    cookie.save(ignore_discard=True, ignore_expires=True)
    loginLock.release()

def getpage(adr, postData = None):
  adr = htmlParser.unescape(adr)
  info('request', adr)
  url = 'https://community.topcoder.com' + adr
  while True:
    try:
      request = opener.open(url, postData, 10)
      ret = request.read()
      if re.search('<div class="errorText">In order to continue, you must provide your user name and password.</div>', ret):
        login()
        info('request', adr, '(retry after login)')
        continue
    except:
      info('error', sys.exc_info()[0])
      info('request', adr, '(retry)')
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
  def validate_name(name):
    return filter(lambda x: x in chatser, name).replace(' ', '_')
  def validate_filename(name, postfix):
    return folder + '/' + validate_name(name) + '.' + postfix

  def strip_html(html):
    ret = re.search(r'<!-- BEGIN BODY -->([\S\s]*?)<!-- END BODY -->', html)
    return ret.group(1).replace('BGCOLOR="#001B35"', '') if ret else html

  def builder_overview(html, prefix):
    return re.findall(r'<A HREF="(/stat\?c=problem_statement&pm=\d+&rd=\d+)" class="statText">(.*?)</A>', html)

  def builder_problem(html, prefix):
    overview_json['problem'].append(prefix)
    write_to_file(validate_filename('Problem Statement ' + prefix[-1], 'html'), strip_html(html))
    return re.findall(r'<a href="(/tc\?module=ProblemDetail&rd=\d+&pm=\d+)">(.*?)</a>', html)

  def builder_detail(html, prefix):
    sols = re.findall(r'<a href="(/stat\?c=problem_solution&amp;cr=\d+&amp;rd=\d+&amp;pm=\d+)" class="statText">view</a>', html)
    return [(sols[-1], 'solution')] if len(sols) else []

  def builder_solution(html, prefix):
    overview_json['solution'].append(prefix)
    write_to_file(validate_filename(prefix[-2] + ' ' + prefix[-3], 'html'), strip_html(html))
    return []

  folder = validate_name(page[1])
  info('begin', folder)
  if os.path.exists(folder):
    if os.path.exists(folder + '/overview.json'): 
      info('end', folder, '(already exists)')
      return
  else:
    os.mkdir(folder)

  overview_json = {}
  overview_json['begin'] = str(time.ctime(time.time()))
  overview_json['problem'] = []
  overview_json['solution'] = []
  crawl(getpage(page[0]), [page[1]], [builder_overview, builder_problem, builder_detail, builder_solution])

  overview_json['end'] = str(time.ctime(time.time()))
  write_to_file(validate_filename('overview', 'json'), 
    json.dumps(overview_json, sort_keys=True, indent=4, separators=(',', ': ')))
  info('end', folder)

queueLock = threading.Lock()
workQueue = Queue.Queue()

class Worker(threading.Thread):
  def run(self):
    while True:
      queueLock.acquire()
      if workQueue.empty():
        queueLock.release()
        return
      else:
        contestPage = workQueue.get()
        queueLock.release()
        crawl_contest(contestPage)
        workQueue.task_done()


if __name__ == '__main__':
  page_overview = getpage('/stat?c=round_overview');
  all_contests = re.findall(r'<OPTION value="(/stat\?c=round_overview&er=\d+&rd=\d+)">(.*?)</OPTION>', page_overview)
  for contest in all_contests: workQueue.put(contest)
  workers = [Worker() for i in range(5)]
  for worker in workers: worker.start()
  workQueue.join()
  print 'DONE :) '
