##############################################################################
#
# Copyright (c) 2008-2012 Alistek Ltd (http://www.alistek.com) All Rights Reserved.
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

from openerp.osv import osv,fields
from openerp import netsvc
try:
    from DocumentConverter import DocumentConverter
except NameError:
    class DocumentConverter:
        pass

class OpenOffice_service (DocumentConverter):

    def __init__(self, cr, host, port):
        cr.execute("SELECT host, port, ooo_restart_cmd FROM oo_config")
        host, port, ooo_restart_cmd = cr.fetchone()
        DocumentConverter.__init__(self, host, port, ooo_restart_cmd)

class oo_config(osv.osv):
    '''
        OpenOffice connection
    '''
    _name = 'oo.config'
    _description = 'OpenOffice connection'

    _columns = {
        'host':fields.char('Host', size=128, required=True),
        'port': fields.integer('Port', required=True),
        'ooo_restart_cmd': fields.char('OOO restart command', size=256, \
            help='Enter the shell command that will be executed to restart the LibreOffice/OpenOffice background process. '+ \
                'The command will be executed as the user of the OpenERP server process,'+ \
                'so you may need to prefix it with sudo and configure your sudoers file to have this command executed without password.'),
        
    }


class report_xml(osv.osv):
    _name = 'ir.actions.report.xml'
    _inherit = 'ir.actions.report.xml'

    _columns = {
        'process_sep':fields.boolean('Process Separately'),
        
    }

