# Copyright 2012 - Now Savoir-faire Linux <https://www.savoirfairelinux.com/>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models


class KPIThreshold(models.Model):
    """KPI Threshold."""

    _name = "kpi.threshold"
    _description = "KPI Threshold"

    def _compute_is_valid_threshold(self):
        for obj in self:
            # check if ranges overlap
            # TODO: This code can be done better
            obj.valid = True
            for range1 in obj.range_ids:
                if not range1.valid:
                    obj.valid = False
                    break
                for range2 in obj.range_ids - range1:
                    if (
                        range1.max_value >= range2.min_value
                        and range1.min_value <= range2.max_value
                    ):
                        obj.valid = False
                        break
            if obj.valid:
                obj.invalid_message = None
            else:
                obj.invalid_message = (
                    "Some ranges are invalid or overlapping. "
                    "Please make sure your ranges do not overlap."
                )

    name = fields.Char(required=True)
    range_ids = fields.Many2many(
        "kpi.threshold.range",
        "kpi_threshold_range_rel",
        "threshold_id",
        "range_id",
        "Ranges",
    )
    valid = fields.Boolean(
        required=True,
        compute="_compute_is_valid_threshold",
        default=True,
    )
    invalid_message = fields.Char(
        string="Message", size=100, compute="_compute_is_valid_threshold"
    )
    kpi_ids = fields.One2many("kpi", "threshold_id", "KPIs")
    company_id = fields.Many2one(
        "res.company", "Company", default=lambda self: self.env.company
    )

    @api.model
    def create(self, data):
        # check if ranges overlap
        # TODO: This code can be done better
        range_obj1 = self.env["kpi.threshold.range"]
        range_obj2 = self.env["kpi.threshold.range"]
        if data.get("range_ids"):
            for range1 in data["range_ids"]:
                range_obj1 = range_obj1.browse(range1[1])
                for range2 in data["range_ids"]:
                    range_obj2 = range_obj2.browse(range2[1])

                    if (
                        range_obj1.valid
                        and range_obj2.valid
                        and range_obj1.min_value < range_obj2.min_value
                    ):
                        if range_obj1.max_value > range_obj2.min_value:
                            raise exceptions.Warning(
                                _("Two of your ranges are overlapping."),
                                _("Make sure your ranges do not overlap!"),
                            )
                    range_obj2 = self.env["kpi.threshold.range"]
                range_obj1 = self.env["kpi.threshold.range"]
        return super().create(data)

    def get_color(self, kpi_value):
        color = "#FFFFFF"
        for obj in self:
            for range_obj in obj.range_ids:
                if (
                    range_obj.min_value <= kpi_value <= range_obj.max_value
                    and range_obj.valid
                ):
                    color = range_obj.color
        return color
