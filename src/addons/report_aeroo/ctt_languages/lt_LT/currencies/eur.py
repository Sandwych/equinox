#!/usr/bin/python
# -*- coding: utf8 -*-

from report_aeroo.ctt_objects import ctt_currency

class eur(ctt_currency):
    def _init_currency(self):
        self.language = u'lt_LT'
        self.code = u'EUR'
        self.fractions = 100
        self.cur_singular = u' euras'
        # default plural form for currency
        self.cur_plural = u' eurų'
        # betwean 1 and 10 yields different plural form, if defined
        self.cur_plural_2to10 = u' eurai'
        self.frc_singular = u' centas'
        # default plural form for fractions
        self.frc_plural = u' centų'
        # betwean 1 and 10 yields different plural form, if defined
        self.frc_plural_2to10 = u' centai'
        # grammatical genders: f - feminine, m - masculine, n -neuter
        self.cur_gram_gender = 'm'
        self.frc_gram_gender = 'm'
    
eur()
