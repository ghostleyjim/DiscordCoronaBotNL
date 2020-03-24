# bot.py

import requests
from bs4 import BeautifulSoup
import csv
import time
import ntplib

import os

import discord
from dotenv import load_dotenv

PIC = ''


def RIVMdata(locatie):
    global plaatsflag
    global PIC
    global filetime
    plaats = []

    date_format = "%A %d %B %Y"
    date_small = '%d%m'
    f = open('updatetime.txt', 'r')
    old_time = f.readline()
    old_time = old_time.rstrip('\n')
    f.close()

    with open('updatetime.txt', "r+") as timefile:

        ntp_client = ntplib.NTPClient()
        response = ntp_client.request('pool.ntp.org')
        current_time = time.strftime(date_format, time.localtime(response.tx_time))
        filetime = time.strftime(date_small, time.localtime(response.tx_time))



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

            with open('database.txt') as csv_file:
                csv_reader = (csv.reader(csv_file, delimiter=';'))

                for row in csv_reader:
                    gemeente = row[1]

                    plaats.append(gemeente)

            with open('gemeentelijst.txt', 'w') as text_file:
                gemeentes = ''
                for i in range(len(plaats)):
                    gemeentes = plaats[i] + '\n'
                print(gemeentes, file=text_file)




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

        plaatsnaam = locatie.lower()
        try:
            plaatsex = plaats.index(plaatsnaam)
            gevallen = besmettingen[plaatsex]
            bericht = 'aantal bekende besmettingen in ' + plaatsnaam + ' is: ' + gevallen
            return(bericht)


        except:
            bericht = plaatsnaam + ' onbekend'
            plaatsflag = False
            PIC = ''
            return(bericht)



load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')


@client.event
async def on_message(message):
    global plaatsflag
    global PIC
    global filetime

    if message.author == client.user:
        return

    incoming = message.content.lower()
    if (incoming.startswith('!corona')):
        PIC = message.author
        locatie = incoming[8:]
        if locatie:
            #print (locatie)
            bericht = RIVMdata(locatie)
            await message.channel.send(bericht)

        else:
            await message.channel.send('Error commando is: !corona <gemeente>')

    elif (message.content == '!gemeentes'):
        PIC = message.author
        with open('gemeentelijst.txt', 'rb') as fp:
            await PIC.send(file=discord.File(fp, 'gemeente.txt'))
    elif (message.content == '!database'):
        PIC = message.author
        with open('database.txt', 'rb') as fp:
            await PIC.send(file=discord.File(fp, 'database' + filetime + '.txt'))

client.run(TOKEN)

