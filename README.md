# Crypto Portfolio Tracker
#### Video Demo:  https://www.youtube.com/watch?v=OSuU6lAm7bE
#### Description:
TODO

My cs50 project combines 2 of my favourite things. Blockchain technology & Comedy. I find the 2 worlds collide well in my project.

I decided to build a Crypto portfolio tracker that does the following functions:
- Allows users to register for an account
- Allows users to track their crypto purchases
- Allows users to track their crypto sells
- Tracks trasaction history
- Provides users with Live price charting (Integrated via Tradingview)
- Price data from Coingecko & Tradingview
- Comedic relief 


The tech stack that I used is as follows:
- HTML, CSS, Javascript
- Python & Flask
- SQLite 
- Bootstrap
- cs50 package
- Coingecko API
- Tradingview Integration

In-order for this to work, user must "pip install pycoingecko"

**Let's talk about the design**

I wanted to go for a simple look, so bootstrap was perfect for the job.

When starting up the site you will be prompted to register for an account. You will be asked for firstname, lastname, username, password, & password confirmation.
All this is handled by app.py and register.html, which then stores the information in my database (crypto.db) table name users.

Right after creating the account, users will be prompted to login and as they are loggin in, I hope the start to see the banter ;)
Logging in is again handled by app.py and the html for this page is login.html. app.py will cross reference the users table in crypto.db to see if the user exists and has entered the right username and password.

After signing in, the user can now see the main / portfolio page, where the user can track their portfolio but can also view educational + sattire videos hand picked by myself embeded on the site.

Users are then met with pages Price, Buy, Sell, History. Let's breakdown each.

**Price**:
The price page is where Tradingview's charting software is integrated directly on the site. Users can view live price of any asset and can even do technical analysis if they please.

This is all taken care of on price.html.

**Buy & Sell**:
Both of these pages are rather similiar, only they do different functions. One allows you to track any purchases you have made and the other tracks sells. You can see each page has it's own sort of banter as well as simple styling. Both buy and sell transactions are tracked in crypto_txs in crypto.db, a seperate table dedicated for transacitons. Portfolio is tracked using crypto_portfolio. I used seperate tables to make it easier to debug issues if they arise. One table seemed to have caused a lot of issues and headaches.

**History**:
History is where both buys and sells are listed, this helps user track their bad decisions, sorry, I mean transactions. Information from here is pulled straight from the crypto_txs database and is handled in app.py and history.html

That is pretty much it, I would explain the jokes but that doesn't make them funny does it? 

I really enjoyed cs50 and honestly felt emotional when watching the last lecture. It's been an honor and a journey. 

Thank you David Malan and cs50 team, it's been a ride.

This was cs50!

