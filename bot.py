# bot.py

import csv  # RIVM uses CSV
import os  # for dotenv
import time  # time control to only contact website once

import discord  # discord library
import ntplib  # time from ntp server
import requests  # URL request
from bs4 import BeautifulSoup  # scrape the website info
from dotenv import load_dotenv  # dotenv to store bot secret

PIC = ''  # person in control
current_datetime = ''
filedate = ''


def RIVMdata(locatie):
    global filedate  # used for adding to .txt database
    global current_datetime

    plaats = []  # array for storing municipality info

    hour_format = "%H"  # format time to stare in updatefile.txt
    day_format = '%d'  # string format only store day
    date_small = '%d%m'  # format time for filedate
    month_format = '%B'  # string format store complete month
    datetime_format = '%d %B %Y %H:%M:%S'  # string format to store datetime for log
    f = open('updatetime.txt', 'r')  # open the file to check the string
    old_time = f.readline()  # store in var
    old_time = old_time.rstrip('\n')  # make sure \n is stripped before comparison
    old_day = f.readline()
    old_day = old_day.rstrip('\n')
    old_month = f.readline()
    old_month = old_month.rstrip('\n')
    f.close()  # close the file again

    update_datetime = old_day + ' ' + old_month + ' ' + old_time + ' uur'  # update message string to chatroom

    ntp_client = ntplib.NTPClient()  # check timeserver
    response = ntp_client.request('pool.ntp.org')  # store variable from timeserver

    current_hour = time.strftime(hour_format, time.localtime(response.tx_time))  # var for current hour (string)
    current_datetime = time.strftime(datetime_format, time.localtime(response.tx_time))  # used for logfile
    daynumber = time.strftime(day_format, time.localtime(
        response.tx_time))  # used for comparing if file has been updated in last 24 hrs
    month = time.strftime(month_format,
                          time.localtime(response.tx_time))  # used to store month used in update message to chatroom
    filedate = time.strftime(date_small, time.localtime(response.tx_time))  # format received string for filedate

    with open('updatetime.txt', "r+") as timefile:  # open updatetime.txt with read + write
        # compare and check if 6 hours has passed or complete day convert strings to int to do math
        if int(old_time) - int(current_hour) >= 6 or int(old_time) - int(current_hour) <= -6 or int(daynumber) != int(
                old_day):
            print(current_hour + '\n' + daynumber + '\n' + month, file=timefile,
                  end='')  # if yes store the new time and date in the txt file

            page = requests.get(
                'https://www.rivm.nl/coronavirus-kaart-van-nederland-per-gemeente')  # request data from RIVM
            print('accessing RIVM...')  # logging print
            soup = BeautifulSoup(page.content, 'html.parser')  # parse the content

            results = soup.find(id="csvData")  # find the id csvdata and store all data

            RIVM = results.get_text()  # get all the text from the data

            RIVM = RIVM.lower()  # store all data in lowercase easy to find

            with open("database.txt", "w") as text_file:  # write all data to txt file database.txt
                print(RIVM[1:], file=text_file,
                      end='')  # print the data in the txt !!end is important to prevent empty lines

            with open('database.txt') as csv_file:  # open the file as a csv
                csv_reader = (csv.reader(csv_file, delimiter=';'))  # split the info in rows and collumns

                for row in csv_reader:  # for loop to only take out info needed
                    gemeente = row[1]  # taking out all info with name of municipals

                    plaats.append(gemeente)  # add them to the array plaats

            with open('gemeentelijst.txt', 'w') as text_file:  # store all in txt file so users can request from bot
                gemeentes = ''  # variable to create string
                for i in range(len(plaats)):  # for loop to put all info in text file with newlines (easy reading)
                    gemeentes = plaats[i] + '\n'  # adding the \n to all
                print(gemeentes, file=text_file)  # print all info to the text file

    while True:  # while loop to extract info from csv with !corona
        with open(
                'database.txt') as csv_file:  # database file open as csv same as above but now with case information as well
            csv_reader = (csv.reader(csv_file, delimiter=';'))  # split the info in rows and collumns

            plaats = []  # variable to store municipality
            besmettingen = []  # variable to store the confirmed infected
            for row in csv_reader:  # for loop to check where info is stored
                gemeente = row[1]  # gemeente (municipality) stored on row 2 (array 1)
                aantal = row[2]  # number confirmed cases stored in row 3 (array 2)

                plaats.append(gemeente)  # add to plaats array
                besmettingen.append(aantal)  # add to confirmed cases array (string number)

        plaatsnaam = locatie.lower()  # municipality name send from !corona <municipality> message from user
        try:  # try to find the name
            plaatsex = plaats.index(
                plaatsnaam)  # if name exists give array index location to variable plaatsex (yeah I know)
            gevallen = besmettingen[
                plaatsex]  # take the confirmed case number from the same index location (arrays are stored the same because of CSV)
            bericht = 'aantal bekende besmettingen in ' + plaatsnaam + ' is: ' + gevallen \
                      + '\n' + "updated: " + update_datetime  # create message to send back to chatroom
            return (bericht)  # return message to send function


        except:  # if name is not in array
            bericht = plaatsnaam + ' onbekend'  # message = municipality + not found
            return (bericht)  # return message to send function


load_dotenv()  # load the secret from the .env file
TOKEN = os.getenv('DISCORD_TOKEN')  # variable token stores the secret

client = discord.Client()  # variable to store client info


@client.event
async def on_ready():  # if script connects to Discord
    print(f'{client.user.name} has connected to Discord!')  # show I am connected with username


@client.event
async def on_message(message):  # if I reveive a message
    global PIC  # global person in command
    global filedate  # global to append filedate to database file

    if message.author == client.user:  # if message is from myself
        return  # ignore and return

    incoming = message.content.lower()  # if message incomming store in var incoming
    author = message.author

    if incoming.startswith('!corona'):  # if that message starts with !corona
        locatie = incoming[8:]  # store the rest of the message (beginning from index 8 to skip space)
        if locatie:  # did I receive a location (municipality)
            # print (locatie)                                              #could be used for debugging
            bericht = RIVMdata(locatie)  # send to function RIVMdata to check if I have info and return in var bericht
            with open('log.txt', 'a') as log_file:  # log request in log.txt
                logwriter = csv.writer(log_file, delimiter=';', quotechar='"') #how should the csv be stored
                logwriter.writerow([current_datetime, str(author), locatie])  # write row for csv
            await message.channel.send(bericht)  # send the data in var bericht

        else:  # no info for location?
            await message.channel.send('Error commando is: !corona <gemeente>')  # send error message

    elif (message.content == '!gemeentes'):  # if command !gemeente is given
        PIC = message.author  # store who asked for it
        with open('gemeentelijst.txt', 'rb') as fp:  # open the file gemeentelijst.txt
            await PIC.send(file=discord.File(fp,
                                             'gemeente.txt'))  # format it as a discord file with name gemeente.txt and send to person who asked private
    elif (message.content == '!database'):  # if command !database is given
        PIC = message.author  # store who asked for it
        with open('database.txt', 'rb') as fp:  # open database file
            await PIC.send(file=discord.File(fp,
                                             'database' + filedate + '.txt'))  # send file same way as above but also append the date of the file for reference


client.run(TOKEN)  # run the client and login with secret
