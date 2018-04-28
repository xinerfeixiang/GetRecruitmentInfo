#-*- coding: utf-8 -*-
import re
import csv
import requests
from tqdm import tqdm
from urllib.parse import urlencode
from requests.exceptions import RequestException

def get_one_page(city, keyword, region, page):
    '''
    Get the content of HTNL
    '''
    paras = {
        'jl' : city,    #Get the city
        'kw' : keyword, #Get the keyword
        'isadv' : 0,    #Whether to open more detailed serch options
        'isfilter' : 1, #Whether the results are filtered
        'p' : page,     #The pages
        're' : region   #The Abbreviation of the region
        }

    headers = {
            'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding' : 'gzip, deflate, br',
            'Accept-Language' : 'zh-CN, zh;q=0.9',
            'Host' : 'sou.zhaopin.com',
            'Referer' : 'https://www.zhaopin.com',
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36'
            }

    url = 'https://sou.zhaopin.com/jobs/searchresult.ashx?' + urlencode(paras)
#    print (url)

    try:
        #Get the webpage content and HTML text
        response = requests.get(url, headers=headers)
        # Determine whether to succeed by state code
        if response.status_code == 200:
            return response.text
        return None
    except RequestException as e:
        return None

def parse_one_page(html):
    '''
    parms the html text to get useful information
    '''
    pattern = re.compile('<a style=.*? target="_blank">(.*?)</a>.*?'   #Get the job name
            '<td class="gsmc"><a href="(.*?)" target="_blank">(.*?)</a>.*?' #Get the website and name of the company
            '<td class="zwyx">(.*?)</td>', re.S) #Get the wage
    
    #Use regular expression to match information
    items = re.findall(pattern, html)

    for item in items:
        job_name = item[0]
        job_name = job_name.replace('<b>', '')
        job_name = job_name.replace('</b>', '')
        yield{
            'job' : job_name,
            'website' : item[1],
            'company' : item[2],
            'salary' : item[3]
            }

def write_csv_file(path, headers, rows):
    '''
    Write the headers and rows into file
    '''
    #add encoding to prevent writing errors in Chinese
    # nowline params prevent each line from writing one more empty line
    with open(path, 'a', encoding='gb18030', newline='') as f:
        f_csv = csv.DictWriter(f, headers)
        f_csv.writeheader()
        f_csv.writerows(rows)

def write_csv_headers(path, headers):
    '''
    write headers
    '''
    with open(path, 'a', encoding='gb18030', newline='')as f:
        f_csv = csv.DictWriter(f, headers)
        f_csv.writeheader()

def write_csv_rows(path, headers, rows):
    '''
    write rows
    '''
    with open(path, 'a', encoding='gb18030', newline='')as f:
        f_csv = csv.DictWriter(f, headers)
        f_csv.writerows(rows)

def main(city, keyword, region, page):
    '''
    main function
    '''
    filename = 'zl_' + city + '_' + keyword + '.csv'
    headers = ['job', 'website', 'company', 'salary']
    write_csv_headers(filename, headers)
    for i in tqdm(range(page)):
        '''
        get the Recruitment information of the page, then write in file
        '''
        jobs = []
        html = get_one_page(city, keyword, region, i)
        items = parse_one_page(html)
        for item in items:
            jobs.append(item)
            write_csv_rows(filename, headers, jobs)

if __name__ == '__main__':
    main('北京' ,'python工程师' , 2005 ,10)
