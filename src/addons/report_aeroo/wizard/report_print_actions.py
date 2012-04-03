##############################################################################
#
# Copyright (c) 2008-2011 Alistek Ltd (http://www.alistek.com) All Rights Reserved.
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

from osv import osv
from osv import fields

class report_print_actions(osv.osv_memory):
    _name = 'aeroo.print_actions'
    _description = 'Aeroo reports print wizard'

    def to_print(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0], context=context)
        report_xml = self.pool.get('ir.actions.report.xml').browse(cr, uid, context['report_action_id'])
        print_ids = []
        if this.copies<=0:
            print_ids = context['active_ids']
        else:
            while(this.copies):
                print_ids.extend(context['active_ids'])
                this.copies -= 1
        data = {'model':report_xml.model, 'ids':print_ids, 'id':context['active_id'], 'report_type': 'aeroo'}
        if report_xml.out_format.id != this.out_format:
            report_xml.write({'out_format':this.out_format}, context=context)
        return {
            'type': 'ir.actions.report.xml',
            'report_name': report_xml.report_name,
            'datas': data,
            'context':context
        }

    def _out_format_get(self, cr, uid, context={}):
        obj = self.pool.get('report.mimetypes')
        in_format = self.pool.get('ir.actions.report.xml').read(cr, uid, context['report_action_id'], ['in_format'])['in_format']
        ids = obj.search(cr, uid, [('compatible_types','=',in_format)], context=context)
        res = obj.read(cr, uid, ids, ['name'], context)
        return [(r['id'], r['name']) for r in res]
    
    _columns = {
        'out_format': fields.selection(_out_format_get, 'Output format', required=True),
        'copies': fields.integer('Number of copies', required=True),
        
    }

    def _get_default_outformat(self, cr, uid, context):
        report_xml = self.pool.get('ir.actions.report.xml').browse(cr, uid, context['report_action_id'])
        return report_xml.out_format.id

    def _get_default_number_of_copies(self, cr, uid, context):
        report_xml = self.pool.get('ir.actions.report.xml').browse(cr, uid, context['report_action_id'])
        return report_xml.copies

    _defaults = {
        'out_format': _get_default_outformat,
        'copies': _get_default_number_of_copies,
    }
report_print_actions()

