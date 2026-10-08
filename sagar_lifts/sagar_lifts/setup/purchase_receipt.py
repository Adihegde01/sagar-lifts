"""Purchase Receipt (GRN) — Sagar Lifts GRN tab.

Linked Sales Order defaults from the Purchase Order the GRN is made against
(doc_events.purchase_receipt_set_job_id).
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

CUSTOM_FIELDS = {
	"Purchase Receipt": [
		{
			"fieldname": "sl_grn_tab",
			"label": "Sagar Lifts GRN",
			"fieldtype": "Tab Break",
			"insert_after": "supplied_items",
		},
		{
			"fieldname": "job_id",
			"label": "Linked Sales Order",
			"fieldtype": "Link",
			"options": "Sales Order",
			"in_standard_filter": 1,
			"description": "Defaults from the Purchase Order",
			"insert_after": "sl_grn_tab",
		},
		{
			"fieldname": "received_by",
			"label": "Received By",
			"fieldtype": "Link",
			"options": "User",
			"reqd": 1,
			"default": "__user",
			"insert_after": "job_id",
		},
		{
			"fieldname": "condition_of_goods",
			"label": "Condition of Goods",
			"fieldtype": "Select",
			"options": "\nGood\nPartial Shortage\nDamaged\nWrong Item",
			"reqd": 1,
			"insert_after": "received_by",
		},
		{
			"fieldname": "supplier_challan_number",
			"label": "Supplier Challan Number",
			"fieldtype": "Data",
			"insert_after": "condition_of_goods",
		},
		{
			"fieldname": "supplier_challan_date",
			"label": "Supplier Challan Date",
			"fieldtype": "Date",
			"insert_after": "supplier_challan_number",
		},
		{
			"fieldname": "grn_verified_by",
			"label": "GRN Verified By",
			"fieldtype": "Link",
			"options": "User",
			"insert_after": "supplier_challan_date",
		},
		{
			"fieldname": "sl_grn_col",
			"fieldtype": "Column Break",
			"insert_after": "grn_verified_by",
		},
		{
			"fieldname": "shortage_noted",
			"label": "Shortage Noted",
			"fieldtype": "Check",
			"insert_after": "sl_grn_col",
		},
		{
			"fieldname": "shortage_details",
			"label": "Shortage Details",
			"fieldtype": "Small Text",
			"depends_on": "shortage_noted",
			"mandatory_depends_on": "shortage_noted",
			"insert_after": "shortage_noted",
		},
		{
			"fieldname": "damage_noted",
			"label": "Damage Noted",
			"fieldtype": "Check",
			"insert_after": "shortage_details",
		},
		{
			"fieldname": "damage_details",
			"label": "Damage Details",
			"fieldtype": "Small Text",
			"depends_on": "damage_noted",
			"mandatory_depends_on": "damage_noted",
			"insert_after": "damage_noted",
		},
		{
			"fieldname": "grn_notes",
			"label": "GRN Notes",
			"fieldtype": "Small Text",
			"insert_after": "damage_details",
		},
	]
}


def setup_purchase_receipt_customization():
	create_custom_fields(CUSTOM_FIELDS, ignore_validate=True)
	frappe.clear_cache(doctype="Purchase Receipt")
