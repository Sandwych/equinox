#!/usr/bin/python
# -*- coding: utf8 -*-

from report_aeroo.ctt_objects import ctt_currency

class uah(ctt_currency):
    def _init_currency(self):
        self.language = u'lv_LV'
        self.code = u'UAH'
        self.fractions = 100
        self.cur_singular = u' grivna'
        # default plural form for currency
        self.cur_plural = u' grivnu'
        # betwean 1 and 10 yields different plural form, if defined
        self.cur_plural_2to10 = u' grivnas'
        self.frc_singular = u' kapeika'
        # default plural form for fractions
        self.frc_plural = u' kapeiku'
        # betwean 1 and 10 yields different plural form, if defined
        self.frc_plural_2to10 = u' kapeikas'
        # grammatical genders: f - feminine, m - masculine, n -neuter
        self.cur_gram_gender = 'f'
        self.frc_gram_gender = 'f'
uah()
