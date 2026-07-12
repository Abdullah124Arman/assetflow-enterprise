from odoo import models, fields, api

class AssetFlowEmployee(models.Model):
    _name = 'assetflow.employee'
    _description = 'AssetFlow Employee Directory'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, tracking=True)
    user_id = fields.Many2one('res.users', string='Related User', required=True, ondelete='cascade')
    email = fields.Char(string='Email', related='user_id.email', store=True)
    department_id = fields.Many2one('assetflow.department', string='Department', tracking=True)
    active = fields.Boolean(default=True)
    
    role = fields.Selection([
        ('employee', 'Employee'),
        ('department_head', 'Department Head'),
        ('asset_manager', 'Asset Manager'),
        ('admin', 'Admin')
    ], string='System Role', default='employee', required=True, tracking=True)
