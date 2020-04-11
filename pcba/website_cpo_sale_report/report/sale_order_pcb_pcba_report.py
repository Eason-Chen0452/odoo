# -*- coding: utf-8 -*-
from odoo import api, fields, models
import math
from decimal import Decimal
import re

class ReportList(models.AbstractModel):
    _name = 'report.website_cpo_sale_report.sale_cpo_report_templates33'


    @api.multi
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        docs = self.env['sale.order'].browse(docids)
        docargs = {
            'doc_ids': docs.ids,
            'doc_model': 'sale.order',
            'docs': docs,
            'pcb_and_pcba_line': self._set_total(docs),
            'proforma': True,
        }
        # print 123
        return self.env['report'].render('website_cpo_sale_report.sale_cpo_report_templates33', docargs)

    def _set_total(self, docs):
        # print docs
        res = {}
        for doc in docs:
            res['date_order'] = re.search('(\d+\-\d+\-\d+)', doc.date_order).group()
            if doc.order_line:
                res['pcba_quantity'] = int(doc.order_line.product_uom_qty)
                res['pcb_plate_fee'] = Decimal(doc.order_line.pcb_plate_fee).quantize(Decimal('0.00'))
                res['bom_material_fee'] = Decimal(doc.order_line.bom_material_fee).quantize(Decimal('0.00'))
                res['smt_assembly_fee'] = Decimal(doc.order_line.smt_assembly_fee).quantize(Decimal('0.00'))
                res['stencil_fee'] = Decimal(doc.order_line.stencil_fee).quantize(Decimal('0.00'))
                res['bom_material_manage_fee'] = Decimal(doc.order_line.bom_material_manage_fee).quantize(Decimal('0.00'))
                res['etdel'] = Decimal(doc.order_line.etdel).quantize(Decimal('0.00'))

            if doc.quotation_line:
                delivery_hour = int(math.ceil(doc.quotation_line.cpo_delivery_day/24))
                # res['customer_file_name'] = float('%.2f' % doc.quotation_line.customer_file_name)
                res['pcb_quantity'] = int(doc.quotation_line.product_uom_qty)
                res['price_unit'] = Decimal(doc.quotation_line.price_unit).quantize(Decimal('0.00'))
                res['engine_fee'] = Decimal(doc.quotation_line.engine_fee).quantize(Decimal('0.00'))
                res['test_fee'] = Decimal(doc.quotation_line.test_fee).quantize(Decimal('0.00'))
                res['cpo_pcb_frame_fee'] = Decimal(doc.quotation_line.drill_fee).quantize(Decimal('0.00'))
                res['delivery_hour'] = doc.quotation_line.cpo_delivery_day

            res['shipping_fee'] = Decimal(doc.shipping_fee).quantize(Decimal('0.00'))
            res['amount_total'] = Decimal(doc.amount_total).quantize(Decimal('0.00'))
            # res['all_amount_total'] = res['amount_total']+res['shipping_fee']
            res['all_amount_total'] = res['amount_total']

        return res


