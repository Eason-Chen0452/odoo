# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import datetime


# 主表 - 打包价价格表 - 往后预留接口 可以给指定客户指定打包价价格表
class Package_Price(models.Model):
    _name = 'package.price.main'
    _description = 'PCB Package Price List'
    _order = 'id'

    name = fields.Char('Package Price List Name', size=64, required=True, translate=True, default='/')
    bale_partner_id = fields.Many2one('res.partner', 'Partner', change_default=False, index=True)
    bale_general_bool = fields.Boolean('General Price List', default=False)
    bale_currency_id = fields.Many2one('res.currency', 'Currency')
    bale_start = fields.Date('Start Date', default=fields.Datetime.now, required=True)
    bale_end = fields.Date('End Date', required=True, default=(datetime.today() + relativedelta(weekday=0, days=0, months=12)).strftime('%Y-%m-%d'))
    active = fields.Boolean('Active', help="If unchecked, it will allow you to hide the pricelist without removing it.", default=True)
    memo = fields.Text('Memo')
    bale_area_id = fields.One2many('pp.area', 'main_id', 'Specification Size Area')

    @api.onchange('bale_general_bool')
    def _check_package_price(self):
        if self.bale_general_bool:
            package_price_id = self.search([('bale_general_bool', '=', True)])
            if len(package_price_id) >= 1:
                self.bale_general_bool = False
                return {
                    'warning': {
                        'title': _("Incorrect 'General Price List' value"),
                        'message': _('The general package price list already exists and cannot be created')
                    }
                }

    @api.onchange('bale_partner_id')
    def _get_currency(self):
        if self.bale_partner_id:
            return self.update({'bale_currency_id': self.bale_partner_id.currency_id.ids[0]})


# 平米面积
class Package_Price_Area(models.Model):
    _name = 'pp.area'
    _description = 'Specification Size Area'
    _order = 'area_min'

    main_id = fields.Many2one('package.price.main', 'PCB Package Price List', required=True, index=True, ondelete='cascade')
    area_min = fields.Float('Minimum Area', digits=(16, 6), default=0.0, required=True)
    area_max = fields.Float('Maximum Area', digits=(16, 6), default=0.0, required=True)
    area_size = fields.Float('Area Size', digits=(16, 2), default=0.0, required=True)
    area_quantity = fields.Integer('Quantity', default=0.0, required=True)
    text_id = fields.One2many('pp.text.color', 'area_id', 'Text Color')
    solder_id = fields.One2many('pp.solder.mask.color', 'area_id', 'Solder Mask Color')
    spacing_id = fields.One2many('pp.line.width.spacing', 'area_id', 'Line Width Spacing')
    aperture_id = fields.One2many('pp.aperture', 'area_id', 'Aperture')
    layer_id = fields.One2many('pp.layer.number', 'area_id', 'Number of Layers')
    surface_id = fields.One2many('pp.surface.treatment', 'area_id', 'Surface Treatment')


# 表面处理
class Package_Price_Surface_Treatment(models.Model):
    _name = 'pp.surface.treatment'
    _description = 'Surface Treatment'
    _order = 'id'

    area_id = fields.Many2one('pp.area', 'Specification Size Area', required=True, index=True, ondelete='cascade')
    surface_id = fields.Many2one('cam.surface.process', 'Surface Process')
    thick_gold = fields.Float('Thickness Gold', default=0)
    price = fields.Float('Price', required=True, digits=(16, 2), default=0.0)
    add_delivery = fields.Integer('Increase delivery time', default=0)


# 层数
class Package_Price_Layer_Number(models.Model):
    _name = 'pp.layer.number'
    _description = 'Number of Layers'
    _order = 'id'

    area_id = fields.Many2one('pp.area', 'Specification Size Area', required=True, index=True, ondelete='cascade')
    layer_number_id = fields.Many2one('cam.layer.number', 'Layer Number', required=True, index=True)
    delivery = fields.Integer('Delivery period', default=0)
    density = fields.Float('Hole density', digits=(16, 2), default=0.0)  # 孔密度
    inner_line = fields.Float('Inner hole to line', digits=(16, 2), default=0.0)
    substrate_id = fields.One2many('pp.substrate', 'ln_id', "Substrate")
    thickness_id = fields.One2many('pp.thickness', 'ln_id', 'Thickness')
    outer_copper_id = fields.One2many('pp.outer.copper', 'ln_id', 'Outer Copper')
    inner_copper_id = fields.One2many('pp.inner.copper', 'ln_id', 'Inner Copper')


# 基材
class Package_Price_Substrate(models.Model):
    _name = 'pp.substrate'
    _description = 'Substrate'
    _order = 'id'

    ln_id = fields.Many2one('pp.layer.number', 'Number of Layers', required=True, index=True, ondelete='cascade')
    base_type = fields.Many2one('cam.base.type', 'Copper Base Tye', index=True)
    price = fields.Float('Price', required=True, digits=(16, 2), default=0.0)


# 板厚
class Package_Price_Thickness(models.Model):
    _name = 'pp.thickness'
    _description = 'Thickness'
    _order = 'min_thick,max_thick'

    ln_id = fields.Many2one('pp.layer.number', 'Number of Layers', required=True, index=True, ondelete='cascade')
    min_thick = fields.Float('Minimum thickness', digits=(16, 2), default=0.0)
    max_thick = fields.Float('Maximum thickness', digits=(16, 2), default=0.0)
    price = fields.Float('Price', required=True, digits=(16, 2), default=0.0)
    add_delivery = fields.Integer('Increase delivery time', default=0)


# 外铜厚
class Package_Price_Outer_Copper(models.Model):
    _name = 'pp.outer.copper'
    _description = 'Outer Copper'
    _order = 'outer'

    ln_id = fields.Many2one('pp.layer.number', 'Number of Layers', required=True, index=True, ondelete='cascade')
    outer = fields.Float('Outer copper thickness', digits=(16, 2), default=0.0)
    price = fields.Float('Price', required=True, digits=(16, 2), default=0.0)
    add_delivery = fields.Integer('Increase delivery time', default=0)


# 内铜厚
class Package_Price_Inner_Copper(models.Model):
    _name = 'pp.inner.copper'
    _description = 'Inner Copper'
    _order = 'inner'

    ln_id = fields.Many2one('pp.layer.number', 'Number of Layers', required=True, index=True, ondelete='cascade')
    inner = fields.Float('Inner copper thickness', digits=(16, 2), default=0.0)
    price = fields.Float('Price', required=True, digits=(16, 2), default=0.0)
    add_delivery = fields.Integer('Increase delivery time', default=0)


# 文字颜色
class Package_Price_Text_Color(models.Model):
    _name = 'pp.text.color'
    _description = 'Text Color'
    _order = 'id'

    area_id = fields.Many2one('pp.area', 'Specification Size Area', required=True, index=True, ondelete='cascade')
    ink_color_id = fields.Many2one('cam.ink.color', 'Text Color')
    price = fields.Float('Price', required=True, digits=(16, 2), default=0.0)
    add_delivery = fields.Integer('Increase delivery time', default=0)


# 阻焊颜色
class Package_Price_solder_mask_color(models.Model):
    _name = 'pp.solder.mask.color'
    _description = 'Solder Mask Color'
    _order = 'id'

    area_id = fields.Many2one('pp.area', 'Specification Size Area', required=True, index=True, ondelete='cascade')
    ink_color_id = fields.Many2one('cam.ink.color', 'Solder Mask Color')
    price = fields.Float('Price', required=True, digits=(16, 2), default=0.0)
    add_delivery = fields.Integer('Increase delivery time', default=0)


# 线宽线距
class Package_Price_Line_Width_Spacing(models.Model):
    _name = 'pp.line.width.spacing'
    _description = 'Line Width Spacing'
    _order = 'id'

    area_id = fields.Many2one('pp.area', 'Specification Size Area', required=True, index=True, ondelete='cascade')
    lws_min = fields.Float('Minimum line width', digits=(16, 2), default=0.0)
    lws_max = fields.Float('Maximum line width', digits=(16, 2), default=0.0)
    price = fields.Float('Price', required=True, digits=(16, 2), default=0.0)


# 孔径
class Package_Price_Aperture(models.Model):
    _name = 'pp.aperture'
    _description = 'Aperture'
    _order = 'id'

    area_id = fields.Many2one('pp.area', 'Specification Size Area', required=True, index=True, ondelete='cascade')
    aperture_min = fields.Float('Minimum Aperture', digits=(16, 2), default=0.0)
    aperture_max = fields.Float('Maximum Aperture', digits=(16, 2), default=0.0)
    price = fields.Float('Price', required=True, digits=(16, 2), default=0.0)







