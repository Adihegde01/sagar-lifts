"""Purchase Invoice — Supplier Bills & Contractor Labour Bills.

One doctype, two purposes: a routine payable to a material Supplier, or a
labour payable to an installation Contractor. Bill Type is what tells
ERPNext — and the person raising it — which rules apply; everything else
here only appears/applies for a Contractor bill.
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

IS_CONTRACTOR_BILL = 'eval:doc.bill_type=="Contractor"'

CUSTOM_FIELDS = {
	"Purchase Invoice": [
		{
			"fieldname": "bill_type",
			"label": "Bill Type",
			"fieldtype": "Select",
			"options": "Contractor\nSupplier",
			"reqd": 1,
			"description": "The person raising the bill picks one — everything else follows from this",
			"insert_after": "supplier_name",
		},
		{
			"fieldname": "job_id",
			"label": "Linked Sales Order",
			"fieldtype": "Link",
			"options": "Sales Order",
			"depends_on": IS_CONTRACTOR_BILL,
			"mandatory_depends_on": IS_CONTRACTOR_BILL,
			"in_standard_filter": 1,
			"description": "The deployment this labour bill is for — blank and irrelevant for a Supplier bill",
			"insert_after": "bill_type",
		},
		{
			"fieldname": "job_number",
			"label": "Job Number",
			"fieldtype": "Data",
			"fetch_from": "job_id.job_number",
			"read_only": 1,
			"depends_on": IS_CONTRACTOR_BILL,
			"insert_after": "job_id",
		},
		{
			"fieldname": "job_name",
			"label": "Job Name",
			"fieldtype": "Data",
			"fetch_from": "job_id.job_name",
			"read_only": 1,
			"depends_on": IS_CONTRACTOR_BILL,
			"insert_after": "job_number",
		},
		{
			"fieldname": "approved_by_manufacturing",
			"label": "Approved by Manufacturing",
			"fieldtype": "Check",
			"depends_on": IS_CONTRACTOR_BILL,
			"description": "Manufacturing manager ticks this to approve",
			"insert_after": "job_name",
		},
		{
			"fieldname": "manufacturing_approval_by",
			"label": "Manufacturing Approval By",
			"fieldtype": "Link",
			"options": "User",
			"read_only": 1,
			"depends_on": IS_CONTRACTOR_BILL,
			"description": "Auto-fills on approval",
			"insert_after": "approved_by_manufacturing",
		},
		{
			"fieldname": "manufacturing_approval_date",
			"label": "Manufacturing Approval Date",
			"fieldtype": "Date",
			"read_only": 1,
			"depends_on": IS_CONTRACTOR_BILL,
			"description": "Auto-fills on approval",
			"insert_after": "manufacturing_approval_by",
		},
	]
}


def setup_purchase_invoice_customization():
	# Drop the earlier is_contractor_bill checkbox — superseded by Bill Type.
	frappe.db.delete("Custom Field", {"dt": "Purchase Invoice", "fieldname": "is_contractor_bill"})
	create_custom_fields(CUSTOM_FIELDS, ignore_validate=True)
	frappe.clear_cache(doctype="Purchase Invoice")
