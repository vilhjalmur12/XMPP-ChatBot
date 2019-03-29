import logging
import re

from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError, IqTimeout


class EchoBot(ClientXMPP):

    def __init__(self, jid, password):
        ClientXMPP.__init__(self, jid, password)

        # environment
        self.available_actions = {'turn-right', 'turn-left', 'direction'}
        self.current_leader = 'bot1@3.18.234.195'
        self.quorums = {f'bot1@3.18.234.195', f'bot2@3.18.234.195', f'bot3@3.18.234.195', f'bot4@3.18.234.195'}
        self.connected = set()

        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message)

        # If you wanted more functionality, here's how to register plugins:
        # self.register_plugin('xep_0030') # Service Discovery
        # self.register_plugin('xep_0199') # XMPP Ping

        # Here's how to access plugins once you've registered them:
        # self['xep_0030'].add_feature('echo_demo')

        # If you are working with an OpenFire server, you will
        # need to use a different SSL version:
        # import ssl
        # self.ssl_version = ssl.PROTOCOL_SSLv3

    def session_start(self, event):
        self.send_presence()
        self.get_roster()

        # Most get_*/set_* methods from plugins use Iq stanzas, which
        # can generate IqError and IqTimeout exceptions
        #
        # try:
        #     self.get_roster()
        # except IqError as err:
        #     logging.error('There was an error getting the roster')
        #     logging.error(err.iq['error']['condition'])
        #     self.disconnect()
        # except IqTimeout:
        #     logging.error('Server is taking too long to respond')
        #     self.disconnect()

    def message(self, msg):
        reciever = str(msg['from']).split('/')
        reciever = reciever[0]

        print(msg['body'])

        if 'newleader' in msg['body']:
            tmp = msg['body'].split()
            self.current_leader = tmp[1]
            return

        if reciever not in self.connected and reciever not in self.quorums:
            self.connected.add(reciever)
            self.send_message(mto=reciever, mbody='oh hi there!')

            welcome_string = f'=====   Welcome to the blind mans direction   =====\n\ndirection: tells you what direction you are facing\nturn-left: tells you what direction you are facing after turning left\nturn-right: tells you what direction you are facing after turning right\nquit: quit the game'
            self.send_message(mto=reciever, mbody=welcome_string)
            return

        if msg['body'] in self.available_actions:
            self.send_message(mto=self.current_leader, mbody=f'{msg["from"].bare} {msg["body"]}')
        elif reciever in self.quorums:
            #print(msg['body'])
            tmp = msg['body'].split()
            tmp = tmp[0]
            message = msg['body'].split(' ', 1)[1]
            self.send_message(mto=tmp, mbody=message)
        else:
            self.send_message(mto=msg['from'].bare, mbody="Not valid")


if __name__ == '__main__':

    xmpp = EchoBot('gateway@3.18.234.195', 'password')
    xmpp.connect()

    xmpp.process(block=True)