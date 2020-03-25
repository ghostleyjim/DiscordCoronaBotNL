DiscordCoronaBotNL

Discord bot created to scrape the RIVM (dutch healthcare institute) 
once a day (to prevent flooding) and collect the number of confirmed cases per municipality.

When user in discord writes !corona <municipality(gemeente)> the bot will respond
with number of confirmed cases..

The user can also use following commands;
!gemeentes: gives list of gemeentes via private chat in text file
!database: sends the database.txt to the user

To use the bot for yourself you need to create an account to get a secret key 
store this in your .env file. Also since it now uses pastebin to paste values you need to create and 
store your userkey in there 

https://pypi.org/project/pbwrap/ library explanation on keycreation and pastebin in python use
https://realpython.com/how-to-make-a-discord-bot-python/ has a nice description
on how-to set discord up.

--disclaimer--
It is still work in progress and this is my first python project so it might not be as nice and clean as it could be
comments will be added in the near future for clarification.

