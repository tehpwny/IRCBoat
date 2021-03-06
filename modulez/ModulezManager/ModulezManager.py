#!/usr/bin/python3
#-*- coding: utf-8 -*-
import os

class ModulezManager():
    def __init__(self,boat):
        self.bangz = {
            'list_modulez': self.list_modulez,
            'install_module': self.install_module
            }
        self.boat = boat
        self.availablemodulez = []
        self.set_available_modulez()

    # Module management

    # BANGZ Methodz
    def list_modulez(self, dst, sender, argz):
        modulez = ''
        for module in self.availablemodulez:
            self.boat.msg(dst, module)

    def install_module(self, dst, sender, argz):
        if argz[0] in self.availablemodulez:
            self.boat.load_module(argz[0])
            self.boat.msg(dst, 'Module ' + argz[0] + ' chargé')
        else:
            self.boat.msg(dst, 'Module ' + argz[0] + ' inconnu')

    def set_available_modulez(self):
        for root, dirz, filez in os.walk("."):
            if root == "./modulez":
                print(dirz)
                self.availablemodulez = dirz

    def load_available_modulez(self):
        for module in self.availablemodulez:
            load_module(module)
