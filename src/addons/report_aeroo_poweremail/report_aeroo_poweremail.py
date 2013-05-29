# -*- encoding: utf-8 -*-
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

from osv import osv
from osv import fields

class poweremail_templates(osv.osv):
    _name = 'poweremail.templates'
    _inherit = 'poweremail.templates'

    def __init__(self, pool, cr):
        super(poweremail_templates, self).__init__(pool, cr)
        if ('aeroo', 'Aeroo reports') not in self._columns['template_language'].selection:
            self._columns['template_language'].selection.append(
                        ('aeroo', 'Aeroo Reports'),
                    )

    
    _columns = {
        'aeroo_report_id':fields.many2one('ir.actions.report.xml', 'Aeroo Report'),
        
    }

    def onchange_null_value(self, cr, uid, ids, model_object_field, sub_model_object_field, null_value, template_language, context=None):
        res = super(poweremail_templates, self).onchange_null_value(cr, uid, ids, model_object_field, sub_model_object_field, null_value, template_language, context)
        if template_language=='aeroo':
            res.update({"value":{"def_body_html":"***aeroo-template***"}})
        elif template_language=='mako' and ids:
            read_res = self.read(cr, uid, ids[0], ['def_body_html'], context=context)
            if read_res['def_body_html']=='***aeroo-template***':
                trans_obj = self.pool.get('ir.translation')
                trans_ids = trans_obj.search(cr, uid, [('type','=','model'),('name','=','poweremail.templates,def_body_html'),('res_id','in',ids)], context=context)
                trans_obj.write(cr, uid, trans_ids, {'value':False}, context=context)
                res.update({"value":{"def_body_html":False}})
        return res

poweremail_templates()

