from flask import Flask, render_template, request, session
import pandas as pd
import pickle
import re
from urllib.parse import unquote
from IPython.display import HTML
import subprocess
import os

from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pretty_html_table import build_table

def sendmail(body):
	message = MIMEMultipart()
	message['Subject'] = 'CrossLog: Warning IDS Alert'
	message['From'] = 'guptajalaj13@gmail.com'                          
	password = 'ipmbitsat'				       
	message['To'] = '19ucs232@lnmiit.ac.in'                          
	body_content = body
	message.attach(MIMEText(body_content, "html"))
	msg_body = message.as_string()
	server = SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(message['From'], password)
	server.sendmail(message['From'], message['To'], msg_body)
	server.quit()


Send_Email = 0

XSS = pickle.load(open('/home/ubuntu/CrossLog/Research Files/XSS.sav', 'rb'))
SQLi = pickle.load(open('/home/ubuntu/CrossLog/Research Files/SQLi.sav', 'rb'))
PT = pickle.load(open('/home/ubuntu/CrossLog/Research Files/PT.sav', 'rb'))
#OS = pickle.load(open('attacks/OS.sav', 'rb'))
CRLFi = pickle.load(open('/home/ubuntu/CrossLog/Research Files/CRLFi.sav', 'rb'))
SSI = pickle.load(open('/home/ubuntu/CrossLog/Research Files/SSI.sav', 'rb'))
LDAPi = pickle.load(open('/home/ubuntu/CrossLog/Research Files/LDAPi.sav', 'rb'))
XPath = pickle.load(open('/home/ubuntu/CrossLog/Research Files/XPath.sav', 'rb'))
#anomalous = pickle.load(open('attacks/anomalous.sav', 'rb'))

XSS_L = ['document', ';', '+', ')', 'div', 'var', '-', '<script', ']', '^', '#', '$', 'window', 'location', 'search', '<', '?', '|', '&', '[', '.', 'src', 'cookie', 'iframe', 'createelement', 'string.fromcharcode', 'img', '/', 'this', '<>', '\\\\', ',', '[]', '(', '}', 'onload', '&#', '%', '>', ':', '{', '==', 'eval()', 'onerror', '!', '_', '@', '=', '"', ' ', '*', 'href', 'http', '.js', "'"]
SQLi_L = ['admin', ',', '||', 'where', 'and', 'between', ';', ']', '^', '<', 'union', 'any', 'exec', '|', 'into', 'drop', '(', '=', 'like', '*', '%', 'not', 'from', 'count', '()', 'select', ' ', ')', 'commit', '>=', 'update', ':', 'replace', 'sleep', '&&', 'null', '-', '>', 'all', '+', '<=', '<>', 'xp', 'sp', 'delete', "'", 'or', 'insert', 'table', '/**/', '"', '.', 'user', '!=', '#', 'char', '[']
PT_L = [':', '.bat', '.conf', '//', 'system', 'exec', 'winnt', '\\\\.', '../', 'ini', '\\\\/', ':/', 'windows', '%00', '/', '..\\\\', 'passwd', 'log', ':\\\\', './', 'boot', 'etc', '..', 'file', 'access', ',,']
LDAPi_L = [';', '+', ')', 'name', 'cn=', 'objectclass', '=)', '<', '|', '&', '*)', ')(', '/', '\\\\', ')&', ',', '&(', '(', '=*', '>', '(|', '+)', '(&', 'sn=', '!', 'mail', '=', ' ', '*', '))', "'"]
XPath_L = ['`', 'path/', ',', '||', 'and', ';', ']', '^', '<', '|', '(', '=', 'comment', '*', '%', 'not', 'child', '()', 'count', ' ', ')', 'position()', '>=', '&&', '/*', '<--', '-', 'node()', '>', '+', '<=', 'name', '<>', 'text()', '//', '((', 'or', '::', 'user', '"', '.', '#', '[']
SSI_L = ['dir', 'fromhost', 'httpd', 'winnt\\\\', '<!-', 'replyto', '.bat', 'etc/', '.conf', '"', 'date_gmt', '"id', '+connect', '"mail', '+-l', '-->', 'email', 'windows', '/passwd', 'toaddress', 'access.log', 'var', '.com', '+id', '+', 'virtual', '#echo', 'bin/', 'sender', '#', 'cmd', '/mail', 'ls+', ':\\\\', 'message', '+statement', '#exec', 'home/', 'odbc', 'log/', 'system.ini', ',', '#include']
#OS_L = [';', ':\\\\', 'c:', 'bash', '.bat', 'shell', 'cmd', 'IP', 'passwd', '\\\\/', 'winnt', 'exec', 'script', 'www.', 'rm', 'ftp', '|', 'access', 'etc', '.', 'file', '-aux', ':/', '..', 'bin/', "'", 'wget', '..\\\\', '\\\\.', 'ping', 'echo', 'system32', '.exe', 'etc/passwd', '../', 'dir', 'log', './', 'tmp/', 'display', 'cat', 'root', ' ', 'telnet', 'http', 'uname', ':']
CRLFi_L = ['SET', '%0A', '%0D', '+', 'TAMPER', ':', '%0D%0A', 'COOKIE']
#Anomaly_L = ['FU', 'NA', 'FS', 'PL', 'RL', 'FD', 'NK', 'FL', 'AL']
Net_Features = ['dir', 'cmd', '#exec', '+id', 'string.fromcharcode', 'sn=', 'winnt', 'access.log', '%0D%0A', '+', '/', 'table', 'onerror', 'mail', '<!-', 'etc/passwd', '<', '-', '.bat', 'union', ']', '//', 'path/', 'sender', ':\\\\', 'node()', '+connect', '%', 'href', 'delete', '..\\\\', '#echo', '}', '!=', '=)', ':', '&', '+-l', 'position()', 'admin', ',', 'where', 'drop', 'insert', 'rm', 'ping', 'cookie', ' ', 'comment', '/mail', '"', 'and', 'objectclass', 'location', '{', '_', '()', 'createelement', '../', '<>', 'http', 'etc/', 'virtual', 'log', 'uname', '<script', '&(', '/*', '.com', 'boot', '))', '%00', 'fromhost', 'wget', 'access', 'winnt\\\\', 'any', ',,', 'update', 'home/', '||', '%0A', '+statement', '\\\\', '>', '(', 'www.', 'eval()', '.js', ':/', ')&', 'email', '|', 'child', 'div', '[]', 'log/', 'TAMPER', 'tmp/', '?', "'", ';', '.exe', '>=', 'like', 'IP', 'name', '-aux', 'windows', '"id', 'bin/', '::', 'date_gmt', '.', '\\\\/', '&&', '<--', 'SET', '&#', '/**/', '#', 'search', 'onload', 'into', '*', '<=', 'odbc', 'xp', 'ls+', 'var', 'all', 'img', '^', 'file', '-->', '=', 'etc', 'this', 'replace', 'c:', 'toaddress', '.conf', '*)', 'from', 'root', 'src', ')(', 'document', 'select', 'char', 'system', '((', ')', 'between', 'display', 'or', 'iframe', 'cat', 'cn=', 'replyto', 'system.ini', '!', 'message', 'window', 'exec', 'commit', 'echo', '$', 'passwd', 'user', 'system32', 'not', 'httpd', './', 'COOKIE', '"mail', '(&', 'count', '/passwd', 'telnet', '..', '`', 'text()', 'ftp', 'null', '=*', '@', 'sp', '+)', 'ini', '#include', 'shell', 'script', 'bash', '==', 'sleep', '\\\\.', '%0D', '[', '(|']


exp = r'^(\S+) (\S+) (\S+) \[([\w:/]+\s[+\-]\d{4})\] "(\S+)\s?(\S+)?\s?(\S+)?" (\d{3}|-) (\d+|-)\s?"?([^"]*)"?\s?"?([^"]*)?"?$'

#def XSS_check(url):
#  df_temp = pd.DataFrame(columns=XSS_L)
# df_temp.loc[0] = 0
#  url = unquote(url)
#  url = unquote(url)
 # url = url.replace('\n','')
  #url = url.replace(' ','')
  #url = url.lower()
  #for col in XSS_L:
   # if col in url:
    #  df_temp[col] = 1
  #return XSS.predict(df_temp)[0]

def SQLi_check(url):
  df_temp = pd.DataFrame(columns=SQLi_L)
  df_temp.loc[0] = 0
  url = unquote(url)
  url = unquote(url)
  url = url.replace('\n','')
  url = url.lower()
  for col in SQLi_L:
    if col in url:
      df_temp[col] = 1
  return SQLi.predict(df_temp)[0]

def PT_check(url):
  df_temp = pd.DataFrame(columns=PT_L)
  df_temp.loc[0] = 0
  url = unquote(url)
  url = unquote(url)
  url = unquote(url)
  url = unquote(url)  
  url = url.replace('\n','')
  url = url.lower()
  for col in PT_L:
    if col in url:
      df_temp[col] = 1
  return PT.predict(df_temp)[0]



def CRLFi_check(url):
  df_temp = pd.DataFrame(columns=CRLFi_L)
  df_temp.loc[0] = 0
  url = unquote(url)
  url = url.upper()
  for col in CRLFi_L:
    if col in url:
      df_temp[col] = 1
  return CRLFi.predict(df_temp)[0]

def SSI_check(url):
  df_temp = pd.DataFrame(columns=SSI_L)
  df_temp.loc[0] = 0
  url = unquote(url) 
  url = url.replace('\n','')
  url = url.replace(' ','+')
  url = url.lower()
  for col in SSI_L:
    if col in url:
      df_temp[col] = 1
  return SSI.predict(df_temp)[0]

def LDAPi_check(url):
  df_temp = pd.DataFrame(columns=LDAPi_L)
  df_temp.loc[0] = 0
  url = unquote(url) 
  url = url.replace('\n','')
  url = url.lower()
  for col in LDAPi_L:
    if col in url:
      df_temp[col] = 1
  return LDAPi.predict(df_temp)[0]

def XPath_check(url):
  df_temp = pd.DataFrame(columns=XPath_L)
  df_temp.loc[0] = 0
  url = unquote(url) 
  url = url.replace('\n','')
  url = url.lower()
  for col in XPath_L:
    if col in url:
      df_temp[col] = 1
  return XPath.predict(df_temp)[0]


app = Flask(__name__)

Attacks = []
Location = ""
Data = []
Position = 0

@app.route('/', methods=['POST','GET'])
def index():		
	return render_template('index.html')

@app.route("/log", methods=["GET","POST"])
def log():
  global Send_Email
  Send_Email = 0
  if request.method == 'POST':
    if 'log_file' in request.files:
      log = request.files['log_file'].read()
      txt = str(log,'utf8')
      lines = txt.splitlines()
      data = []
      for l in lines:
        z = re.match(exp, l)
        #if XSS_check(z[6]):
         # x = 'XSS'
        if SQLi_check(z[6]):
          x = 'SQLi'
        elif PT_check(z[6]):
          x = 'PT'
       # elif OS_check(z[6]):
        #  x = 'OS'
        elif CRLFi_check(z[6]):
          x = 'CRLFi'
        elif SSI_check(z[6]):
          x = 'SSI'
        elif LDAPi_check(z[6]):
          x = 'LDAPi'
        elif XPath_check(z[6]):
          x = 'XPath'
        #elif Anomaly_check(z[6]):
         # x = 'Anomaly'
        else:
          x = 'Normal'
        data.append([z[1],z[4],z[5],z[6],z[8],x])

      df = pd.DataFrame(data, columns=['IP Address', 'Timestamp', 'Method','Request Vector','Response Code','Type'])
      return render_template('log.html', value1=df.to_html(table_id="example"))
  return render_template('log.html')



@app.route("/test", methods=["GET","POST"])
def test():
  global Send_Email
  Send_Email = 0
  global Attacks
  if request.method == 'POST':
    if 'test_query' in request.form:
      if XSS_check(request.form['test_query']):
        x = 'Cross Site Scripting'
      elif SQLi_check(request.form['test_query']):
        x = 'SQL Injection'
      elif PT_check(request.form['test_query']):
        x = 'Path Traversal Attack'
     # elif OS_check(request.form['test_query']):
      #  x = 'OS Commandline Injection'
      elif CRLFi_check(request.form['test_query']):
        x = 'CRLF Injection'
      elif SSI_check(request.form['test_query']):
        x = 'SSI'
      elif LDAPi_check(request.form['test_query']):
        x = 'LDAP Injection'
      elif XPath_check(request.form['test_query']):     
        x = 'XPath Injection'
      #elif Anomaly_check(request.form['test_query']):
       # x = 'Anomaly'
      else:
        x = 'Normal'
      if [x, request.form['test_query']] not in Attacks:
        Attacks = [[x, request.form['test_query']]] + Attacks
      return render_template('test.html', Attacks=Attacks)
  return render_template('test.html')



if __name__ == '__main__':
	app.run(debug=True)
