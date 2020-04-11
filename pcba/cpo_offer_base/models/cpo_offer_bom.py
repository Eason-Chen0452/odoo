# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo import _
import xlrd
import xlwt
import base64
import re
from .cpo_inherit_sale_order import CPO_BOM_SUPPLY_SELECT,BOM_SELECTION_STATE

def get_digi_data(vals, type=int):
    if type == int:
        data = re.search('\d*', vals)
    elif type == float:
        data = re.search('(\d*).(\d*)', vals)
    if data:# and str(type(data.group(0))) == vals:
        return type(data.group())
    else:
        return 0

def get_list_count_item(l, i):
    return len(l)-len([x for x in l if x!=i])

def recheck_bom_file_content(rows):
    rows2 = []
    rows = [x for x in rows if list(set(x))!=['']]
    rows_len_list = [len(list(set(x))) for x in rows]
    rows_len_list_only = list(set(rows_len_list))
    row_dict = {}
    for row in rows_len_list_only:
        row_dict[row] = get_list_count_item(rows_len_list, row)
    header_len = [x[0] for x in row_dict.items() if x[1]==max(row_dict.values())][0]
    #rows = [x for x in rows if len([i for i in x if ''!=i]) == header_len]
    rows = [x for x in rows if len([i for i in x if ''!=i]) >= 2]
    rows_check = [x.encode('utf-8') if type(x) == unicode else x for x in rows[0]]
    if len([x for x in list(set(rows_check)-set([''])) if not re.search('^\d+.?\d?$',str(x))]) != len(list(set(rows_check)-set(['']))):
        for row in range(len(rows[0])):
            rows2.append('item_0'+str(row+1))
    return [rows2]+rows if rows2 else rows

class cpo_offer_bom(models.Model):
    _name = 'cpo_offer_bom.bom'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'


    bom_supply_line = fields.One2many('cpo_bom_supply.list_for_bom', 'bom_id', string="BOM Supply")
    bom_fields_line = fields.One2many("cpo_bom_fields.line_for_bom", 'bom_id', string="BOM Fields Ref")
    bom_express_line = fields.One2many("express_waybill.line_for_bom", 'bom_id', string="Express Line")

    smt_component_qty = fields.Integer(string="SMT Component Quantity")
    smt_plug_qty = fields.Integer(string="Plug-in Pin quantity")

    cpo_smt_assembly_fee = fields.Float(string="CPO SMT Assembly fee")
    cpo_test_tool_fee = fields.Float(string="CPO Test Tool fee")
    cpo_jig_tool_fee = fields.Float(string="CPO Jig Tool fee")
    cpo_stencil_fee = fields.Float(string="CPO Stencil fee")
    #smt_component_qty = fields.Integer(related='order_ids.smt_component_qty', string="SMT Component Quantity")
    #smt_plug_qty = fields.Integer(related='order_ids.smt_plug_qty', string="Plug-in Pin quantity")

    #cpo_smt_assembly_fee = fields.Float(related='order_ids.cpo_smt_assembly_fee', string="CPO SMT Assembly fee")
    #cpo_test_tool_fee = fields.Float(related='order_ids.cpo_test_tool_fee', string="CPO Test Tool fee")
    #cpo_jig_tool_fee = fields.Float(related='order_ids.cpo_jig_tool_fee', string="CPO Jig Tool fee")
    #cpo_stencil_fee = fields.Float(related='order_ids.cpo_stencil_fee', string="CPO Stencil fee")
    partner_id = fields.Many2one("res.partner", string='Partner')
    bom_file_name = fields.Char(string="Bom File Name")
    pcs_number = fields.Integer("PCS Number", default=1)

    name = fields.Char(string="Bom number", readonly=True, index=True)
    bom_file = fields.Binary(string="Bom File", attachment=True)
    smt_file = fields.Binary(string="SMT File", attachment=True)
    pcb_file = fields.Binary(string="Gerber File", attachment=True)
    product_pro = fields.Many2one('product.product', string="Product", domain="[('name', '=', 'BOM')]", index=True)
    base_table_bom = fields.One2many('cpo_offer_bom.bom_line', 'base_table_bom_id', string="Bom")
    bom_prices = fields.Float(string="Total Price")
    state = fields.Selection(BOM_SELECTION_STATE, default='draft', string="Status")
    force_import = fields.Boolean("Force Import")
    order_ids = fields.One2many("sale.order.line", 'bom_rootfile', "Order IDS")

    #@api.constrains('order_ids')
    #def _check_order_ids(self):
    #    if not self.order_ids:
    #        return True
    #    res = self.search([('order_ids', 'in', self.order_ids.mapped("id"))])
    #    if len(res) > 1:
    #        raise ValidationError("Bom File to order line fond repeat.")

    #返回nam字段和product_pro
    @api.multi
    @api.depends('name', 'product_pro')
    def name_get(self):
        return [(r.id, (r.name +'(' + (r.product_pro.name or _('Default'))+')' )) for r in self]

    @api.model
    def create(self, valus):
        #a=1
        if not valus.get('name'):
            valus['name'] = self.env['ir.sequence'].next_by_code('cpo_offer_bom.bom')
        res = super(cpo_offer_bom, self).create(valus)
        res.go_update_data_to_saleorder()
        if len(res.order_ids) > 1:
            raise ValidationError(_("One Bom relate to One Order, but find many bom to order"))
        return res

    @api.multi
    def write(self, vals):
        res = super(cpo_offer_bom, self).write(vals)
        self.go_update_data_to_saleorder()
        if 'state' in vals.keys():
            for row in self:
                if row.order_ids:
                    row.sudo().order_ids.order_id.bom_state = vals.get('state')
        if 'base_table_bom' in vals.keys() and not self.env.context.get('from_write_to_update_total'):
            self.with_context({'from_write_to_update_total':True}).to_calc_total()
        return res

    @api.multi
    def go_update_data_to_saleorder(self):
        for row in self.filtered(lambda x:x.order_ids):
            vals = {
                'cpo_smt_assembly_fee' : row.cpo_smt_assembly_fee,
                'cpo_test_tool_fee' : row.cpo_test_tool_fee,
                'cpo_jig_tool_fee' : row.cpo_jig_tool_fee,
                'cpo_stencil_fee' : row.cpo_stencil_fee
            }
            if row.smt_component_qty > 0:
                vals.update({
                    'smt_component_qty' : row.smt_component_qty,
                })
            if row.smt_plug_qty > 0:
                vals.update({
                    'smt_plug_qty' : row.smt_plug_qty,
                })
            row.order_ids.only_pcba_order_line().write(vals)

    def create_atta_for_new_bom(self,partner_id, tag_val, name, datas):
        atta_pool = self.env['ir.attachment'].sudo()
        #has_atta = atta_pool.search([('datas','=',datas),('name','=',name),('res_id', '=', order_id),('res_model', '=', 'sale.order')])
        error = ''
        #if has_atta:
        #    if has_atta.description != tag_val:
        #        has_atta.description = tag_val
        #    else:
        #        error = 'already has atta file'
        #else:
        if name and name[-4:].lower() == '.xls':
            bom_file_name = name[:-4]
        elif name and name[-5:].lower() == '.xlsx':
            bom_file_name = name[:-5]
        else:
            bom_file_name = name
        bom_id = self.create({'partner_id':partner_id, 'bom_file_name': bom_file_name})
        vals = {
            'name':name,
            'description':tag_val,
            'res_model':'cpo_offer_bom.bom',
            'type': 'binary',
            'public': True,
            'datas':datas,
            'res_id':bom_id,
            'datas_fname':name,
        }
        #self.sudo().write({'bom_fields_line': [(2,x.id) for x in self.bom_fields_line]})
        #pcba_order_line = [x for x in self.order_line.sudo() if x.product_id.name == 'PCBA']
        #if tag_val == 'BOM File' and pcba_order_line:
        #    if name and name[-4:].lower() == '.xls':
        #        bom_file_name = name[:-4]
        #    elif name and name[-5:].lower() == '.xlsx':
        #        bom_file_name = name[:-5]
        #    else:
        #        bom_file_name = name
        #    pcba_order_line[0].write({'bom_file_name': bom_file_name})
        atta_id = atta_pool.create(vals)
        return {'atta_id':atta_id.id, 'error': error}

    @api.multi
    def to_auto_import_date(self):
        bom_head_dict = dict([(x.src_title, x.cpo_title) for x in self.bom_fields_line if x.cpo_title])
        #bom_head_dict = dict([(x.original_col, x.new_table_head) for x in self.cpo_title if x.new_table_head])
        self.force_import = True
        self.do_importing(bom_head_dict=bom_head_dict)

    #创建上传文件除表头之外的内容
    @api.multi
    def do_importing(self, bom_head_dict) :
        for row in self:
            bom_file = False
            if row.bom_file :
                bom_file =  row.bom_file
            else:
                atta_pool = self.env['ir.attachment']
                atta_row = atta_pool.search([
                    ('res_id', '=', self.id),
                    ('res_model', '=', 'cpo_offer_bom.bom'),
                    ('description', '=', 'BOM File')
                ])
                if atta_row:
                    bom_file = atta_row.datas
            if not bom_file:
                return False
            workbook = xlrd.open_workbook(file_contents=base64.decodestring(bom_file))
            #bom_wizard = row.env['cpo_bom_wizard.wizard'].search([('id', '=', wizard_id)])
            #if not bom_wizard:
                #return False
            if len(workbook._sheet_list) >= 1 :
                row.base_table_bom.unlink()
                workbook_content = workbook.sheet_by_index(0)
                #row_head = bom_wizard.cpo_title.search([('basedata_id', '=', bom_wizard[len(bom_wizard)-1].id)])
                #bom_line_count = int(row.base_table_bom.search_count([('base_table_bom_id', '=', row.id)]))
                #bom_data = {}
                #for zz in row_head :
                    #if zz.new_table_head :
                #        bom_data.update({zz.original_col : zz.new_table_head})
                bom_data = bom_head_dict

                #for x_row in range(1,workbook_content.nrows):
                #    bom_row_data = {}
                #    #if x_row == bom_line_count :
                #        #raise ValidationError(_("Bom data already exists, cannot repeat import!"))
                #    #else:
                #    for y_col in range(workbook_content.ncols) :
                #        tabel_head_d = workbook_content.cell(0,y_col).value
                #        if tabel_head_d in bom_data.keys():
                #            cell_head = workbook_content.cell(x_row,y_col).value
                #            if bom_data.get(tabel_head_d) in ['cpo_item', 'cpo_qty'] and type(cell_head) not in [float, int]:
                #                if not row.force_import:
                #                    raise ValidationError("Find File Data Error,Please check {row} row, {col} col of file.".format(row=x_row,col=y_col))
                #                continue
                #            bom_row_data.update({bom_data.get(tabel_head_d):cell_head})

                #            #update supply to bom line
                #            bom_supply = 'chinapcbone'
                #            if bom_data.get(tabel_head_d) == 'cpo_mfr_p_n':
                #                supply_val = [x.supply for x in row.order_ids.order_id.bom_supply_line if x.mfr == cell_head]
                #                if supply_val:
                #                    bom_supply = supply_val[0]
                #            bom_row_data.update({'bom_supply':bom_supply})

                #    row.write({'base_table_bom' : [(0,0,bom_row_data)]})
                ce_rows = []
                for x_row in range(0,workbook_content.nrows):
                    i_row = []
                    for y_col in range(workbook_content.ncols):
                        i_row.append(workbook_content.cell(x_row,y_col).value)
                    ce_rows.append(i_row)
                rows = recheck_bom_file_content(ce_rows)
                res=[]
                excel_title = [x.strip() for x in rows[0]]
                for x_row in rows[1:]:
                    bom_row_data = {}
                    #bom_row_data.update({'bom_supply':'chinapcbone'})
                    bom_supply = 'chinapcbone'
                    for src_title,cpo_title in bom_head_dict.items():
                        t_index = excel_title.index(src_title)
                        if cpo_title in ['cpo_item', 'cpo_qty'] and type(x_row[t_index]) not in [float, int]:
                            if not row.force_import:
                                raise ValidationError("Find File Data Error,Please check {row} row, {col} col of file.".format(row=x_row,col=y_col))
                            continue
                        bom_row_data.update({cpo_title:x_row[t_index]})
                        if cpo_title == 'cpo_mfr_p_n':
                            bom_supply_line = []
                            if row.bom_supply_line:
                                bom_supply_line = row.bom_supply_line
                            elif row.order_ids:
                                bom_supply_line = row.order_ids.order_id.bom_supply_line
                            supply_val = [x.supply for x in bom_supply_line if x.mfr == x_row[t_index]]
                            if supply_val:
                                bom_supply = supply_val[0]
                    bom_row_data.update({'bom_supply':bom_supply})
                    res.append((0,0,bom_row_data))
                row.write({'base_table_bom' : res})
        return True

    def matched_data_d(self):
        for row in self:
            row.base_table_bom.matched_data()
            total_prices = sum(row.base_table_bom.filtered(lambda x:x.bom_supply!='customer').mapped("total"))
            #新增总数量
            #qty_total = sum(row.base_table_bom.filtered(lambda x: x.bom_supply != 'customer').mapped("cpo_qty"))
            for order_id in row.order_ids:
                order_id.bom_material_price = total_prices
                order_id.bom_material_fee = total_prices * order_id.product_uom_qty
                order_id.buttton_check_pcba_data()
            row.bom_prices = total_prices
            #row.smt_component_qty = qty_total #重新赋值
        return True

    @api.multi
    def to_calc_total(self):
        for row in self:
            row.base_table_bom.calc_bom_line_total()
            row.bom_prices = sum([x.total for x in row.base_table_bom.filtered(lambda x:x.bom_supply!='customer')])
            #计算总数
            #row.smt_component_qty = sum([x.cpo_qty for x in row.base_table_bom.filtered(lambda x:x.bom_supply!='customer')])
            for order_id in row.order_ids:
                order_id.bom_material_price = row.bom_prices
                order_id.bom_material_fee = row.bom_prices * order_id.product_uom_qty

    def do_complete(self):
        if self.state == 'check' :
            self.state = 'complete'
        return True




class cpo_offer_bom_line(models.Model):
    _name = 'cpo_offer_bom.bom_line'

    @api.depends('base_table_bom_id', 'cpo_qty')
    def _get_require_qty(self):
        for row in self:
            pcs_number = row.base_table_bom_id.pcs_number if row.base_table_bom_id.pcs_number else 1
            row.require_qty = row.cpo_qty * pcs_number

    base_table_bom_id = fields.Many2one('cpo_offer_bom.bom', string="table bom", required=True, ondelete='cascade', index=True, copy=False)

    CHECK_STATE_SELECTION = [('true1', 'TRUE'),('flase0','FLASE'),('lack', 'Lack')]

    name = fields.Char(string="CPO number")
    cpo_item = fields.Integer(string="Item")
    cpo_qty = fields.Integer(string="QTY/PCS")
    require_qty = fields.Integer(string="Require Quantity", compute=_get_require_qty)
    cpo_p_n = fields.Char(string="P/N")
    #cpo_type = fields.Char(string="Type")
    #cpo_title = fields.Char(string="Title")
    #cpo_detail = fields.Char(string="Detail")
    #cpo_reference = fields.Char(string="Reference(m)")
    #cpo_vendor = fields.Char(string="Vendor")
    cpo_vendor_p_n = fields.Char(string="Vendor P/N")
    #cpo_vendor_desc = fields.Char(string="VendorDesc")
    cpo_mfr = fields.Char(string="Manufacturer")
    cpo_mfr_p_n = fields.Char(string="Manufacturer P/N")
    cpo_package = fields.Char(string="Packaging")
    check_state = fields.Selection(CHECK_STATE_SELECTION, default="true1", string="Status")
    state = fields.Selection(BOM_SELECTION_STATE, related="base_table_bom_id.state", store=False, default='check')
    price = fields.Float(string="Unit Price")
    total = fields.Float(string="Total")
    cpo_description = fields.Char(string="Description")
    cpo_replace_p_n = fields.Char(string="Replace P/N")
    cpo_remark = fields.Char(string="Remark")


    #BOM_SUPPLY_SELECTION = [('factory_supply', 'Factory Supply'), ('partner_supply', 'Partner_Supply'),('other', 'Other')]
    bom_supply = fields.Selection(CPO_BOM_SUPPLY_SELECT, string='Bom Supply')

    @api.multi
    def calc_bom_line_total(self):
        for row in self:
            row.total = row.price * row.cpo_qty
        return True

    def matched_data(self):
        type_name = None
        bom_fee = 0
        last_data = 0
        for this in self :
            if this.bom_supply == 'customer':
                continue
            if this.cpo_mfr_p_n :
                #mfr_p_n = self.env['electron.disk_center'].get_ele_data(type_name, this.cpo_mfr_p_n)
                mfr_p_n = self.env['electron.disk_center'].get_product_price(this.cpo_mfr_p_n)
                price_p_n = mfr_p_n.get('price')
                package = mfr_p_n.get('package')

                this.check_state = 'true1'
                this.price = price_p_n
                if package:
                    this.cpo_package = package
                this.total = this.cpo_qty * price_p_n
                bom_fee += this.total
                #for i in mfr_p_n:
                #    i = i[0]

                #    this.check_state = 'true1'
                #    this.price = i.price
                #    this.total = this.cpo_qty * get_digi_data(i.price, float)
                #    bom_fee += this.total
                if not mfr_p_n :
                    this.check_state = 'flase0'
            else :
                this.check_state = "lack"
            #last_data += 1
        return True

    #bom search select
    @api.multi
    def workflow_check_bom(self):
        ele_disk = self.env['electron.disk_center']
        bom_description = self.cpo_description
        mfr_p_n = self.cpo_mfr_p_n
        cpo_bom_line_id = self.id
        bom_search = False
        #if mfr_p_n:
        #    bom_search = ele_disk.do_search_origin_data(search=mfr_p_n)
        #if not bom_search and bom_description:
        #    bom_search = ele_disk.do_search_origin_data(search=bom_description)

        # temp_bom_wizard = self.env["cpo_offer_bom.cpo_multi_ele_wizard"]
        # for search_line in bom_search:
        #     search_line_result = self.env['electron.origin_data'].search([('id', '=', search_line)])
            # temp_bom_wizard.create({
            #     "cpo_manuf": search_line_result.manufacture,
            #     "cpo_manuf_pn": search_line_result.dash_number,
            #     "cpo_price": search_line_result.price,
            #     "cpo_bom_descriprion": search_line_result.description,
            #     "cpo_bom_line_id": cpo_bom_line_id,
            # })

        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'cpo_offer_bom.cpo_multi_ele_wizard',
            # 'views':  [(self.env.ref('cpo_offer_bom.cpo_offer_bom_wizard_form').id, 'form')],
            # 'view_id': 'cpo_offer_bom.cpo_offer_bom_wizard_form',
            'target': 'new',
        }




