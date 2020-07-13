from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
from ftplib import FTP
import os

#################################################################
##
##    Script to get the current crypto prices and
##    generate the html for widget for Perry's website
##    because it would have no content otherwise ;-)
##    Shane Frost 
##    12 Jul 2020
##
#################################################################

## Start by reading the configuration file. It's best to have variables in the config file as it makes maintenance MUCH easier.
dirname = os.path.dirname(__file__)
ct = open(dirname + '\\config.txt','r')
configText = ct.read()
configData = json.loads(configText)

## Then get the html / css values so we can use them later on.
ct = open(dirname + '\\' + configData['files']['tophtmltemplate'] ,'r')
htmlHead = ct.read()
ct = open(dirname + '\\' + configData['files']['bottomhtml'] ,'r')
htmlFoot = ct.read()



##    This is where you define the currencies you want to have are. You can add or remove currencies by adding or removing them from the array.
##    The array is coin name, coin id
curr = [['bitcoin','ethereum'],[1,1027]]
slugs = ''

for x in curr[0]: # Transform the names in the array to a CSV string so that the API will accept them.
    if len(slugs) == 0:
        slugs = x
    else:
        slugs = slugs + ',' + x 
    
url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
parameters = {
  'slug':slugs,
  'aux':'market_cap_by_total_supply'
}
headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': configData['API']['API_KEY']
}

# Begin the API Session   
session = Session()
session.headers.update(headers)

try:
    htmlOut = htmlHead
    response = session.get(url, params=parameters)
    data = json.loads(response.text)
    for k in data['data']:
        #print(data['data'][k]['quote']['USD']['percent_change_24h'])
        htmlOut = htmlOut + '<p>' + data['data'][k]['symbol'] + ': ' + str(data['data'][k]['quote'])[2:5] + '$' + str(data['data'][k]['quote']['USD']['price']) + ' '
        if data['data'][k]['quote']['USD']['percent_change_24h'] > 0:
            htmlOut = htmlOut + '<span class="up">   +' + str(data['data'][k]['quote']['USD']['percent_change_24h']) + '%</span></p>'
        else:
            htmlOut = htmlOut + '<span class="dn">   -' + str(data['data'][k]['quote']['USD']['percent_change_24h']) + '%</h1></p>'

        print(data['data'][k]['symbol'] + ': ' + str(data['data'][k]['quote'])[2:5] + '$' + str(data['data'][k]['quote']['USD']['price']))
    htmlOut = htmlOut + htmlFoot
    f = open(dirname + '\\' + configData['ftp']['file'] ,'w')
    f.write(htmlOut)
    f.close()

    # Now upload the file to the server via ftp
    ftp = FTP(configData['ftp']['address'])
    ftp.login(configData['ftp']['username'],configData['ftp']['password'] )
    file = configData['ftp']['file']
    
    ftp.storbinary('STOR ' + file, open(dirname + '\\' + file, 'rb'))
    
except (ConnectionError, Timeout, TooManyRedirects) as e:
    print(e)







