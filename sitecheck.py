import requests
from bs4 import BeautifulSoup
import csv
import time
import ntplib

date_format = "%A %d %B %Y"
f = open('updatetime.txt', 'r')
old_time = f.readline()
old_time = old_time.rstrip('\n')
f.close()



with open('updatetime.txt', "r+") as timefile:
    ntp_client = ntplib.NTPClient()
    response = ntp_client.request('pool.ntp.org')
    current_time = time.strftime(date_format, time.localtime(response.tx_time))
    if current_time != old_time:
        print(current_time, file=timefile, end='')


        page = requests.get('https://www.rivm.nl/coronavirus-kaart-van-nederland-per-gemeente')
        print('accessing RIVM...')
        soup = BeautifulSoup(page.content, 'html.parser')

        results = soup.find(id="csvData")

        RIVM = results.get_text()

        RIVM = RIVM.lower()

        with open("database.txt", "w") as text_file:
            print(RIVM[1:], file=text_file, end='')

while True:
    with open('database.txt') as csv_file:
        csv_reader = (csv.reader(csv_file, delimiter=';'))

        plaats = []
        besmettingen = []
        for row in csv_reader:
            gemeente = row[1]
            aantal = row[2]

            plaats.append(gemeente)
            besmettingen.append(aantal)

        plaatsnaam = input('welke plaatsnaam?').lower()
        try:
            plaatsex = plaats.index(plaatsnaam)
            gevallen = besmettingen[plaatsex]
            print('aantal bekende besmettingen in', plaatsnaam, 'is: ', gevallen)
        except:
            print(plaatsnaam, 'plaats onbekend')
