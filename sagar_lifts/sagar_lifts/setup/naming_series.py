"""Naming series — No-Code Guide Section 6.

Sales Invoice: Proforma Invoice -> PI/NNN/YY-YY, Tax Invoice -> SL/NNN/YY-YY
(3-digit like the issued PI/911/26-27 and SL/238/26-27, grows past 999),
where YY-YY is the Indian FY of the posting date (.SL_FY. — see
amc_calendar.naming_fy, wired via hooks.naming_series_variables). The series
is picked from Invoice Type automatically (doc_events.sales_invoice_set_naming_series).
The counter sits before the FY part, so numbering continues across years
rather than restarting at 0001 each April. Delivery Note (Challan) -> E.####, GE.### or
M.### (the three paper challan books, e.g. E1181 / GE181 / M680 — counters continue
from them); the older CH-.####. series stays selectable for existing challans.
Purchase Order -> SL/YY-YY/NNN (paper PO#SL/23-24/182) — FY in the middle, so the
counter restarts each April.

Return-document series (SRET-.YY.-, DRET-.YY.-) are kept alongside — the guide
never mentions them, but dropping them would break Sales/Delivery Returns.
"""

import frappe

# Last number used in each paper challan book — ERP numbering continues after it.
LAST_PAPER_CHALLAN = {"E": 1181, "GE": 181, "M": 680}
# Last invoices issued outside the ERP (PI/911/26-27, SL/238/26-27) — series keys.
LAST_PAPER_INVOICE = {"PI/": 911, "SL/": 238}

PROPERTY_SETTERS = [
	{
		"doctype": "Sales Invoice",
		"fieldname": "naming_series",
		"property": "options",
		"value": "PI/.###./.SL_FY.\nSL/.###./.SL_FY.\nSRET-.YY.-",
	},
	{
		"doctype": "Sales Invoice",
		"fieldname": "naming_series",
		"property": "default",
		"value": "PI/.###./.SL_FY.",
	},
	{
		"doctype": "Delivery Note",
		"fieldname": "naming_series",
		"property": "options",
		"value": "E.####\nGE.###\nM.###\nCH-.####.\nDRET-.YY.-",
	},
	{
		"doctype": "Delivery Note",
		"fieldname": "naming_series",
		"property": "default",
		"value": "E.####",
	},
	{
		"doctype": "Purchase Order",
		"fieldname": "naming_series",
		"property": "options",
		"value": "SL/.SL_FY./.###\nPUR-ORD-.YYYY.-",
	},
	{
		"doctype": "Purchase Order",
		"fieldname": "naming_series",
		"property": "default",
		"value": "SL/.SL_FY./.###",
	},
]


def setup_naming_series():
	for ps in PROPERTY_SETTERS:
		frappe.make_property_setter({**ps, "property_type": "Text"}, is_system_generated=True)
	# Never move a counter back.
	for prefix, last in {**LAST_PAPER_CHALLAN, **LAST_PAPER_INVOICE}.items():
		frappe.db.sql(
			"insert into `tabSeries` (name, current) values (%(p)s, %(n)s)"
			" on duplicate key update current = greatest(current, %(n)s)",
			{"p": prefix, "n": last},
		)
