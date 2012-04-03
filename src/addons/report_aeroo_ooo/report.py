##############################################################################
#
# Copyright (c) 2009-2011 Alistek Ltd (http://www.alistek.com) All Rights Reserved.
#                    General contacts <info@alistek.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This module is GPLv3 or newer and incompatible
# with OpenERP SA "AGPL + Private Use License"!
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from osv import osv,fields
import netsvc
from DocumentConverter import DocumentConverter

class OpenOffice_service (DocumentConverter, netsvc.Service):

    def __init__(self, cr, host, port):
        cr.execute("SELECT host, port FROM oo_config")
        host, port = cr.fetchone()
        DocumentConverter.__init__(self, host, port)
        netsvc.Service.__init__(self, 'openoffice')


class oo_config(osv.osv):
    '''
        OpenOffice connection
    '''
    _name = 'oo.config'
    _description = 'OpenOffice connection'

    _columns = {
        'host':fields.char('Host', size=128, required=True),
        'port': fields.integer('Port', required=True),
        
    }

oo_config()

class report_xml(osv.osv):
    _name = 'ir.actions.report.xml'
    _inherit = 'ir.actions.report.xml'

    _columns = {
        'process_sep':fields.boolean('Process separately'),
        
    }

report_xml()

