##############################################################################
#
# Copyright (c) 2008-2013 Alistek Ltd (http://www.alistek.com) All Rights Reserved.
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
from tools.translate import _

import netsvc
import cups
from tempfile import NamedTemporaryFile
import md5
SUPPORTED_PRINT_FORMAT = ('pdf','raw')
SPECIAL_PRINTERS = ('user-def-gen-purpose-printer','user-def-label-printer')

class report_print_actions(osv.osv_memory):
    _name = 'aeroo.print_actions'
    _inherit = 'aeroo.print_actions'

    def report_to_printer(self, cr, uid, ids, report_id, printer, context={}):
        context['active_ids'] = ids
        report = self.pool.get('ir.actions.report.xml').browse(cr, uid, report_id, context=context)
        data = {'model':  report.model, 'id': context['active_ids'][0], 'report_type': 'aeroo'}
        res = netsvc.Service._services['report.%s' % report.report_name].create(cr, uid, context['active_ids'], data, context=context)
        if res[1] in SUPPORTED_PRINT_FORMAT:
            with NamedTemporaryFile(suffix='', prefix='aeroo-print-', delete=False) as temp_file:
                temp_file.write(res[0])
            conn = cups.Connection()
            return conn.printFile(printer, temp_file.name, 'Aeroo Print', {'copies': report.copies > 0 and str(report.copies) or '1'})
        else:
            raise osv.except_osv(_('Warning!'), _('Unsupported report format "%s". Is not possible direct print to printer.') % res[1])
        return False

    def to_print(self, cr, uid, ids, context={}):
        this = self.browse(cr, uid, ids[0], context=context)
        report_xml = self.pool.get('ir.actions.report.xml').browse(cr, uid, context['report_action_id'])
        self.check_report(report_xml.report_name)
        if this.printer:
            data = {'model':  report_xml.model, 'id': this.print_ids[0], 'report_type': 'aeroo'}
            res = netsvc.Service._services['report.%s' % report_xml.report_name].create(cr, uid, this.print_ids, data, context=context)
            if res[1] in SUPPORTED_PRINT_FORMAT:
                with NamedTemporaryFile(suffix='', prefix='aeroo-print-', delete=False) as temp_file:
                    temp_file.write(res[0])
                conn = cups.Connection()
                conn.printFile(this.printer, temp_file.name, 'Aeroo Print', {'copies': this.copies > 0 and str(this.copies) or '1'})
                return {
                    'type': 'ir.actions.act_window_close'
                }

        print_ids = []
        if this.copies<=0:
            print_ids = this.print_ids
        else:
            while(this.copies):
                print_ids.extend(this.print_ids)
                this.copies -= 1
        if report_xml.out_format.id != this.out_format:
            report_xml.write({'out_format':this.out_format}, context=context)
        if self.check_if_deferred(report_xml, this.print_ids):
            return this.write({'state':'confirm','message':_("This process may take too long for interactive processing. \
It is advisable to defer the process in background. \
Do you want to start a deferred process?"),'print_ids':print_ids}, context=context)

        data = {'model':report_xml.model, 'ids':print_ids, 'id':context['active_id'], 'report_type': 'aeroo'}
        context['aeroo_dont_print_to_pinter'] = True
        return {
            'type': 'ir.actions.report.xml',
            'report_name': report_xml.report_name,
            'datas': data,
            'context':context
        }

    def _get_printers(self, cr, uid, context={}):
        printers_obj = self.pool.get('aeroo.printers')
        ids = printers_obj.search(cr, uid, [], context=context)
        printers = printers_obj.read(cr, uid, ids, ['name', 'code', 'state'], context=context)
        return [('','')]+[(p['code'], p['name']) for p in printers if p['code'] not in SPECIAL_PRINTERS]
    
    _columns = {
        'printer': fields.selection(_get_printers, 'Print to Printer', required=False),
        
    }

    def _get_default_printer(self, cr, uid, context):
        report_action_id = context.get('report_action_id', False)
        report_xml = report_action_id and self.pool.get('ir.actions.report.xml').browse(cr, uid, report_action_id, context=context) or False
        if report_xml and report_xml.printer_id:
            try:
                if report_xml.printer_id.code in SPECIAL_PRINTERS:
                    printer_id = context.get("def_%s_%s" % tuple(report_xml.printer_id.code.split('-')[-2:]), False)
                    if printer_id:
                        return self.pool.get('aeroo.printers').browse(cr, uid, printer_id, context=context).code
                else:
                    return report_xml.printer_id.code
            except Exception, e:
                return False
        return False

    _defaults = {
        'printer': _get_default_printer,
        
    }

report_print_actions()

class aeroo_printers(osv.osv):
    _name = 'aeroo.printers'
    _description = 'Available printers for Aeroo direct print'

    def _get_state(self, cr, uid, ids, name, args, context={}):
        res = {}
        conn = cups.Connection()
        printers = conn.getPrinters()
        for p in self.browse(cr, uid, ids, context=context):
            state = printers.get(p.code, {}).get('printer-state')
            res[p.id] = state and str(state) or state
        return res
    
    _columns = {
        'name':fields.char('Description', size=256, required=True),
        'code':fields.char('Name', size=64, required=True),
        'note': fields.text('Details'),
        'group_ids':fields.many2many('res.groups', 'aeroo_printer_groups_rel', 'printer_id', 'group_id', 'Groups'),
        'state': fields.function(_get_state, type='selection', selection=[('3', _('Idle')),
                                                                        ('4', _('Busy')),
                                                                        ('5', _('Stopped'))], method=True, store=False, string='State', help=''),
        'active':fields.boolean('Active'),
        
    }

    def search(self, cr, user, args, offset=0, limit=None, order=None, context={}, count=False):
        if context and not context.get('view_all'):
            args.append(('code','not in',SPECIAL_PRINTERS))
        res = super(aeroo_printers, self).search(cr, user, args, offset, limit, order, context, count)
        return res

    def refresh(self, cr, uid, ids, context={}):
        conn = cups.Connection()
        printers = conn.getPrinters()
        for r in self.browse(cr, uid, ids, context=context):
            data = printers.get(r.code)
            if not data:
                raise osv.except_osv(_('Error!'), _('Printer "%s" not found!') % r.code)
            note = '\n'.join(map(lambda key: "%s: %s" % (key, data[key]), data))
            r.write({'note':note}, context=context)
        return True

    _defaults = {
        'active': True,
        
    }
aeroo_printers()

class res_users(osv.osv):
    _name = 'res.users'
    _inherit = 'res.users'
    
    _columns = {
        'context_def_purpose_printer': fields.property(
            'aeroo.printers',
            type='many2one',
            relation='aeroo.printers',
            string='Default Genreral Purpose Printer',
            method=True,
            view_load=True,
            domain='[("code","not in",%s)]' % str(SPECIAL_PRINTERS),
            help="",
            required=False),
        'context_def_label_printer': fields.property(
            'aeroo.printers',
            type='many2one',
            relation='aeroo.printers',
            string='Default Label Printer',
            method=True,
            view_load=True,
            domain='[("code","not in",%s)]' % str(SPECIAL_PRINTERS),
            help="",
            required=False),
        
    }
res_users()

class report_xml(osv.osv):
    _name = 'ir.actions.report.xml'
    _inherit = 'ir.actions.report.xml'
    
    _columns = {
        'printer_id':fields.many2one('aeroo.printers', 'Printer', help='Printer for direct print, or printer selected by default, if "Report Wizard" field is checked.'),
        
    }

    def unlink(self, cr, uid, ids, context={}):
        act_srv_obj = self.pool.get('ir.actions.server')
        reports = self.read(cr, uid, ids, ['report_wizard','printer_id'])
        for r in reports:
            if not r['report_wizard'] and r['printer_id']:
                act_srv_id = act_srv_obj.search(cr, uid, [('code','like','# %s #' % md5.md5(str(r['id'])).hexdigest())], context=context)
                if act_srv_id:
                    act_srv_obj.unlink(cr, uid, act_srv_id, context=context)
        res = super(report_xml, self).unlink(cr, uid, ids, context)
        return res

    def create(self, cr, user, vals, context={}):
        res_id = super(report_xml, self).create(cr, user, vals, context)
        if vals.get('report_type') == 'aeroo' and not vals.get('report_wizard') and vals.get('printer_id'):
            self._set_report_server_action(cr, user, res_id, context)
        return res_id

    def write(self, cr, user, ids, vals, context={}):
        if type(ids)==list:
            ids = ids[0]
        record = self.read(cr, user, ids)
        if vals.get('report_type', record['report_type']) == 'aeroo':
            if ('report_wizard' in vals and not vals['report_wizard'] or
               'report_wizard' not in vals and not record['report_wizard']) and \
                    ('printer_id' in vals and vals['printer_id'] or 'printer_id' not in vals and record['printer_id']):
                res = super(report_xml, self).write(cr, user, ids, vals, context)
                self._set_report_server_action(cr, user, ids, context)
            elif 'printer_id' in vals and not vals.get('printer_id') or vals.get('report_wizard'):
                self._unset_report_server_action(cr, user, ids, context)
                res = super(report_xml, self).write(cr, user, ids, vals, context)
            else:
                res = super(report_xml, self).write(cr, user, ids, vals, context)
        else:
            res = super(report_xml, self).write(cr, user, ids, vals, context)
        return res

    def _set_report_server_action(self, cr, uid, ids, context={}):
        report_id = isinstance(ids, list) and ids[0] or ids
        report = self.browse(cr, uid, report_id, context=context)
        if not report.report_wizard:
            ir_values_obj = self.pool.get('ir.values')
            event_id = ir_values_obj.search(cr, uid, [('value','=',"ir.actions.report.xml,%s" % report_id)])
            if event_id:
                event_id = event_id[0]
                model_id = self.pool.get('ir.model').search(cr, uid, [('model','=',report.model)], context=context)[0]
                python_code = """
# %s #
report_action_id = %s
context['report_action_id'] = report_action_id
print_actions_obj = self.pool.get('aeroo.print_actions')
printer = print_actions_obj._get_default_printer(cr, uid, context)
print_actions_obj.report_to_printer(cr, uid, [obj.id], report_action_id, printer, context=context)
""" % (md5.md5(str(report_id)).hexdigest(), report_id)
                action_data = {'name':report.name,
                               'model_id':model_id,
                               'state':'code',
                               'code':python_code,
                               }
                act_id = self.pool.get('ir.actions.server').create(cr, uid, action_data, context)
                ir_values_obj.write(cr, uid, event_id, {'value':"ir.actions.server,%s" % act_id}, context=context)

                return act_id
        return False

    def _unset_report_server_action(self, cr, uid, ids, context={}):
        report_id = isinstance(ids, list) and ids[0] or ids
        ir_values_obj = self.pool.get('ir.values')
        act_srv_obj = self.pool.get('ir.actions.server')
        act_srv_id = act_srv_obj.search(cr, uid, [('code','like','# %s #' % md5.md5(str(report_id)).hexdigest())], context=context)
        if act_srv_id:
            event_id = ir_values_obj.search(cr, uid, [('value','=',"ir.actions.server,%s" % act_srv_id[0])])
            if event_id:
                event_id = event_id[0]
                ir_values_obj.write(cr, uid, event_id, {'value':"ir.actions.report.xml,%s" % report_id}, context=context)
            act_srv_obj.unlink(cr, uid, act_srv_id, context=context)
            return True
        return False

report_xml()

