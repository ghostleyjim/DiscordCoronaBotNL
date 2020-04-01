from datetime import datetime, timedelta
import csv

clock = datetime.now()

def casecalculator(locatie, tijd):
    tijd = int(tijd)
    deltamax = clock - timedelta(days=tijd)
    deltamin = clock - timedelta(days=(tijd + 1))

    with open("history.txt", 'r') as csv_file, open ('database.txt') as db, open('histbuf.txt', 'w') as buffer:
        #print(tijd)
        info = csv_file.read().split('\n')

        j = ''
        l = ''

        for i in info:
            try:
                time = datetime.strptime(i, '%Y-%m-%d %H:%M:%S.%f') #2020-03-31 00:38:24.541781
                print(time)
                if deltamin < time < deltamax:
                    print("true")
                    j = info.index(i) + 1
                    break
                else:
                    bericht = 'geen data'
                    return bericht
            except:
                pass





        for k in info[ j: ]:
            if k == 'end':
                l = info.index(k)

        history = '\n'.join(info[j:l])
        print(history, file=buffer, end='')

    with open('histbuf.txt', 'r') as buffer:
        past = (csv.reader(buffer, delimiter=';'))  # split the info in rows and collumns

        plaats = [ ]  # variable to store municipality
        besmettingen = [ ]  # variable to store the confirmed infected
        for row in past:  # for loop to check where info is stored
            gemeente = row[ 1 ]  # gemeente (municipality) stored on row 2 (array 1)
            aantal = row[ 2 ]  # number confirmed cases stored in row 3 (array 2)

            plaats.append(gemeente)  # add to plaats array
            besmettingen.append(aantal)  # add to confirmed cases array (string number)

        plaatsnaam = locatie.lower()  # municipality name send from !corona <municipality> message from user

        plaatsex = plaats.index(plaatsnaam)  # if name exists give array index location to variable plaatsex (yeah I know)
        hist_gevallen = besmettingen[ plaatsex ]  # take the confirmed case number from the same index location (arrays are stored the same because of CSV)

    with open('database.txt', 'r') as db:
        present = (csv.reader(db, delimiter=';'))  # split the info in rows and collumns

        plaats = [ ]  # variable to store municipality
        besmettingen = [ ]  # variable to store the confirmed infected
        for row in present:  # for loop to check where info is stored
            gemeente = row[ 1 ]  # gemeente (municipality) stored on row 2 (array 1)
            aantal = row[ 2 ]  # number confirmed cases stored in row 3 (array 2)

            plaats.append(gemeente)  # add to plaats array
            besmettingen.append(aantal)  # add to confirmed cases array (string number)


        plaatsex = plaats.index(plaatsnaam)  # if name exists give array index location to variable plaatsex (yeah I know)
        gevallen = besmettingen[ plaatsex ]  # take the confirmed case number from the same index location (arrays are stored the same because of CSV)


    verschil = int(gevallen) - int(hist_gevallen)


    return verschil