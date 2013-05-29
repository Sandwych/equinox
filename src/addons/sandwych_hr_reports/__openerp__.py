# -*- encoding: utf-8 -*-
##############################################################################
#
#    WychERP Business Application Platform
#    Copyright (C) 2012 Kunming Sandwych Consulting Limited (<http://www.sandwych.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
{
    'name': u'人事系统报表增强',
    'category': 'Sandwych',
    'author': u'昆明维智众源企业管理咨询有限公司',
    'depends': ['hr', 'hr_expense', 'report_aeroo'],
    'version': '1.0',
    'website': 'www.sandwych.com',
    'description': """
        HR 报表改进
    """,

    'auto_install': False,
    'demo': [
    ],
    'data':[
     'hr_report.xml',
    ],
    'installable': True
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
