"""Purchase Order — same Contractor/Supplier split as Purchase Invoice
(setup/purchase_invoice.py). A PO for contractor labour needs to trace back
to the job just like the resulting Purchase Invoice does; a routine material
PO to a supplier never carries a Job Number.

A contractor is a Supplier (Section 15: contractors are registered as
Suppliers, Supplier Group "Contractors") — so both Bill Types use the same
native `supplier` field, always visible and mandatory as standard. A
separate "Contractor" field was tried and dropped: Purchase Order's own
controller (tax templates, payment terms, price list, party account
currency, reports) all key off `supplier` specifically, so a parallel field
would just sit there inert while the real logic silently had no party.
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
			"description": "The person raising the PO picks one — Supplier below is the contractor "
			"themself when this is Contractor (contractors are registered as Suppliers)",
			"insert_after": "supplier_name",
		},
		{
			"fieldname": "job_id",
			"label": "Linked Sales Order",
			"fieldtype": "Link",
			"options": "Sales Order",
			"depends_on": IS_CONTRACTOR_PO,
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
		{
			# Dedicated field, not the native `status` — Purchase Order's own
			# status is recomputed by ERPNext's set_status() on every save
			# (Draft/To Receive and Bill/Completed/...), which would stomp any
			# value a workflow set on it. See setup/po_approval_workflow.py.
			"fieldname": "po_approval_status",
			"label": "PO Approval Status",
			"fieldtype": "Select",
			"options": "\nDraft\nPending Approval\nApproved\nOrdered",
			"description": "Workflow state field — PO Approval workflow",
			"insert_after": "job_name",
		},
	]
}


def setup_purchase_order_customization():
	# Drop the dropped "contractor" field and the supplier overrides an
	# earlier version of this setup applied — supplier is native/stock again.
	frappe.db.delete("Custom Field", {"dt": "Purchase Order", "fieldname": "contractor"})
	frappe.db.delete(
		"Property Setter",
		{
			"doc_type": "Purchase Order",
			"field_name": "supplier",
			"property": ["in", ("reqd", "mandatory_depends_on", "depends_on")],
		},
	)
	create_custom_fields(CUSTOM_FIELDS, ignore_validate=True)
	frappe.clear_cache(doctype="Purchase Order")
