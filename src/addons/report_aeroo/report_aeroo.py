# -*- encoding: utf-8 -*-

##############################################################################
#
# Copyright (c) 2009-2013 Alistek Ltd (http://www.alistek.com) All Rights Reserved.
#                    General contacts <info@alistek.com>
# Copyright (C) 2009  Domsense s.r.l.                                   
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

import os, sys, traceback
from tempfile import NamedTemporaryFile
from openerp import report
from openerp.report.report_sxw import report_sxw, report_rml
from openerp.osv.orm import browse_record_list
from pyPdf import PdfFileWriter, PdfFileReader
#import zipfile
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
from xml.dom import minidom
import base64
from openerp.osv import osv
from openerp.tools.translate import _
from openerp import tools
import time
import re
import copy
import threading
from random import randint

try:
    from addons import load_information_from_description_file # for OpenERP 6.0.x
except ImportError:
    from openerp.modules import load_information_from_description_file # for OpenERP 6.1
from openerp import release

import aeroolib
from aeroolib.plugins.opendocument import Template, OOSerializer
from genshi.template import NewTextTemplate
from genshi import __version__ as genshi_version
from openerp import pooler
from openerp import netsvc
from lxml import etree
import logging

logger = logging.getLogger(__name__)

from ExtraFunctions import ExtraFunctions

try:
    aeroo_lock = threading.Lock()
    msg = "Aeroo lock instantiated."
    logger.log(logging.INFO, msg)
except Exception:
    err_msg = "Could not instantiate Aeroo lock!!!"
    logger.log(logging.CRITICAL, err_msg)

def aeroo_ooo_test(cr):
    '''
    Detect report_aeroo_ooo module
    '''
    aeroo_ooo = False
    cr.execute("SELECT id, state FROM ir_module_module WHERE name='report_aeroo_ooo'")
    helper_module = cr.dictfetchone()
    if helper_module and helper_module['state'] in ('installed', 'to upgrade'):
        aeroo_ooo = True
    return aeroo_ooo

class Counter(object):
    def __init__(self, name, start=0, interval=1):
        self.name = name
        self._number = start
        self._interval = interval

    def next(self, increment=True):
        if increment:
            self._number += self._interval
            return self._number
        else:
            return self._number + self._interval

    def get_inc(self):
        return self._number

    def prev(self, decrement=True):
        if decrement:
            self._number -= self._interval
            return self._number
        else:
            return self._number-self._interval

class AerooPrint(object):
    print_ids = [] # static property
    def __init__(self):
        print_id = False
        while(not print_id or print_id in self.print_ids):
            print_id = randint(1, 99999)
        self.print_ids.append(print_id)
        self.id = print_id
        self.subreports = []
        self.epl_images = []
        self.counters = {}
        self.start_time = 0
        self.start_total_time = 0

class Aeroo_report(report_sxw):

    def logger(self, message, level=logging.DEBUG):
        logger.log(level, message, exc_info=1)

    def __init__(self, cr, name, table, rml=False, parser=False, header=True, store=False):
        super(Aeroo_report, self).__init__(
            name, table, rml, parser, header, store, register=False)
        self.logger("registering %s (%s)" % (name, table), logging.INFO)
        self.active_prints = {}

        pool = pooler.get_pool(cr.dbname)
        ir_obj = pool.get('ir.actions.report.xml')
        name = name.startswith('report.') and name[7:] or name
        try:
            report_xml_ids = ir_obj.search(cr, 1, [('report_name', '=', name)])
            if report_xml_ids:
                report_xml = ir_obj.browse(cr, 1, report_xml_ids[0])
            else:
                report_xml = False

            if report_xml and report_xml.preload_mode == 'preload':
                file_data = report_xml.report_sxw_content
                if not file_data:
                    self.logger("template is not defined in %s (%s) !" % (name, table), logging.WARNING)
                    template_io = None
                else:
                    template_io = StringIO()
                    template_io.write(base64.decodestring(file_data))
                    style_io=self.get_styles_file(cr, 1, report_xml)
                if template_io:
                    self.serializer = OOSerializer(template_io, oo_styles=style_io)
        except Exception, e:
            print e

    def getObjects_mod(self, cr, uid, ids, rep_type, context):
        table_obj = pooler.get_pool(cr.dbname).get(self.table)
        if rep_type=='aeroo':
            return table_obj.browse(cr, uid, ids, context=context)
        return table_obj.browse(cr, uid, ids, context=context)

    ##### Counter functions #####
    def _def_inc(self, aeroo_print):
        def def_inc(name, start=0, interval=1):
            aeroo_print.counters[name] = Counter(name, start, interval)
        return def_inc

    def _get_inc(self, aeroo_print):
        def get_inc(name):
            return aeroo_print.counters[name].get_inc()
        return get_inc

    def _prev(self, aeroo_print):
        def prev(name):
            return aeroo_print.counters[name].prev()
        return prev

    def _next(self, aeroo_print):
        def next(name):
            return aeroo_print.counters[name].next()
        return next
    #############################

    def _epl_asimage(self, data, aeroo_print):
        from PIL import Image
        from math import ceil
        if not data:
            return ''
        img = Image.open(StringIO(base64.decodestring(data)))
        if img.format!='BMP':
            return ''
        data = base64.decodestring(data)[62:]
        line_len = int(ceil(img.size[0]/32.0)*4)
        temp_data = ''
        for n in range(img.size[1]):
            curr_pos = n*line_len
            temp_data = data[curr_pos:curr_pos+line_len][:int(img.size[0]/8)] + temp_data

        new_data = ''
        for d in temp_data:
            new_data += chr(ord(d)^255)
        aeroo_print.epl_images.append(new_data)
        return img.size

    def _epl2_gw(self, aeroo_print):
        def epl2_gw(start_x, start_y, data):
            if not data:
                return None
            size_x, size_y = self._epl_asimage(data, aeroo_print)
            return 'GW'+str(start_x)+','+str(start_y)+','+str(int(size_x/8))+','+str(size_y)+',<binary_data>'
        return epl2_gw

    def _include_document(self, print_id, aeroo_ooo=False):
        def include_document(data, silent=False):
            if not aeroo_ooo:
                return _("Error! Include document not available!")
            import binascii, urllib2
            temp_file = NamedTemporaryFile(suffix='.odt', prefix='aeroo-report-', delete=False)
            if os.path.isfile(data):
                fd = file(data, 'rb')
                data = fd.read()
            else:
                error = False
                try:
                    url_file = urllib2.urlopen(data)
                    data = url_file.read()
                except urllib2.HTTPError, e:
                    os.unlink(temp_file.name)
                    error = _('HTTP Error %s! File not found:') % e.getcode() + ' %s' % data
                except urllib2.URLError, e:
                    os.unlink(temp_file.name)
                    error = _('Error!')+' %s' % e
                except IOError, e:
                    os.unlink(temp_file.name)
                    error = _('Error!')+' %s' % e
                except Exception, e:
                    try:
                        data = base64.decodestring(data)
                    except binascii.Error:
                        os.unlink(temp_file.name)
                        error = _('Error! File not found:')+' %s' % data
                if error:
                    if not silent:
                        return error
                    else:
                        return None
            try:
                temp_file.write(data)
            finally:
                temp_file.close()
            #self.oo_subreports[print_id].append(temp_file.name)
            self.active_prints[print_id].subreports.append(temp_file.name)
            return "<insert_doc('%s')>" % temp_file.name
        return include_document

    def _subreport(self, cr, uid, aeroo_print, output='odt', aeroo_ooo=False, context={}):
        pool = pooler.get_pool(cr.dbname)
        ir_obj = pool.get('ir.actions.report.xml')
        #### for odt documents ####
        def odt_subreport(name=None, obj=None):
            if not aeroo_ooo:
                return _("Error! Subreports not available!")
            report_xml_ids = ir_obj.search(cr, uid, [('report_name', '=', name)], context=context)
            if report_xml_ids:
                service = netsvc.Service._services['report.%s' % name]
                report_xml = ir_obj.browse(cr, uid, report_xml_ids[0], context=context)
                data = {'model': obj._table_name, 'id': obj.id, 'report_type': 'aeroo', 'in_format': 'oo-odt'}
                ### Get new printing object ###
                sub_aeroo_print = AerooPrint()
                service.active_prints[sub_aeroo_print.id] = sub_aeroo_print
                context['print_id'] = sub_aeroo_print.id
                ###############################
                sub_aeroo_print.start_time = time.time()
                report, output = service.create_aeroo_report(cr, uid, \
                                            [obj.id], data, report_xml, context=context, output='odt') # change for OpenERP 6.0 - Service class usage

                ### Delete printing object ###
                AerooPrint.print_ids.remove(sub_aeroo_print.id)
                del service.active_prints[sub_aeroo_print.id]
                ##############################
                with NamedTemporaryFile(suffix='.odt', prefix='aeroo-report-', delete=False) as temp_file:
                    temp_file.write(report)

                #self.oo_subreports[print_id].append(temp_file.name)
                aeroo_print.subreports.append(temp_file.name)

                return "<insert_doc('%s')>" % temp_file.name
            return None
        #### for text documents ####
        def raw_subreport(name=None, obj=None):
            report_xml_ids = ir_obj.search(cr, uid, [('report_name', '=', name)], context=context)
            if report_xml_ids:
                report_xml = ir_obj.browse(cr, uid, report_xml_ids[0], context=context)
                data = {'model': obj._table_name, 'id': obj.id, 'report_type': 'aeroo', 'in_format': 'genshi-raw'}
                report, output = netsvc.Service._services['report.%s' % name].create_genshi_raw_report(cr, uid, \
                                            [obj.id], data, report_xml, context=context, output=output) # change for OpenERP 6.0 - Service class usage
                return report
            return None

        if output=='odt':
            return odt_subreport
        elif output=='raw':
            return raw_subreport

    def set_xml_data_fields(self, objects, parser):
        xml_data_fields = parser.localcontext.get('xml_data_fields', False)
        if xml_data_fields:
            for field in xml_data_fields:
                for o in objects:
                    if getattr(o, field):
                        xml_data = base64.decodestring(getattr(o, field))
                        xmldoc = minidom.parseString(xml_data)
                        setattr(o, field, xmldoc.firstChild)
        return objects

    def get_other_template(self, cr, uid, data, parser):
        if hasattr(parser, 'get_template'):
            pool = pooler.get_pool(cr.dbname)
            record = pool.get(data['model']).browse(cr, uid, data['id'], {})
            template = parser.get_template(cr, uid, record)
            return template
        else:
            return False

    def get_styles_file(self, cr, uid, report_xml, company=None, context=None):
        pool = pooler.get_pool(cr.dbname)
        style_io=None
        if report_xml.styles_mode!='default':
            if report_xml.styles_mode=='global':
                company_id = company or pool.get('res.users')._get_company(cr, uid, context=context)
                style_content = pool.get('res.company').browse(cr, uid, company_id, context=context).stylesheet_id
                style_content = style_content and style_content.report_styles or False
            elif report_xml.styles_mode=='specified':
                style_content = report_xml.stylesheet_id
                style_content = style_content and style_content.report_styles or False
            if style_content:
                style_io = StringIO()
                style_io.write(base64.decodestring(style_content))
        return style_io

    def create_genshi_raw_report(self, cr, uid, ids, data, report_xml, context=None, output='raw', tmpl=False):
        def preprocess(data, aeroo_print):
            aeroo_print.epl_images.reverse()
            while aeroo_print.epl_images:
                img = aeroo_print.epl_images.pop()
                data = data.replace('<binary_data>', img, 1)
            return data.replace('\n', '\r\n')

        print_id = context.get('print_id', False)
        aeroo_print = self.active_prints[print_id] # Aeroo print object
        if not aeroo_print.start_time:
            aeroo_print.start_time = time.time()
        if not context:
            context={}
        context = context.copy()
        objects = self.getObjects_mod(cr, uid, ids, report_xml.report_type, context)
        oo_parser = self.parser(cr, uid, self.name2, context=context)
        oo_parser.localcontext.update(context)
        oo_parser.set_context(objects, data, ids, report_xml.report_type)
        self.set_xml_data_fields(oo_parser.objects, oo_parser) # Get/Set XML
        oo_parser.localcontext['data'] = data
        oo_parser.localcontext['user_lang'] = context.get('lang', False)
        if len(objects)>0:
            oo_parser.localcontext['o'] = objects[0]
        xfunc = ExtraFunctions(cr, uid, report_xml.id, oo_parser.localcontext)
        oo_parser.localcontext.update(xfunc.functions)
        file_data = tmpl or self.get_other_template(cr, uid, data, oo_parser) or report_xml.report_sxw_content # Get other Tamplate
        if not file_data or file_data=='False':
            raise osv.except_osv(_('Error!'), _('No template found!'))
        ################################################
        if not file_data:
            self.logger("End process %s (%s), elapsed time: %s" % (self.name, self.table, time.time() - aeroo_print.start_time), logging.INFO) # debug mode
            return False, output

        print_id = context.get('print_id', False)
        aeroo_print = self.active_prints[print_id]

        oo_parser.localcontext['include_subreport'] = self._subreport(cr, uid, aeroo_print, output='raw', aeroo_ooo=False, context=context)
        oo_parser.localcontext['epl2_gw'] = self._epl2_gw(aeroo_print)
        deferred = context.get('deferred_process')
        oo_parser.localcontext['progress_update'] = deferred and deferred.progress_update or (lambda:True)

        aeroo_print.epl_images = []
        basic = NewTextTemplate(source=base64.decodestring(file_data))
        #try:
        if genshi_version<='0.6':
            data = preprocess(basic.generate(**oo_parser.localcontext).render().decode('utf8').encode(report_xml.charset), aeroo_print)
        else:
            data = preprocess(basic.generate(**oo_parser.localcontext).render().encode(report_xml.charset), aeroo_print)
        #except Exception, e:
        #    self.logger(str(e), logging.ERROR)
        #    return False, output

        if report_xml.content_fname:
            output = report_xml.content_fname
        self.logger("End process %s (%s), elapsed time: %s" % (self.name, self.table, time.time() - aeroo_print.start_time), logging.INFO) # debug mode
        return data, output

    def _generate_doc(self, DC, data, report_xml, print_id):
        with aeroo_lock:
            DC.putDocument(data)
            #subreports = self.oo_subreports.get(print_id)
            aeroo_print = self.active_prints.get(print_id, False)
            if aeroo_print:
                DC.insertSubreports(aeroo_print.subreports)
                #self.oo_subreports = []
                #del self.oo_subreports[print_id]
            if report_xml.out_format.code=='oo-dbf':
                data = DC.saveByStream(report_xml.out_format.filter_name, "78")
            else:
                data = DC.saveByStream(report_xml.out_format.filter_name)
            DC.closeDocument()
        return data

    def _raise_exception(self, e, print_id):
        tb_s = reduce(lambda x, y: x+y, traceback.format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback))
        self.logger(_("Report generation error!")+'\n'+tb_s, logging.ERROR)
        #subreports = self.oo_subreports.get(print_id, [])
        aeroo_print = self.active_prints.get(print_id, [])
        if aeroo_print:
            for sub_report in aeroo_print.subreports:
                if os.path.isfile(sub_report):
                    os.unlink(sub_report)
        raise Exception(_("Aeroo Reports: Error while generating the report."), e, str(e), _("For more reference inspect error logs."))

    def create_aeroo_report(self, cr, uid, ids, data, report_xml, context=None, output='odt'):
        """ Returns an aeroo report generated with aeroolib
        """
        pool = pooler.get_pool(cr.dbname)
        if not context:
            context={}
        context = context.copy()
        if self.name=='report.printscreen.list':
            context['model'] = data['model']
            context['ids'] = ids
        
        print_id = context.get('print_id', False)
        aeroo_print = self.active_prints[print_id] # Aeroo print object
        aeroo_print.subreports = []
        #self.oo_subreports[print_id] = []
        objects = self.getObjects_mod(cr, uid, ids, report_xml.report_type, context) or []
        parser = report_xml.get_custom_parser(cr, uid, [report_xml.id], context=context)
        if parser is None:
            oo_parser = self.parser(cr, uid, self.name2, context=context)
        else:
            oo_parser = parser(cr,uid, self.name2, context=context)

        oo_parser.localcontext.update(context)
        oo_parser.set_context(objects, data, ids, report_xml.report_type)

        self.set_xml_data_fields(objects, oo_parser) # Get/Set XML

        oo_parser.localcontext['data'] = data
        oo_parser.localcontext['user_lang'] = context.get('lang', False)
        if len(objects)>0:
            oo_parser.localcontext['o'] = objects[0]
        xfunc = ExtraFunctions(cr, uid, report_xml.id, oo_parser.localcontext)
        oo_parser.localcontext.update(xfunc.functions)

        #company_id = objects and 'company_id' in objects[0]._table._columns.keys() and \
        #                        objects[0].company_id and objects[0].company_id.id or False # for object company usage
        company_id = False
        style_io=self.get_styles_file(cr, uid, report_xml, company=company_id, context=context)

        if report_xml.tml_source in ('file', 'database'):
            if not report_xml.report_sxw_content or report_xml.report_sxw_content=='False':
                raise osv.except_osv(_('Error!'), _('No template found!'))
            file_data = base64.decodestring(report_xml.report_sxw_content)
        else:
            file_data = self.get_other_template(cr, uid, data, oo_parser)
        if not file_data and not report_xml.report_sxw_content:
            self.logger("End process %s (%s), elapsed time: %s" % (self.name, self.table, time.time() - aeroo_print.start_time), logging.INFO) # debug mode
            return False, output
        #elif file_data:
        #    template_io = StringIO()
        #    template_io.write(file_data or report_xml.report_sxw_content)
        #    basic = Template(source=template_io, styles=style_io)
        else:
            if report_xml.preload_mode == 'preload' and hasattr(self, 'serializer'):
                serializer = copy.copy(self.serializer)
                serializer.apply_style(style_io)
                template_io = serializer.template
            else:
                template_io = StringIO()
                template_io.write(file_data or base64.decodestring(report_xml.report_sxw_content) )
                serializer = OOSerializer(template_io, oo_styles=style_io)
            try:
                basic = Template(source=template_io, serializer=serializer)
            except Exception, e:
                self._raise_exception(e, print_id)

        #if not file_data:
        #    return False, output

        #basic = Template(source=template_io, serializer=serializer)

        aeroo_ooo = context.get('aeroo_ooo', False)
        oo_parser.localcontext['include_subreport'] = self._subreport(cr, uid, aeroo_print, output='odt', aeroo_ooo=aeroo_ooo, context=context)
        oo_parser.localcontext['include_document'] = self._include_document(aeroo_ooo, print_id)
        deferred = context.get('deferred_process')
        oo_parser.localcontext['progress_update'] = deferred and deferred.progress_update or (lambda:True)
        ####### Add counter functons to localcontext #######
        oo_parser.localcontext.update({'def_inc':self._def_inc(aeroo_print),
                                      'get_inc':self._get_inc(aeroo_print),
                                      'prev':self._prev(aeroo_print),
                                      'next':self._next(aeroo_print)})

        user_name = pool.get('res.users').browse(cr, uid, uid, {}).name
        model_id = pool.get('ir.model').search(cr, uid, [('model','=',context.get('active_model', data['model']) or data['model'])])[0]
        model_name = pool.get('ir.model').browse(cr, uid, model_id).name

        #basic = Template(source=None, filepath=odt_path)

        basic.Serializer.add_title(model_name)
        basic.Serializer.add_creation_user(user_name)
        module_info = load_information_from_description_file('report_aeroo')
        version = module_info['version']
        basic.Serializer.add_generator_info('Aeroo Lib/%s Aeroo Reports/%s' % (aeroolib.__version__, version))
        basic.Serializer.add_custom_property('Aeroo Reports %s' % version, 'Generator')
        basic.Serializer.add_custom_property('OpenERP %s' % release.version, 'Software')
        basic.Serializer.add_custom_property(module_info['website'], 'URL')
        basic.Serializer.add_creation_date(time.strftime('%Y-%m-%dT%H:%M:%S'))

        # stream filter function for translation
        def _translate_stream(stream):
            for kind, data, pos in stream:
                result = (kind, data, pos)
                if kind == 'TEXT' and len(data) > 3:
                    result = (
                            kind,
                            pool.get('ir.translation')._get_source(
                                cr, uid, report_xml.report_name,
                                report_xml.report_type,
                                oo_parser.localcontext.get('lang',
                                    oo_parser.localcontext['user_lang']),
                                data),
                            pos)
                yield result

        try:
            data = basic.generate(**oo_parser.localcontext)\
                    .filter(_translate_stream)\
                    .render().getvalue()
        except osv.except_osv, e:
            raise
        except Exception, e:
            self._raise_exception(e, print_id)

        ######### OpenOffice extras #########
        if aeroo_ooo:
            from openerp.addons.report_aeroo_ooo import report as rpt
            DC = rpt.OpenOffice_service(cr, 'localhost', 8100)
        else:
            DC = False
        #if (output!=report_xml.in_format[3:] or self.oo_subreports.get(print_id)):
        if output!=report_xml.in_format[3:] or aeroo_print.subreports:
            if aeroo_ooo and DC:
                try:
                    data = self._generate_doc(DC, data, report_xml, print_id)
                except Exception, e:
                    self.logger(_("OpenOffice.org related error!")+'\n'+str(e), logging.ERROR)
                    if DC._restart_ooo():
                        # We try again
                        try:
                            data = self._generate_doc(DC, data, report_xml, print_id)
                        except Exception, e:
                            self.logger(_("OpenOffice.org related error!")+'\n'+str(e), logging.ERROR)
                            if not report_xml.fallback_false:
                                output=report_xml.in_format[3:]
                    elif not report_xml.fallback_false:
                        output=report_xml.in_format[3:]
                    aeroo_print.subreports = []
            else:
                if report_xml.fallback_false:
                    if not aeroo_ooo:
                        raise osv.except_osv(_('OpenOffice.org related error!'), _('Module "report_aeroo_ooo" not installed.'))
                    elif not DC:
                        raise osv.except_osv(_('OpenOffice.org related error!'), _('Can not connect to OpenOffice.org.'))
                else:
                    self.logger(_("PDF generator temporarily offline, please wait a minute"), logging.WARNING)
                    output=report_xml.in_format[3:]
        elif output in ('pdf', 'doc', 'xls'):
            output=report_xml.in_format[3:]
        #####################################

        if report_xml.content_fname:
            output = report_xml.content_fname
        self.logger("End process %s (%s), elapsed time: %s" % (self.name, self.table, time.time() - aeroo_print.start_time), logging.INFO) # debug mode
        return data, output

    # override needed to keep the attachments' storing procedure
    def create_single_pdf(self, cr, uid, ids, data, report_xml, context=None):
        if not context:
            context={}
        if report_xml.report_type == 'aeroo':
            if report_xml.out_format.code.startswith('oo-'):
                output = report_xml.out_format.code[3:]
                return self.create_aeroo_report(cr, uid, ids, data, report_xml, context=context, output=output)
            elif report_xml.out_format.code =='genshi-raw':
                return self.create_genshi_raw_report(cr, uid, ids, data, report_xml, context=context, output='raw')
        logo = None
        context = context.copy()
        title = report_xml.name
        rml = report_xml.report_rml_content
        oo_parser = self.parser(cr, uid, self.name2, context=context)
        objs = self.getObjects_mod(cr, uid, ids, report_xml.report_type, context)
        oo_parser.set_context(objs, data, ids, report_xml.report_type)
        processed_rml = self.preprocess_rml(etree.XML(rml),report_xml.report_type)
        if report_xml.header:
            oo_parser._add_header(processed_rml)
        if oo_parser.logo:
            logo = base64.decodestring(oo_parser.logo)
        create_doc = self.generators[report_xml.report_type]
        pdf = create_doc(etree.tostring(processed_rml),oo_parser.localcontext,logo,title.encode('utf8'))
        return (pdf, report_xml.report_type)

    def create_source_pdf(self, cr, uid, ids, data, report_xml, context=None):
        if not context:
            context={}
        pool = pooler.get_pool(cr.dbname)
        attach = report_xml.attachment
        aeroo_ooo = aeroo_ooo_test(cr) # Detect report_aeroo_ooo module
        context['aeroo_ooo'] = aeroo_ooo
        print_id = context.get('print_id', False)
        aeroo_print = self.active_prints[print_id] # Aeroo print object
        if attach or aeroo_ooo and report_xml.process_sep:
            objs = self.getObjects_mod(cr, uid, ids, report_xml.report_type, context)
            deferred = context.get('deferred_process')
            results = []
            for obj in objs:
                aeroo_print.start_time = time.time()
                if deferred:
                    deferred.progress_update()
                aname = attach and eval(attach, {'object':obj, 'time':time}) or False
                result = False
                if report_xml.attachment_use and aname and context.get('attachment_use', True):
                    #aids = pool.get('ir.attachment').search(cr, uid, [('datas_fname','=',aname+'.pdf'),('res_model','=',self.table),('res_id','=',obj.id)])
                    #if aids:
                    #    brow_rec = pool.get('ir.attachment').browse(cr, uid, aids[0])
                    #    if not brow_rec.datas:
                    #        continue
                    #    d = base64.decodestring(brow_rec.datas)
                    #    results.append((d,'pdf'))
                    #    continue
                    cr.execute("SELECT id, datas_fname FROM ir_attachment WHERE datas_fname ilike %s and res_model=%s and res_id=%s LIMIT 1", (aname+'.%',self.table,obj.id))
                    search_res = cr.dictfetchone()
                    if search_res:
                        brow_rec = pool.get('ir.attachment').browse(cr, uid, search_res['id'])
                        if not brow_rec.datas:
                            continue
                        d = base64.decodestring(brow_rec.datas)
                        extension = search_res['datas_fname'].split('.')[1]
                        results.append((d,extension))
                        continue
                result = self.create_single_pdf(cr, uid, [obj.id], data, report_xml, context)
                if not result:
                    return False
                try:
                    if attach and aname:
                        name = aname+'.'+result[1]
                        datas = base64.encodestring(result[0])
                        ctx = dict(context)
                        ctx.pop('default_type', None)
                        pool.get('ir.attachment').create(cr, uid, {
                            'name': aname,
                            'datas': datas,
                            'datas_fname': name,
                            'res_model': self.table,
                            'res_id': obj.id,
                            'type': 'binary'
                            }, context=ctx
                        )
                        cr.commit()
                except Exception,e:
                    tb_s = reduce(lambda x, y: x+y, traceback.format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback))
                    logger.log(logging.ERROR, str(e))
                results.append(result)
            if results and len(results)==1:
                return results[0]
            if results:
                not_pdf = filter(lambda r: r[1]!='pdf', results)
                if not_pdf:
                    raise osv.except_osv(_('Error!'), _('Unsupported combination of formats!'))
                #if results[0][1]=='pdf':
                output = PdfFileWriter()
                for r in results:
                    reader = PdfFileReader(StringIO(r[0]))
                    for page in range(reader.getNumPages()):
                        output.addPage(reader.getPage(page))
                s = StringIO()
                output.write(s)
                return s.getvalue(), results[0][1]
        return self.create_single_pdf(cr, uid, ids, data, report_xml, context)

    def create_source_odt(self, cr, uid, ids, data, report_xml, context=None):
        if not context:
            context={}
        pool = pooler.get_pool(cr.dbname)
        results = []
        attach = report_xml.attachment
        aeroo_ooo = aeroo_ooo_test(cr) # Detect report_aeroo_ooo module
        context['aeroo_ooo'] = aeroo_ooo
        print_id = context.get('print_id', False)
        aeroo_print = self.active_prints[print_id] # Aeroo print object
        if attach or aeroo_ooo and report_xml.process_sep:
            objs = self.getObjects_mod(cr, uid, ids, report_xml.report_type, context)
            deferred = context.get('deferred_process')
            for obj in objs:
                aeroo_print.start_time = time.time()
                if deferred:
                    deferred.progress_update()
                aname = attach and eval(attach, {'object':obj, 'time':time}) or False
                result = False
                if report_xml.attachment_use and aname and context.get('attachment_use', True):
                    #aids = pool.get('ir.attachment').search(cr, uid, [('datas_fname','=',aname+'.odt'),('res_model','=',self.table),('res_id','=',obj.id)])
                    #if aids:
                    #    brow_rec = pool.get('ir.attachment').browse(cr, uid, aids[0])
                    #    if not brow_rec.datas:
                    #        continue
                    #    d = base64.decodestring(brow_rec.datas)
                    #    results.append((d,'odt'))
                    #    continue
                    cr.execute("SELECT id, datas_fname FROM ir_attachment WHERE datas_fname ilike %s and res_model=%s and res_id=%s LIMIT 1", (aname+'.%',self.table,obj.id))
                    search_res = cr.dictfetchone()
                    if search_res:
                        brow_rec = pool.get('ir.attachment').browse(cr, uid, search_res['id'])
                        if not brow_rec.datas:
                            continue
                        d = base64.decodestring(brow_rec.datas)
                        extension = search_res['datas_fname'].split('.')[1]
                        results.append((d,extension))
                        continue
                result = self.create_single_pdf(cr, uid, [obj.id], data, report_xml, context)
                try:
                    if attach and aname:
                        name = aname+'.'+result[1]
                        datas = base64.encodestring(result[0])
                        ctx = dict(context)
                        ctx.pop('default_type', None)
                        pool.get('ir.attachment').create(cr, uid, {
                            'name': aname,
                            'datas': datas,
                            'datas_fname': name,
                            'res_model': self.table,
                            'res_id': obj.id,
                            'type': 'binary'
                            }, context=ctx
                        )
                        cr.commit()
                except Exception,e:
                     self.logger(_("Create attachment error!")+'\n'+str(e), logging.ERROR)
                results.append(result)

        if aeroo_ooo:
            from openerp.addons.report_aeroo_ooo import report as rpt
            DC = rpt.OpenOffice_service(cr, 'localhost', 8100)
        else:
            DC = False
        if results and len(results)==1:
            return results[0]
        elif results and DC:
            not_odt = filter(lambda r: r[1]!='odt', results)
            if not_odt:
                raise osv.except_osv(_('Error!'), _('Unsupported combination of formats!'))
            results.reverse()
            data = results.pop()
            with aeroo_lock:
                DC.putDocument(data[0])
                DC.joinDocuments([r[0] for r in results])
                result = DC.saveByStream()
                DC.closeDocument()
            return (result, data[1])
        else:
            return self.create_single_pdf(cr, uid, ids, data, report_xml, context)

    # override needed to intercept the call to the proper 'create' method
    def create(self, cr, uid, ids, data, context=None):
        #### Get Aeroo print object ###
        aeroo_print = AerooPrint()
        aeroo_print.start_total_time = time.time()
        aeroo_print.start_time = time.time()
        self.active_prints[aeroo_print.id] = aeroo_print
        context['print_id'] = aeroo_print.id
        ###############################
        self.logger("Start process %s (%s)" % (self.name, self.table), logging.INFO) # debug mode
        pool = pooler.get_pool(cr.dbname)
        if context is None:
            context = {}
        if 'tz' not in context:
            context['tz'] = pool.get('res.users').browse(cr, uid, uid).context_tz

        data.setdefault('model', context.get('active_model',False))
        ir_obj = pool.get('ir.actions.report.xml')
        name = self.name.startswith('report.') and self.name[7:] or self.name
        report_xml_ids = ir_obj.search(cr, uid,
                [('report_name', '=', name)], context=context)
        if report_xml_ids:
            report_xml = ir_obj.browse(cr, uid, report_xml_ids[0], context=context)
            copies = report_xml.copies
            copies_ids = []
            if not report_xml.report_wizard and copies>1:
                while(report_xml.copies):
                    copies_ids.extend(ids)
                    copies -= 1
            ids = copies_ids or ids
        else:
            title = ''
            report_file = tools.file_open(self.tmpl)
            try:
                rml = report_file.read()
                report_type= data.get('report_type', 'pdf')
                class a(object):
                    def __init__(self, *args, **argv):
                        for key,arg in argv.items():
                            setattr(self, key, arg)
                report_xml = a(title=title, report_type=report_type, report_rml_content=rml, \
                            name=title , attachment=False, header=self.header, process_sep=False)
            finally:
                report_file.close()
        report_type = report_xml.report_type
        if report_type in ['sxw','odt']:
            fnct = self.create_source_odt
        elif report_type in ['pdf','raw','txt','html']:
            fnct = self.create_source_pdf
        elif report_type=='html2html':
            fnct = self.create_source_html2html
        elif report_type=='mako2html':
            fnct = self.create_source_mako2html
        elif report_type=='aeroo':
            if report_xml.out_format.code in ['oo-pdf']:
                fnct = self.create_source_pdf
            elif report_xml.out_format.code in ['oo-odt','oo-ods','oo-doc','oo-xls','oo-csv','oo-dbf','genshi-raw']:
                fnct = self.create_source_odt
            else:
                return super(Aeroo_report, self).create(cr, uid, ids, data, context)
        else:
            raise NotImplementedError(_('Unknown report type: %s') % report_type)
        return fnct(cr, uid, ids, data, report_xml, context)

class ReportTypeException(Exception):
    def __init__(self, value):
      self.parameter = value
    def __str__(self):
      return repr(self.parameter)

