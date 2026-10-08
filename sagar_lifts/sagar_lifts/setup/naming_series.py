"""Naming series — No-Code Guide Section 6.

Sales Invoice: Proforma Invoice -> PI/NNNN/YY-YY, Tax Invoice -> SL/NNNN/YY-YY,
where YY-YY is the Indian FY of the posting date (.SL_FY. — see
amc_calendar.naming_fy, wired via hooks.naming_series_variables). The series
is picked from Invoice Type automatically (doc_events.sales_invoice_set_naming_series).
The counter sits before the FY part, so numbering continues across years
rather than restarting at 0001 each April. Delivery Note (Challan) -> CH-.####.

Return-document series (SRET-.YY.-, DRET-.YY.-) are kept alongside — the guide
never mentions them, but dropping them would break Sales/Delivery Returns.
"""

import frappe

PROPERTY_SETTERS = [
	{
		"doctype": "Sales Invoice",
		"fieldname": "naming_series",
		"property": "options",
		"value": "PI/.####./.SL_FY.\nSL/.####./.SL_FY.\nSRET-.YY.-",
	},
	{
		"doctype": "Sales Invoice",
		"fieldname": "naming_series",
		"property": "default",
		"value": "PI/.####./.SL_FY.",
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
