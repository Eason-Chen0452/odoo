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
from odoo.report import report_sxw
import pooler
from odoo import api, fields, models, _


class sale_quotation_report_pcb(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(sale_quotation_report_pcb, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({'time': time, 
                                  'get_quotation_report':self._get_quotation_report,
                                  })
    
    def _get_quotation_report(self,records,o_id):
        pool = pooler.get_pool(self.cr.dbname)
        rec_ids=[]
        res=[]
        cats = []
        em_mp=' '
        o_id=[o_id,]
        #print "adfsadsf",o_id,type(o_id)
        for record in records:
            records = []
            rec_ids.append(record.id)
        #print rec_ids
        rows = self.pool.get('sale.quotation').browse(self.cr, self.uid, o_id,context=self.localcontext)
        #cats=pool.get('sale.quotation').read(self.cr, self.uid, o_id, ['partner_id','partner_id','user_id','name'], context=self.localcontext)
        for row in rows:
            vals = {'partner_id':row.partner_id.name,
                    'user_id':row.user_id.name,
                    'name':row.name,}
            val = {'lxr':row.partner_id.name,
                    'em_mp':row.user_id.name,
                    'em_phone':row.user_id.partner_id.phone,
                    'name':row.name,
                    'quotation_name':row.name,}
        #cats.append(vals)
        #print cats[0]['user_id'][1],cats[0]['user_id'][0],cats[0]['user_id']
        #print cats
        #if not cats:
        #    return res   
        #for cat in cats:
        #    rows=pool.get('resource.resource').search(self.cr,self.uid, [('name','=',cats[0]['user_id'][1])], context=self.localcontext)
            #print "1",rows
        #    for row in rows:
                #print row
        #        irows=pool.get('hr.employee').search(self.cr,self.uid, [('resource_id','=',row)], context=self.localcontext)
        #        for irow in irows:
        #            em_mp=pool.get('hr.employee').read(self.cr, self.uid, irow, ['mobile_phone'], context=self.localcontext)['mobile_phone']
        #    lxr=cat['partner_id']#[1].split(',')[0]
        #    partner=pool.get('res.partner').read(self.cr, self.uid, cat['partner_id'][0], ['name'], context=self.localcontext)
        #    name=str(partner['name'])
         #   val = {
         #        'name':name,
         #        'lxr':lxr,
         #        'em_mp':em_mp,
         #        'quotation_name':cat['name'],
         #       }
         #   name=' '
         #   lxr=' '
         #   em_mp=' '
            records.append(val)
        #print records
        return records
report_sxw.report_sxw('report.sale.quotation.report.pcb', 'sale.quotation', 'addons/sale_pcb_rfq/report/sale_quotation_report.rml',parser=sale_quotation_report_pcb,header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: