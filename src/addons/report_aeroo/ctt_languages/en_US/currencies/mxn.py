#!/usr/bin/python
# -*- coding: utf8 -*-

from report_aeroo.ctt_objects import ctt_currency

class mxn(ctt_currency):
    def _init_currency(self):
        self.language = u'en_US'
        self.code = u'MXN'
        self.fractions = 100
        self.cur_singular = u' Mexican peso'
        self.cur_plural = u' Mexican pesos'
        self.frc_singular = u' cent'
        self.frc_plural = u' cents'
        # grammatical genders: f - feminine, m - masculine, n -neuter
        self.cur_gram_gender = 'm'
        self.frc_gram_gender = 'm'
    
mxn()
