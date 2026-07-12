from odoo import models, fields

class AssetFlowDepartment(models.Model):
    _name = 'assetflow.department'
    _description = 'AssetFlow Department'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Department Name', required=True, tracking=True)
    parent_id = fields.Many2one('assetflow.department', string='Parent Department')
    manager_id = fields.Many2one('assetflow.employee', string='Department Head', tracking=True)
    active = fields.Boolean(default=True)
