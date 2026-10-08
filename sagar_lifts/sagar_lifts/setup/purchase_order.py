"""Purchase Order — same Contractor/Supplier split as Purchase Invoice
(setup/purchase_invoice.py). A PO for contractor labour needs to trace back
to the job just like the resulting Purchase Invoice does. Material POs can
carry the job too (Sagar Lifts Procurement tab) when bought for a specific lift.

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
			# Dedicated field, not the native `status` — Purchase Order's own
			# status is recomputed by ERPNext's set_status() on every save
			# (Draft/To Receive and Bill/Completed/...), which would stomp any
			# value a workflow set on it. See setup/po_approval_workflow.py.
			"fieldname": "po_approval_status",
			"label": "PO Approval Status",
			"fieldtype": "Select",
			"options": "\nDraft\nPending Approval\nApproved\nOrdered",
			"description": "Workflow state field — PO Approval workflow",
			"insert_after": "bill_type",
		},
		# --- Sagar Lifts Procurement tab (between Details and Address & Contact)
		{
			"fieldname": "sl_procurement_tab",
			"label": "Sagar Lifts Procurement",
			"fieldtype": "Tab Break",
			"insert_after": "item_wise_tax_details",
		},
		{
			"fieldname": "job_id",
			"label": "Linked Sales Order",
			"fieldtype": "Link",
			"options": "Sales Order",
			"in_standard_filter": 1,
			"description": "The lift/deployment this PO is for — contractor labour or material for that job",
			"insert_after": "sl_procurement_tab",
		},
		{
			"fieldname": "job_number",
			"label": "Job Number",
			"fieldtype": "Data",
			"fetch_from": "job_id.job_number",
			"read_only": 1,
			"insert_after": "job_id",
		},
		{
			"fieldname": "job_name",
			"label": "Job Name",
			"fieldtype": "Data",
			"fetch_from": "job_id.job_name",
			"read_only": 1,
			"insert_after": "job_number",
		},
		{
			"fieldname": "procurement_reason",
			"label": "Procurement Reason",
			"fieldtype": "Select",
			"options": "\nNew Installation\nRe-erection\nAMC Spare\nReplacement\nBreakdown Emergency\nStock Replenishment",
			"reqd": 1,
			"insert_after": "job_name",
		},
		{
			"fieldname": "required_at_site_by",
			"label": "Required at Site By",
			"fieldtype": "Date",
			"insert_after": "procurement_reason",
		},
		{
			"fieldname": "urgency_level",
			"label": "Urgency Level",
			"fieldtype": "Select",
			"options": "Normal\nUrgent\nCritical",
			"default": "Normal",
			"insert_after": "required_at_site_by",
		},
		{
			"fieldname": "sl_procurement_col",
			"fieldtype": "Column Break",
			"insert_after": "urgency_level",
		},
		{
			"fieldname": "po_approved_by",
			"label": "Approved By",
			"fieldtype": "Link",
			"options": "User",
			"read_only": 1,
			"description": "Auto-fills when the PO Approval workflow reaches Approved",
			"insert_after": "sl_procurement_col",
		},
		{
			"fieldname": "po_approval_date",
			"label": "Approval Date",
			"fieldtype": "Date",
			"read_only": 1,
			"insert_after": "po_approved_by",
		},
		{
			"fieldname": "procurement_notes",
			"label": "Procurement Notes",
			"fieldtype": "Small Text",
			"insert_after": "po_approval_date",
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
