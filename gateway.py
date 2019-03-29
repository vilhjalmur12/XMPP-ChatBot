import logging

from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError, IqTimeout


class EchoBot(ClientXMPP):

    def __init__(self, jid, password):
        ClientXMPP.__init__(self, jid, password)

        # environment
        self.available_actions = {'turn-right', 'turn-left', 'direction'}
        self.current_leader = 'bot1@3.18.234.195'
        self.quorums = {f'bot1@3.18.234.195', f'bot2@3.18.234.195', f'bot3@3.18.234.195', f'bot4@3.18.234.195'}


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
        reciever = msg['from'].split('/')
        reciever = reciever[0]

        if msg['body'] in self.available_actions:
            self.send_message(mto=self.current_leader, mbody=msg['body'])
        elif reciever in self.quorums:
            tmp = msg['body'].split()
            tmp = tmp[0]
            self.send_message(mto=tmp, mbody=msg['body'])
        else:
            self.send_message(mto=msg['from'].bare, mbody="Not valid")

if __name__ == '__main__':

    xmpp = EchoBot('gateway@3.18.234.195', 'password')
    xmpp.connect()

    print("=====   Welcome to the blind mans direction   =====")
    print("There are several helpers to help you with the direction... ask them")

    print("==========   Actions  =========")
    print(" direction: tells you what direction you are facing")
    print(" turn-left: tells you what direction you are facing after turning left")
    print(" turn-right: tells you what direction you are facing after turning right")
    print(" quit: quit the game ")
    print("===================================")


    arg = ""

    while (arg != "quit"):
        print("hello")


    xmpp.process(block=True)