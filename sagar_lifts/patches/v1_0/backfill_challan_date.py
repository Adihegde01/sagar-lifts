import frappe


def execute():
	# Challan Date arrived after these challans were made; their own posting
	# date is the date the challan was raised.
	frappe.db.sql(
		"update `tabDelivery Note` set challan_date = posting_date where challan_date is null and is_return = 0"
	)
