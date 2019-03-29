import sys
import logging
import getpass
from optparse import OptionParser
import time
from statistics import mode

import sleekxmpp

# Python versions before 3.0 do not use UTF-8 encoding
# by default. To ensure that Unicode is handled properly
# throughout SleekXMPP, we will set the default encoding
# ourselves to UTF-8.
#
#if sys.version_info < (3, 0):
#    reload(sys)
#    sys.setdefaultencoding('utf8')
#else:
raw_input = input


class MUCBot(sleekxmpp.ClientXMPP):

    def __init__(self, jid, password, room, nick, leader):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        self.jid = jid
        self.room = room
        self.nick = nick
        self.incoming_log = False
        self.domain = "3.18.234.195"
        self.bot_room = "botroom@conference.3.18.234.195"
        self.requester = ""
        self.current_leader = 'bot1@3.18.234.195'
        self.ballad_votes = []
        self.server_count = 4
        self.leader = leader
        self.processess = {}
        self.n = 1
        self.process_n = 1
        self.quorums = [ f'bot1@3.18.234.195', f'bot2@3.18.234.195', f'bot3@3.18.234.195', f'bot4@3.18.234.195' ]
        self.active_quorums = [ f'bot1@3.18.234.195', f'bot2@3.18.234.195', f'bot3@3.18.234.195', f'bot4@3.18.234.195' ]

        # game environment
        self.direction = 'north'
        self.available_actions = {'turn-right', 'turn-left'}

        # The session_start event will be triggered when
        # the bot establishes its connection with the server
        # and the XML streams are ready for use. We want to
        # listen for this event so that we we can initialize
        # our roster.
        self.add_event_handler("session_start", self.start)

        # The groupchat_message event is triggered whenever a message
        # stanza is received from any chat room. If you also also
        # register a handler for the 'message' event, MUC messages
        # will be processed by both handlers.
        self.add_event_handler("groupchat_message", self.muc_message)

        # The groupchat_presence event is triggered whenever a
        # presence stanza is received from any chat room, including
        # any presences you send yourself. To limit event handling
        # to a single room, use the events muc::room@server::presence,
        # muc::room@server::got_online, or muc::room@server::got_offline.
        self.add_event_handler("muc::%s::got_online" % self.room,
                               self.muc_online)


        self.add_event_handler("muc::%s::got_offline" % self.room,
                               self.muc_offline)

        self.add_event_handler("message" , self.reccieve_message)


    def start(self, event):

        self.get_roster()
        self.send_presence()
        self.plugin['xep_0045'].joinMUC(self.room,
                                        self.nick,
                                        # If a room password is needed, use:
                                        # password=the_room_password,
                                        wait=True)


    def log(self, command, sender):
        """Do some logging"""
        # TODO: breyta þessu i lampart eða vector clocks
        timestamp = time.time()
        user = sender.user
        domain = sender.domain

        whole_string = f"{self.n}\t{str(timestamp)}\t{user}\t{domain}\t{command}\n"

        with open(f"{self.jid}_log.log", 'a') as f:
            f.write(whole_string)

    def reccieve_message(self, msg):

        if msg['from'].bare != self.bot_room:
            #print('Command inbound: ', msg['body'])

            spltCommand = msg['body'].split()

            self.log(msg['body'], msg['from'])

            if not spltCommand:
                return

            self.splitAndCommand(spltCommand, msg['from'])


    def splitAndCommand(self, command, sender):

        headCommand = command[0]

        if headCommand == "log":
            self.send_message(mto=sender.bare,
                              mbody=self.getLogString())

        if self.leader:
            # TODO: Remove the sleep
            time.sleep(1)

            if (len(self.active_quorums) - len(self.quorums)) >= len(self.quorums):
                self.send_message(mto=sender.bare, mbody="monk")
                return

            if headCommand == "direction":
                self.send_message(mto=sender.bare, mbody=self.direction)
                return

            # TODO: tests
            if headCommand == "servercount":
                self.send_message(mto=sender.bare, mbody=str(len(self.active_quorums)))
                return


            if headCommand == "promise":
                print(command)
                if (len(self.active_quorums) - 1 == len(self.ballad_votes)):
                    # here we process the verifying votes
                    self.ballad_votes.append(command[2])

                    # the votes chosen
                    vote = mode(self.ballad_votes)

                    self.send_message(mto=self.bot_room,
                                      mbody=f'accept {self.n} {self.jid} {vote}',
                                      mtype='groupchat')
                    self.ballad_votes = []
                    self.ballad_votes.append(self.own_vote)
                else:
                    self.ballad_votes.append(command[2])

            elif headCommand == "accepted":
                if (len(self.active_quorums) - 1 <= len(self.ballad_votes)):
                    # here the last voting
                    self.ballad_votes.append(command[3])

                    vote = mode(self.ballad_votes)

                    # send to gateway
                    self.send_message(mto=self.requester,
                                    mbody=f"{self.requester} you are facing {vote} sent from: {self.jid}")

                    self.ballad_votes = []
                    self.requester = ""
                    del self.processess[self.n]
                    self.n += 1
                    if self.processess:
                        self.requester = self.processess[self.n]['sender']
                        self.sendRequest(self.requester)
                else:
                    self.ballad_votes.append(command[3])
            else:
                if command[0] not in self.available_actions:
                    error_string = f"Did not recognize try: turn-left, turn-right or direction - sent from: {self.jid}"
                    self.send_message(mto=sender.bare, mbody=error_string)
                    return

                print(command)

                if not self.processess:
                    self.process_n = self.n
                    self.processess[self.n] = {"sender": sender.bare, "command": command }
                    self.sendRequest(sender.bare, command[0])
                else:
                    self.process_n += 1
                    self.processess[self.process_n] = { "sender": sender.bare, "command": command }
        else:
            self.send_message(mto=sender.bare, mbody=f"Unauthorized! Ask {self.current_leader}")


    def figureDirection(self, action):
        if self.direction == 'north':
            tmp = { 'turn-right': 'east', 'turn-left': 'west' }
            return tmp[action]
        elif self.direction == 'south':
            tmp = {'turn-right': 'west', 'turn-left': 'east'}
            return tmp[action]
        elif self.direction == 'east':
            tmp = {'turn-right': 'south', 'turn-left': 'north'}
            return tmp[action]
        else:
            tmp = {'turn-right': 'north', 'turn-left': 'south'}
            return tmp[action]


    def sendRequest(self, sender, command):
        self.requester = sender
        self.own_vote = self.figureDirection(command)
        self.ballad_votes.append(self.own_vote)
        self.send_message(mto=self.bot_room,
                          mbody=f'prepare {self.n} {self.jid} {self.requester} {command}',
                          mtype='groupchat')


    def getLogString(self):
        with open('commands.log', 'r') as f:
            return f.read()

    def muc_message(self, msg):

        if msg['mucnick'] != self.nick:
            spltCommand = msg["body"].split()
            headCommand = spltCommand[0]
            if 'prepare' == headCommand:
                self.n = spltCommand[1]
                messageTo = spltCommand[2]
                self.requester = spltCommand[3]

                # TODO: decide vote
                self.own_vote = self.figureDirection(spltCommand[4])

                self.send_message(mto=messageTo,
                                  mbody=f'promise {self.n} {self.own_vote}')
            elif 'accept' == headCommand:

                if spltCommand[3] == self.own_vote:
                    response_message = f"accepted {self.n} agree {self.own_vote}"
                    self.direction = spltCommand[3]
                else:
                    response_message = f"accepted {self.n} disagree {self.own_vote}"


                messageTo = spltCommand[2]
                self.send_message(mto=messageTo,
                                mbody=response_message)

            """
            self.send_message(mto=msg['from'].bare,
                              mbody="I heard that, %s." % msg['mucnick'],
                              mtype='groupchat')
            """

    def muc_online(self, presence):

        incomer = f'{presence["muc"]}@{self.domain}'

        if incomer in self.quorums:
            self.active_quorums.append(incomer)

        #self.server_count += 1

        # if presence['muc']['nick'] != self.nick:
        #    self.send_message(mto=presence['from'].bare,
        #                      mbody="Hello %s %s" % (presence['muc']['role'],
        #                                              presence['muc']['nick']),
        #                      mtype='groupchat')

        # self.dumbRosterIncr(presence['muc']['nick'])

    def muc_offline(self, presence):

        goner_jid = f"{presence['muc']['nick']}@{self.domain}"
        if goner_jid in self.active_quorums:
            self.active_quorums.remove(goner_jid)

        if goner_jid in self.quorums:
            print('is goner')
            self.quorums.remove(goner_jid)

            self.current_leader = self.quorums.pop()
            self.quorums.append(self.current_leader)

            print(self.current_leader)

            if self.jid == self.current_leader:
                print('is the new leader')
                self.leader = True

                '''
                with open(f'{goner_jid}_log.log', 'r') as f:
                    text = f.read()
                    text = text.split('\n')
                    self.n = text[:text.count() - 1].split()[0]

                    print(text[:text.count() - 1].split()[0])
                '''

                self.sendRequest(self.requester)



        print(self.quorums)

        if goner_jid == self.current_leader:
            print(self.quorums[0])




if __name__ == '__main__':
    # Setup the command line arguments.
    optp = OptionParser()

    # Output verbosity options.
    optp.add_option('-q', '--quiet', help='set logging to ERROR',
                    action='store_const', dest='loglevel',
                    const=logging.ERROR, default=logging.INFO)
    optp.add_option('-d', '--debug', help='set logging to DEBUG',
                    action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)
    optp.add_option('-v', '--verbose', help='set logging to COMM',
                    action='store_const', dest='loglevel',
                    const=5, default=logging.INFO)

    # JID and password options.
    optp.add_option("-j", "--jid", dest="jid",
                    help="JID to use")
    optp.add_option("-p", "--password", dest="password",
                    help="password to use")
    optp.add_option("-r", "--room", dest="room",
                    help="MUC room to join")
    optp.add_option("-n", "--nick", dest="nick",
                    help="MUC nickname")

    opts, args = optp.parse_args()

    # Setup logging.
    #logging.basicConfig(level=opts.loglevel,
                        #format='%(levelname)-8s %(message)s')

    leader = False

    if (len(sys.argv) > 1):
        opts.jid = sys.argv[1]
        opts.password = sys.argv[2]
        opts.room = sys.argv[3]
        opts.nick = sys.argv[4]
        if sys.argv[1] == 'bot1@3.18.234.195':
            leader = True
    else:
        if opts.jid is None:
            opts.jid = raw_input("Username: ")
        if opts.password is None:
            opts.password = getpass.getpass("Password: ")
        if opts.room is None:
            opts.room = raw_input("MUC room: ")
        if opts.nick is None:
            opts.nick = raw_input("MUC nickname: ")


    xmpp = MUCBot(opts.jid, opts.password, opts.room, opts.nick, leader)
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0045') # Multi-User Chat
    xmpp.register_plugin('xep_0199') # XMPP Ping

    # Connect to the XMPP server and start processing XMPP stanzas.
    if xmpp.connect():

        xmpp.process(block=True)


        print("Done")
    else:
        print("Unable to connect.")