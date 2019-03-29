# Chat bot MUC
Ejabber server runs on an AWS instance at 3.18.234.195.

## Requirements
The bots are written in python so the requirements are:
* python 3.6
* pip3
* sleekxmpp library

Assuming you are using a UNIX distro (linux/OSX), below installations in terminal should do

#### Install python

#####OSX
`brew install python3`

#####Linux
`sudo apt install python3`

#### Install pip

#####OSX
`brew install pip3`

#####Linux
`sudo apt install python3-pip`

#### Install sleekxmpp

#####OSX & Linux
`pip3 install sleekxmpp`

## How to run

Use terminal to navigate to the root directory

run the following in terminal

`
python3 ChatBot.py bot1@3.18.234.195 password botroom@conference.3.18.234.195 bot1
`

This will only start the leader bot or bot1. To start more bots open up more terminals, navigate to root and execute
same command except increment the bot numbers. F.x. replace the X in the command below with 2, 3, 4 etc.

`
python3 ChatBot.py botX@3.18.234.195 password botroom@conference.3.18.234.195 botX
`

To get started with a client open what ever client you like to use and log in with the credentials below
`
Username: arnor@3.18.234.195
password: password
`

add `bot1@3.18.234.195` to your contacts and try to chat. He will tell you what commands to use.

### Simulating server down

To simulate a leader down simply quit the process of bot1 in your terminal with ctrl + c. Bot 1 shuts down and the next
bot available takes over. Try talking to any other bot you created, they will either tell you who's the leader or keep 
going as the previous leader.




