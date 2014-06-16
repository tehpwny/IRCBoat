#!/usr/bin/python3
#-*- coding: utf-8 -*-
#
#
#
# A l'attention des singes codeurs de BOAT :
#
# Convention de nommage (PEP-8):
    # classes : CorrectClassName
    # exceptions : IncorrectClassNameError (suffixe "Error" !)
    # fonctions : get_correct_number()
    # méthodes : get_correct_number(self, arg1=None, arg2, arg3)
    # arguments des méthodes et fonctions : get_correct_number(random=False, arg2)
    # variables : number = my_object.get_correct_number()
    # constantes : ANSWER_TO_LIFE_UNIVERSE = 42
#
#
#
# imports utiles aux anciennes fonctions, à moduler plus tard (pour moi)
# from fractions import Fraction as fr
# from random import randrange
# import sys, random, math

# next on pwny rox at python : class BOATModule with eventhandle funcz
import socket
import time
import ssl
import os
import sys
from urllib.request import urlopen
from urllib.error import URLError

class IRCBoat():

    def __init__(self, host, port, nick, ident, realname):
        self.host = host
        self.port = port
        self.nick = nick
        self.ident = ident
        self.realname = realname
        self.users = ['niko', 'pwny'] # Default users for BOAT
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(20)
        self.buffer = '' # Data read from chanz
        self.bangzlist = {} # Dictionnary containing the module functions availables
        self.timestamp = time.time()
        self.refreshrate = 5
        self.modulez = {} # Dictionnary containing the modules installed

    def load_module(self, modulename):
        if modulename not in self.modulez.keys():
            newmodule = __import__('modulez.' + modulename + '.' + modulename, fromlist=[modulename])
            print(newmodule)
            print(dir(newmodule))
            #moduleclass_ = getattr(newmodule, "BaseIRC")
            moduleclass_ = getattr(newmodule, modulename)

            self.modulez[modulename] = moduleclass_(self)
            print(modulename + ' loaded')
            for bang, func in self.modulez[modulename].bangz.items():
                if bang in self.bangzlist.keys():
                    print("Le bang est déjà utilisé => ignoré")
                else:
                    self.bangzlist[bang] = func

            print('dbug', self.modulez)
        else:
            print("Module déjà chargé")

    # Methodes
    #
    # Methodes de connexions


    def connect(self):
        """Connection au serveur"""
        self.socket.connect((self.host, self.port))
        self.raw_irc_command('NICK ' + self.nick)
        print(('USER ' + self.ident + ' ' + self.host + ' :' + self.realname))
        self.raw_irc_command('USER ' + self.ident + ' ' + self.host + ' '
                             + self.host + ' :' + self.realname)
        print('Connexion OK')

    def ssl_connect(self):
        """Connection au serveur en SSL"""
        self.socket.connect((self.host, self.port))
        self.socket = ssl.wrap_socket(self.socket, keyfile=None,
                                      certfile=None, server_side=False,
                                      do_handshake_on_connect=False,
                                      suppress_ragged_eofs=True)
        self.raw_irc_command('NICK ' + self.nick)
        print(('USER ' + self.ident + ' ' + self.host + ' :' + self.realname))
        self.raw_irc_command('USER ' + self.ident + ' ' + self.host + ' '
                             + self.host + ' :' + self.realname)
        print('Connexion OK')

    # Authentication processing TODO
    def is_boat_user(self, nick):
        return nick in self.users

    def clean_buffer(self, buffr):
        clean = []
        for item in buffr:
            clean.append(item.strip())
        return clean

    # BOAT Commandz
    def event_bcast(self,event,source, dest, text):
      print('bcast:',event,source, dest, text)
      for mod in self.modulez.items():
        try:
          getattr(mod[1],event)(source, dest, text)
        except AttributeError:
          print('no',event,'for',mod[1].__class__.__name__,':(')

    def handle_event(self, msg):
        print('msg',msg)
        if len(msg) < 2:
          return
        text = ''
        for i in msg[3:]:
          text += i + ' '
        #print('TEXT before :', text)
        text = text[1:].rstrip()
        #print('TEXT after :', text)
        dest = msg[2]
        try:
          source = msg[0].split('!')[0].split(':')[1]
        except IndexError as e:
          print('something awful happend :',e)
        if msg[1] == 'PRIVMSG':
          # for bangz ----
          cmd = msg[3].strip('\r').strip('\n').split(':')[1]
          argz = msg[4:]
          if cmd == '' :
              cmd = ' '
          if dest.find(self.nick) != -1: # private message to BOAT --------
              print('command')
              return
              # handle_cmd
        #------------------------------------------------------------------
          if dest.find('#') != -1: # channel message ----------------------
              if msg[3].find(':\x01ACTION') != -1:
                self.event_bcast('eventchanaction',source,dest,text)
              else:
                self.event_bcast('eventchanmsg',source,dest,text)
              if self.is_bang(cmd): # which is a bang
                  msg = self.clean_buffer(msg)
                  bang = cmd.split('!')[1]
                  print('bang :', bang) # my baby shot me down
                  if bang in self.bangzlist.keys():
                      retour = self.bangzlist[bang](dest, source, argz)
                      print(retour)
        # ---------------------------------------------------------------
        if msg[1] == 'NICK':
          print('eventnick')
          self.event_bcast('eventnick',source, dest, text)
        if msg[1] == 'MODE':
          print('eventmode')
          self.event_bcast('eventmode',source, dest, text)
        if msg[1] == 'QUIT':
          print('eventquit')
          self.event_bcast('eventquit',source, dest, text)
        if msg[1] == 'JOIN':
          print('eventjoin')
          self.event_bcast('eventjoin',source, dest, text)
        if msg[1] == 'PART':
          print('eventpart')
          self.event_bcast('eventpart',source, dest, text)
        if msg[1] == 'MODE':
          print('eventmode')
          self.event_bcast('eventmode',source, dest, text)
        if msg[1] == 'KICK':
          print('eventkick')
          self.event_bcast('eventkick',source, dest, text)
        if msg[1] == 'TOPIC':
          print('eventtopic')
          self.event_bcast('eventtopic',source, dest, text)
        if msg[1] == 'NOTICE':
          print('eventnotice')
          self.event_bcast('eventnotice',source, dest, text)


    def is_bang(self, cmd):
        if cmd[0] == '!':
            # TODO : cherche si c'est un bang qui retourne une fonction
            return True
        else:
            return False

    # Data processing
    def listen_input(self):
        ''' Écoute les messages du serveur '''
        lines = self.process_buffer()
        res = ''
        for line in lines:
            msg = line.split(' ')
            if msg[0] == 'PING':
                self.pong(msg[1].split(":")[1])
            else:
              try:
                  res = socket.getaddrinfo(msg[0].strip(':'),self.port)[1][4][0]
              except socket.gaierror:
                  pass
              except IndexError:
                  pass
              if res == self.host:
                  print('server :', line)

              else:
                  self.handle_event(msg)


    def process_buffer(self):
        ''' Traitement initial du buffer '''
        self.buffer = ''
        try:
            self.buffer = str(self.socket.recv(4096).decode('utf-8'))
            print('Buffer : ')
            print(self.buffer)
        except socket.error as e:
            err = e.args[0]
            if err == 'timed out':
              #print('debug :',err)
              pass
            else:
              print('Error while receiving buffer :',err)

        if self.buffer != '':
            self.buffer = self.buffer.split("\n")
            self.buffer.pop()
            pass
        return self.buffer

    def print_state(self):
        '''Dump du buffer (debug)'''
        print(self.socket.recv(4096))

    # Basic IRC methodz
    def pong(self, ping):
        ''' Fonction de réponse aux ping'''
        self.raw_irc_command('PONG ' + ping)
        print('Ping : ' + ping)

    def join(self, chan):
        ''' Joindre un chan '''
        self.raw_irc_command('JOIN ' + chan)

    def msg(self, dest, message):
        ''' Envoie un message à un chan ou un user '''
        self.raw_irc_command('PRIVMSG ' + dest + ' :' + str(message))
        print(">" + dest, ":", message)

    def topic(self, chan, topic):
        self.raw_irc_command('TOPIC ' + chan + ' :' + topic)

    def set_mode(self, chan, mode, nick=None):
        ''' Change les modes d\'un salon ou d\'un user '''
        self.raw_irc_command('MODE ' + chan + ' ' + mode + ' ' + nick)
        print('mode', chan, mode, nick)

    def raw_irc_command(self, cmd):
        """Envoie de commande IRC brute"""
        self.send(str(cmd) + '\r\n')

    def send(self, data):
        ''' Envoie brut au socket '''
        try:
          self.socket.send(bytes(data, 'UTF-8'))
        except socket.error:
          print('oh shit')
