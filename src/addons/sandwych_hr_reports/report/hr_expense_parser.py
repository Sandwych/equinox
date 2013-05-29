
#encoding: utf-8

from report import report_sxw
from report.report_sxw import rml_parse
import util

class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'rmb_upper': util.rmb_upper,
        })

    def set_context(self, objects, data, ids, report_type=None):
        return super(Parser, self).set_context(objects, data, ids, report_type=report_type)

