#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 OpenERP SA (<http://openerp.com>). All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv
import decimal_precision as dp

class hr_contract_cn(osv.osv):
    _inherit = 'hr.contract'

    _columns = {
        'social_insurance_amount': fields.float('社保基数', digits_compute=dp.get_precision('Payroll')),
        'pit_exemption_amount': fields.float('个税起征点', required=True, digits_compute=dp.get_precision('Payroll')),
    }

    _defaults = {
        'pit_exemption_amount': 3500.00,
    }
    
hr_contract_cn()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
