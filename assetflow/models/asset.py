from odoo import models, fields, api

class AssetFlowAsset(models.Model):
    _name = 'assetflow.asset'
    _description = 'Physical Asset / Shared Resource'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Asset Name', required=True, tracking=True)
    asset_tag = fields.Char(string='Asset Tag', required=True, copy=False, readonly=True, default=lambda self: 'New')
    category_id = fields.Many2one('assetflow.category', string='Category', required=True)
    serial_number = fields.Char(string='Serial Number', tracking=True)
    
    acquisition_date = fields.Date(string='Acquisition Date')
    acquisition_cost = fields.Float(string='Acquisition Cost')
    
    condition = fields.Selection([
        ('excellent', 'Excellent / New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor (Needs Attention)')
    ], string='Condition', default='excellent', tracking=True)
    
    location = fields.Char(string='Location', tracking=True)
    is_shared_resource = fields.Boolean(string='Shared / Bookable Resource', default=False)
    
    status = fields.Selection([
        ('available', 'Available'),
        ('allocated', 'Allocated'),
        ('reserved', 'Reserved'),
        ('maintenance', 'Under Maintenance'),
        ('lost', 'Lost'),
        ('retired', 'Retired'),
        ('disposed', 'Disposed')
    ], string='Lifecycle Status', default='available', tracking=True)
    
    current_employee_id = fields.Many2one('assetflow.employee', string='Allocated To (Employee)', tracking=True)
    current_department_id = fields.Many2one('assetflow.department', string='Allocated To (Department)', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('asset_tag', 'New') == 'New':
            vals['asset_tag'] = self.env['ir.sequence'].next_by_code('assetflow.asset') or 'AF-0001'
        return super(AssetFlowAsset, self).create(vals)
