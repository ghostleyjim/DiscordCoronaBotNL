# bot.py

import new_cases

import csv  # RIVM uses CSV
import os  # for dotenv
from dotenv import load_dotenv  # dotenv to store bot secret

import discord  # discord library

from datetime import datetime

import requests  # URL request
from bs4 import BeautifulSoup  # scrape the website info
from pbwrap import Pastebin

updateTime = None

with open('updatetime.txt', 'r') as tm:
    i = tm.read()
    updateTime = datetime.strptime(i, '%Y-%m-%d %H:%M:%S.%f')


PIC = ''  # person in control
current_datetime = ''
filedate = ''

clock = datetime.now()

load_dotenv()  # load the secret from the .env file
TOKEN = os.getenv('DISCORD_TOKEN')  # variable token stores the secret
PASTEAPI = os.getenv('PASTEBIN_TOKEN')
PASTEUSERKEY = os.getenv('PASTEBIN_USERKEY')
client = discord.Client()  # variable to store client info

pastebin = Pastebin(PASTEAPI)


def RIVMdata(locatie, tijd):
    global filedate  # used for adding to .txt database
    global current_datetime

    if locatie == 'database':
        with open('database.txt', 'r') as database:
            RIVM = database.read()
            pasteurl = pastebin.create_paste(RIVM, api_paste_private=0, api_paste_name=None, api_paste_expire_date='10M', api_paste_format='text')  # print all info to the text file
            return pasteurl

    if locatie == 'gemeentelijst':

        with open('database.txt', 'r') as csv_file:  # open the file as a csv
            csv_reader = (csv.reader(csv_file, delimiter=';'))  # split the info in rows and collumns
            plaats = [ ]
            for row in csv_reader:  # for loop to only take out info needed
                gemeente = row[ 1 ]  # taking out all info with name of municipals

                plaats.append(gemeente)  # add them to the array plaats
        gemeentelijst = '\n'.join(plaats)
        pasteurl = pastebin.create_paste(gemeentelijst, api_paste_private=0, api_paste_name=None, api_paste_expire_date='10M', api_paste_format='text')  # print all info to the text file
        return pasteurl

    while True:  # while loop to extract info from csv with !corona

        update_datetime = datetime.strftime(updateTime, '%d %B %H:%M')  # update message
        # string to chatroom

        with open('database.txt') as csv_file:  # database file open as csv same as above but now with case information as well
            csv_reader = (csv.reader(csv_file, delimiter=';'))  # split the info in rows and collumns

            plaats = [ ]  # variable to store municipality
            besmettingen = [ ]  # variable to store the confirmed infected
            for row in csv_reader:  # for loop to check where info is stored
                gemeente = row[ 1 ]  # gemeente (municipality) stored on row 2 (array 1)
                aantal = row[ 2 ]  # number confirmed cases stored in row 3 (array 2)

                plaats.append(gemeente)  # add to plaats array
                besmettingen.append(aantal)  # add to confirmed cases array (string number)

        plaatsnaam = locatie.lower()  # municipality name send from !corona <municipality> message from user
        try:  # try to find the name
            plaatsex = plaats.index(plaatsnaam)  # if name exists give array index location to variable plaatsex (yeah I know)
            gevallen = besmettingen[ plaatsex ]  # take the confirmed case number from the same index location (arrays are stored the same because of CSV)
            if tijd != None:

                geschiedenis = new_cases.casecalculator(plaatsnaam, tijd)

                bericht = 'aantal bekende besmettingen in ' + plaatsnaam + ' is: ' + gevallen + '\n' + f'verschil met {tijd} dag(en): ' + str(geschiedenis) + '\n' + "updated: " + update_datetime
                return bericht
            else:
                bericht = 'aantal COVID-19 patienten in ziekenhuis in ' + plaatsnaam + ' is: ' + gevallen + '\n' + "updated: " + update_datetime  # create message to send back to chatroom
                return (bericht)  # return message to send function


        except:  # if name is not in array
            bericht = plaatsnaam + ' onbekend'  # message = municipality + not found
            return (bericht)  # return message to send function


@client.event
async def on_ready():  # if script connects to Discord
    print(f'{client.user.name} has connected to Discord!')  # show I am connected with username


@client.event
async def on_message(message):  # if I reveive a message
    global PIC  # global person in command
    global filedate  # global to append filedate to database file
    global updateTime

    if clock.day != updateTime.day:
        updateDatabase()
        updateTime = clock

    if message.author == client.user:  # if message is from myself
        return  # ignore and return

    incoming = message.content.lower()  # if message incomming store in var incoming
    author = message.author

    if incoming.startswith('!corona'):  # if that message starts with !corona
        commando = incoming.split()
        locatie = commando[ 1 ]  # store the rest of the message (beginning from index 8 to skip space)

        if len(commando) == 3:
            geschiedenis = commando[ 2 ]
        else:
            geschiedenis = None

        #print(commando)

        if locatie:  # did I receive a location (municipality)
            # print (locatie)                                              #could be used for debugging
            bericht = RIVMdata(locatie, geschiedenis)  # send to function RIVMdata to check if I have info and return in var bericht
            with open('log.txt', 'a') as log_file:  # log request in log.txt
                logwriter = csv.writer(log_file, delimiter=';', quotechar='"')  # how should the csv be stored
                logwriter.writerow([ current_datetime, str(author), locatie ])  # write row for csv
            await message.channel.send(bericht)  # send the data in var bericht

        else:  # no info for location?
            await message.channel.send('Error commando is: !corona <gemeente>')  # send error message

    elif (message.content == '!gemeentes'):  # if command !gemeente is given
        bericht = RIVMdata('gemeentelijst')
        await message.channel.send(bericht)

    elif (message.content == '!database'):  # if command !database is given
        bericht = RIVMdata('database')
        await message.channel.send(bericht)


def updateDatabase():

    with open('history.txt', 'a') as writer, open('database.txt', 'r') as reader:
        database_copy = reader.read()
        print(clock, file=writer)
        writer.write(database_copy + "\n")
        print("end", file=writer, end = '')

    page = requests.get('https://www.rivm.nl/coronavirus-kaart-van-nederland-per-gemeente')  # request data from RIVM
    print('accessing RIVM...')  # logging print
    soup = BeautifulSoup(page.content, 'html.parser')  # parse the content

    results = soup.find(id="csvData")  # find the id csvdata and store all data

    RIVM = results.get_text()  # get all the text from the data
    RIVM = RIVM.lower()  # store all data in lowercase easy to find

    RIVM = RIVM.split("\n")

    for i in RIVM:
        if i == '':
            x = RIVM.index(i)
            del RIVM[ x ]

    RIVM = "\n".join(RIVM)

    with open("database.txt", "w") as text_file:  # write all data to txt file database.txt
        print(RIVM, file=text_file, end='')

    with open('updatetime.txt', 'w') as dtm:
        print(clock, file=dtm, end= '')

client.run(TOKEN)  # run the client and login with secret

