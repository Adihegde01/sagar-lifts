"""Naming series — No-Code Guide Section 6.

Sales Invoice: Proforma Invoice -> PI/.####./25-26, Tax Invoice -> SL/.####./25-26
(billing picks the series matching PI Type). Delivery Note (Challan) -> CH-.####.

Return-document series (SRET-.YY.-, DRET-.YY.-) are kept alongside — the guide
never mentions them, but dropping them would break Sales/Delivery Returns.
"""

import frappe

PROPERTY_SETTERS = [
	{
		"doctype": "Sales Invoice",
		"fieldname": "naming_series",
		"property": "options",
		"value": "PI/.####./25-26\nSL/.####./25-26\nSRET-.YY.-",
	},
	{
		"doctype": "Sales Invoice",
		"fieldname": "naming_series",
		"property": "default",
		"value": "PI/.####./25-26",
	},
	{
		"doctype": "Delivery Note",
		"fieldname": "naming_series",
		"property": "options",
		"value": "CH-.####.\nDRET-.YY.-",
	},
	{
		"doctype": "Delivery Note",
		"fieldname": "naming_series",
		"property": "default",
		"value": "CH-.####.",
	},
]


def setup_naming_series():
	for ps in PROPERTY_SETTERS:
		frappe.make_property_setter({**ps, "property_type": "Text"}, is_system_generated=True)
