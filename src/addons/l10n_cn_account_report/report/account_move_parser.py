#encoding: utf-8

from report import report_sxw
from report.report_sxw import rml_parse

class AccountMoveParser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(AccountMoveParser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'hello_world':self.hello_world,
        })

    def hello_world(self, name):
        return "Hello, %s!" % name

