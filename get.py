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
from ssl import SSLError

filename = 'cookie'
cookie = cookielib.MozillaCookieJar(filename)
if os.path.exists(filename):
  cookie.load(filename, ignore_discard=True, ignore_expires=True)
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
htmlParser = HTMLParser.HTMLParser()

def login():
  print 'please login'
  username = raw_input('username:');
  password = getpass.getpass('password:');

  postdata = urllib.urlencode({
             'nextpage': 'http://community.topcoder.com/stat?c=problem_solution&cr=10574855&rd=16554&pm=13986',
             'module': 'Login',
             'username': username,
             'password': password
             })
  loginUrl = 'https://community.topcoder.com/tc';
  getpage(loginUrl, postdata)
  cookie.save(ignore_discard=True, ignore_expires=True)

def getpage(url, postData = None):
  print 'send request', url 
  while True:
    try:
      request = opener.open(url, postData, 10)
      ret = request.read()
    except Exception as e:
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

# return html
def getData(problemUrl):
  html = getpage(problemUrl);
  ref = re.findall(r'(/tc\?module=ProblemDetail[^"]*)"', html);
  assert len(ref) > 0
  statusUrl = 'http://community.topcoder.com' + ref[0];

  html = getpage(statusUrl);
  ref = re.findall(r'<a href="([^"]*)" class="statText">view</a>', html);
  assert len(ref) > 0
  dataUrl = 'http://community.topcoder.com' + ref[-1].replace('&amp;', '&');
  firstIn = True;
  while True:
    html = getpage(dataUrl);
    if re.search('<!-- System Testing -->', html): return html
    if firstIn: firstIn = False; 
    else: print 'Is username or password wrong?';
    login();

def output(data, layout):
  # mangle
  mangle_prefix = ['#' + i + ''.join(random.sample(string.lowercase, 13)) + '#' for i in string.uppercase]
  for c in string.uppercase:
    layout = layout.replace(c, mangle_prefix[ord(c) - ord('A')])

  def getLabel(i, j):
    return mangle_prefix[i] + '.' * j
  
  def checkTypeStr(s):
    if len(s) == 0: return False;
    s = s[0];
    return isinstance(s, str) or isinstance(s, unicode);

  for i, s in enumerate(data):
    if isinstance(s, list) and checkTypeStr(s):
      layout = layout.replace(getLabel(i, 2), str(len(s[0])));
  for i, s in enumerate(data):
    if isinstance(s, list):
      layout = layout.replace(getLabel(i, 1), str(len(s)));
  for i, s in enumerate(data):
    if isinstance(s, list):
      layout = layout.replace(getLabel(i, 0), 
          ('\n' if checkTypeStr(s) else ' ').join(map(str, s)));
    else:
      layout = layout.replace(getLabel(i, 0), str(s));
  return layout

def generateData(html):
  data = re.findall(r'<TD (?:BACKGROUND="/i/steel_blue_bg.gif" )?CLASS="statText" ALIGN="(?:left|right)">([^<]*)</TD>', html)
  assert len(data) % 3 == 0

  def pretty(s):
    s = htmlParser.unescape(s)
    s = '[' + s.replace('\n', '').replace('{', '[').replace('}', ']') + ']';
    return json.loads(s);
  dataIn = map(pretty, data[::3]);
  dataOut = map(pretty, data[1::3]);
    
  number_of_data = len(dataIn)

  layoutIn = read_from_file('layout.in')
  layoutOut = read_from_file('layout.out')
  
  name = raw_input('file name:');
  group = input('group size:');

  if os.path.exists(name) == False: os.mkdir(name);
  for i in xrange(0, number_of_data, group):
    filenameIn = '%s/%d.in' % (name, i / group + 1)
    filenameOut = '%s/%d.out' % (name, i / group + 1)
    contentIn, contentOut = "", ""
    
    if group > 1: contentIn += str(min(number_of_data - i, group)) + '\n'

    for j in xrange(i, min(number_of_data, i + group)) :
      contentIn += output(dataIn[j], layoutIn)
      contentOut += output(dataOut[j], layoutOut)
    write_to_file(filenameIn, contentIn)
    write_to_file(filenameOut, contentOut)

if __name__ == "__main__":
  problemUrl = raw_input('problem url:');
  dataHtml = getData(problemUrl);
  write_to_file('data.html', dataHtml)
  dataHtml = read_from_file('data.html')
  generateData(dataHtml);

