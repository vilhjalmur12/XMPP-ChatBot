#!/bin/bash

cert="~/.aws/ejabbered.pem"

ssh -o StrictHostKeyChecking=no -i "$cert" ubuntu@18.224.87.198 "rm -R bots/"
ssh -o StrictHostKeyChecking=no -i "$cert" ubuntu@18.224.87.198 "mkdir bots/"
ssh -o StrictHostKeyChecking=no -i "$cert" ubuntu@18.224.87.198 "virtualenv  bots/venv"

scp -i "$cert" ChatBot.py ubuntu@18.224.87.198:~/bots/bot1.py
scp -i "$cert" ChatBot.py ubuntu@18.224.87.198:~/bots/bot2.py
scp -i "$cert" ChatBot.py ubuntu@18.224.87.198:~/bots/bot3.py
scp -i "$cert" ChatBot.py ubuntu@18.224.87.198:~/bots/bot4.py

ssh -o StrictHostKeyChecking=no -i "$cert" ubuntu@18.224.87.198 "cd bots | source venv/bin/activate | pip3 install sleekxmpp"
ssh -o StrictHostKeyChecking=no -i "$cert" ubuntu@18.224.87.198 ""

scp -i "~/.aws/ejabbered.pem" ChatBot.py ubuntu@18.224.87.198:~/bots/bot1.py