# -*- coding: utf-8 -*-

from odoo import fields, models, api
image = 'ad_photo'

image_width = 300
image_high = 300

from odoo import tools
import datetime
image_size = (image_width, image_high)

class website_cpo_advertising(models.Model):
    _name = 'cpo_advertising'

    ad_title = fields.Char(string="Title")
    ad_content = fields.Text(string="Advertising content")
    ad_start_time = fields.Datetime(string="Start time")
    ad_end_time = fields.Datetime(string="End time")
    color = fields.Char(string="Color")
    ad_photo = fields.Binary(string="Advertising Picture")
    ad_link = fields.Char(string="Advertising Link")
    ad_now_time = fields.Datetime(string="Advertising Now Time", compute='get_ad_now_time')

    @api.model
    def create(self, vals):
        if image in vals:
            vals.update({image:tools.image_resize_image(vals[image], image_size)})
        return super(website_cpo_advertising, self).create(vals)

    @api.multi
    def write(self, vals):
        if image in vals:
            vals.update({image:tools.image_resize_image(vals[image], image_size)})
        return super(website_cpo_advertising, self).write(vals)

    def get_ad_now_time(self):
        nowTime = datetime.datetime.now()
        # print nowTime
        # print (self.ad_end_time+datetime.timedelta(hours=8))
        self.ad_now_time = nowTime
