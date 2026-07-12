from odoo import models, fields

class AssetFlowCategory(models.Model):
    _name = 'assetflow.category'
    _description = 'Asset Category'

    name = fields.Char(string='Category Name', required=True)
    description = fields.Text(string='Description')
