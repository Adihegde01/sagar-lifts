"""Purchase Invoice — Contractor Labour Bill approval.

Manufacturing's sign-off on a contractor bill, shown only when the bill is
tagged is_contractor_bill (a routine Supplier bill never carries these).
"""

from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

CUSTOM_FIELDS = {
	"Purchase Invoice": [
		{
			"fieldname": "approved_by_manufacturing",
			"label": "Approved by Manufacturing",
			"fieldtype": "Check",
			"depends_on": "eval:doc.is_contractor_bill",
			"insert_after": "job_name",
			"description": "Manufacturing manager ticks this to approve a contractor labour bill",
		},
		{
			"fieldname": "manufacturing_approval_by",
			"label": "Manufacturing Approval By",
			"fieldtype": "Link",
			"options": "User",
			"read_only": 1,
			"depends_on": "eval:doc.is_contractor_bill",
			"insert_after": "approved_by_manufacturing",
		},
		{
			"fieldname": "manufacturing_approval_date",
			"label": "Manufacturing Approval Date",
			"fieldtype": "Date",
			"read_only": 1,
			"depends_on": "eval:doc.is_contractor_bill",
			"insert_after": "manufacturing_approval_by",
		},
	]
}


def setup_purchase_invoice_customization():
	create_custom_fields(CUSTOM_FIELDS, ignore_validate=True)
