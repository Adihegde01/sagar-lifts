"""Purchase Order — same Contractor/Supplier split as Purchase Invoice
(setup/purchase_invoice.py). A PO for contractor labour needs to trace back
to the job just like the resulting Purchase Invoice does; a routine material
PO to a supplier never carries a Job Number.
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

IS_CONTRACTOR_PO = 'eval:doc.bill_type=="Contractor"'

CUSTOM_FIELDS = {
	"Purchase Order": [
		{
			"fieldname": "bill_type",
			"label": "Bill Type",
			"fieldtype": "Select",
			"options": "Contractor\nSupplier",
			"reqd": 1,
			"description": "The person raising the PO picks one — everything else follows from this",
			"insert_after": "supplier_name",
		},
		{
			"fieldname": "job_id",
			"label": "Linked Sales Order",
			"fieldtype": "Link",
			"options": "Sales Order",
			"depends_on": IS_CONTRACTOR_PO,
			"mandatory_depends_on": IS_CONTRACTOR_PO,
			"in_standard_filter": 1,
			"description": "The deployment this labour is for — blank and irrelevant for a Supplier PO",
			"insert_after": "bill_type",
		},
		{
			"fieldname": "job_number",
			"label": "Job Number",
			"fieldtype": "Data",
			"fetch_from": "job_id.job_number",
			"read_only": 1,
			"depends_on": IS_CONTRACTOR_PO,
			"insert_after": "job_id",
		},
		{
			"fieldname": "job_name",
			"label": "Job Name",
			"fieldtype": "Data",
			"fetch_from": "job_id.job_name",
			"read_only": 1,
			"depends_on": IS_CONTRACTOR_PO,
			"insert_after": "job_number",
		},
	]
}


def setup_purchase_order_customization():
	create_custom_fields(CUSTOM_FIELDS, ignore_validate=True)
	frappe.clear_cache(doctype="Purchase Order")
