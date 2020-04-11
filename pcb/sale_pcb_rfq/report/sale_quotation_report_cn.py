# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import time
import pooler
from odoo.report import report_sxw
from odoo import api, fields, models, _



class sale_quotation_report_pcb_cn(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(sale_quotation_report_pcb_cn, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({'time': time, 
                                  'get_quotation_report_cn':self._get_quotation_report_cn,
                                  })
    
    def _get_quotation_report_cn(self,records,o_id):
        pool = pooler.get_pool(self.cr.dbname)
        rec_ids=[]
        res=[]
        cats = []
        em_mp=' '
        o_id=[o_id,]
        for record in records:
            records = []
            rec_ids.append(record.id)
        rows = self.pool.get('sale.quotation').browse(self.cr, self.uid, o_id,context=self.localcontext)
        for row in rows:
            vals = {'partner_id':row.partner_id and row.partner_id.name or row.lead_id.name,
                    'user_id':row.user_id.name,
                    'name':row.name,}
            val = {'lxr':row.partner_id and row.partner_id.name or row.lead_id.name,
                    'em_mp':row.user_id.name,
                    'em_phone':row.user_id.partner_id.phone,
                    'name':row.name,
                    'quotation_name':row.name,}
            records.append(val)
        return records
report_sxw.report_sxw('report.sale.quotation.report.pcb.cn', 'sale.quotation', 'addons/sale_pcb_rfq/report/sale_quotation_report_cn.rml',parser=sale_quotation_report_pcb_cn,header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
