#!/usr/bin/python3.5
# By: Volker Strobel, improved by Patrick Hofmann and Timo Korthals
from bs4 import BeautifulSoup
from urllib.request import Request, build_opener, HTTPCookieProcessor
from urllib.parse import urlencode
import browser_cookie3
import re, time, sys, urllib

def get_num_results(search_term, start_date, end_date):
    """
    Helper method, sends HTTP request and returns response payload.
    """

    # Open website and read html
    # Get the user agent of your browser: https://www.whatismybrowser.com/detect/what-is-my-user-agent
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
    query_params = { 'q' : search_term, 'as_ylo' : start_date, 'as_yhi' : end_date}
    # Build the request: "as_sdt=1 : exclude patents", "as_vis=1 : exclude citations"
    url = "https://scholar.google.com/scholar?as_vis=1&hl=en&as_sdt=1,5&" + urllib.parse.urlencode(query_params)
    cookie_jar = browser_cookie3.chrome() # or firefox()
    opener = build_opener(HTTPCookieProcessor(cookie_jar))
    request = Request(url=url, headers={'User-Agent': user_agent})

    try:
        handler = opener.open(request)

        html = handler.read()

        # Create soup for parsing HTML and extracting the relevant information
        soup = BeautifulSoup(html, 'html.parser')
        div_results = soup.find("div", {"id": "gs_ab_md"}) # find line 'About x results (y sec)

        if div_results != None:

            res = re.findall(r'(\d+).?(\d+)?.?(\d+)?\s', div_results.text) # extract number of search results

            if res == []:
                num_results = '0'
                success = True
            else:
                num_results = ''.join(res[0]) # convert string to numbe
                success = True
        else:
            success = False
            num_results = '-1'
    except IOError as err:
        print("********************************************************************************")
        print("IO error: {0}".format(err))
        print("********************************************************************************")
        success = False
        num_results = '-1'

    return num_results, success

def get_range(search_term, start_date, end_date):

    fp = open("out.csv", 'w')
    fp.write("year,results\n")
    print("year,results")

    for date in range(start_date, end_date + 1):

        num_results, success = get_num_results(search_term, date, date)
        while not(success):
            print("It seems that you made to many requests to Google Scholar. Take action by visiting the site!", flush=True)
            value = str(input("repeat/continue/quit [r/c/q]: "))
            if value[0].lower() == 'r':
                num_results, success = get_num_results(search_term, date, date)
            elif value[0].lower() == 'c':
                break
            elif value[0].lower() == 'q':
                exit(-1)
            else:
                print("Choose correct value")
        year_results = "{0},{1}".format(date, num_results)
        print(year_results)
        fp.write(year_results + '\n')
        time.sleep(0.4)

    fp.close()

if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("******")
        print("Academic word relevance")
        print("******")
        print("")
        print("Usage: python extract_occurences.py '<search term>' <start date> <end date>")

    else:
        search_term = sys.argv[1]
        start_date = int(sys.argv[2])
        end_date = int(sys.argv[3])
        html = get_range(search_term, start_date, end_date)
