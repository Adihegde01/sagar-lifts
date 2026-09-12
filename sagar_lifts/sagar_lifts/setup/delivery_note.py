"""Delivery Note customisation for Sagar Lifts — the Challan.

Extends the standard Delivery Note so native stock-reduction-on-submit
behaviour is reused as-is; only the Sagar Lifts dispatch fields are added
via Customize Form. Depends on setup_job_id_links having already added
job_id/job_number/job_name to Delivery Note.
"""

from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

CUSTOM_FIELDS = {
	"Delivery Note": [
		{
			"fieldname": "sl_challan_section",
			"label": "Challan Details",
			"fieldtype": "Section Break",
			"insert_after": "job_name",
		},
		{
			"fieldname": "challan_type",
			"label": "Challan Type",
			"fieldtype": "Select",
			"options": "Main Dispatch\nAdditional Dispatch\nJumping Material",
			"reqd": 1,
			"insert_after": "sl_challan_section",
		},
		{
			"fieldname": "vehicle_number",
			"label": "Vehicle Number",
			"fieldtype": "Data",
			"reqd": 1,
			"insert_after": "challan_type",
		},
		{
			# Not "driver_name" — Delivery Note already has a native field with
			# that name (idx 126, unrelated Transporter Info section); reusing
			# it would silently hijack this field's position and orphan every
			# field chained after it via insert_after.
			"fieldname": "sl_driver_name",
			"label": "Driver Name",
			"fieldtype": "Data",
			"insert_after": "vehicle_number",
		},
		{
			"fieldname": "dispatched_by",
			"label": "Dispatched By",
			"fieldtype": "Data",
			"description": "Staff name",
			"insert_after": "sl_driver_name",
		},
		{
			"fieldname": "sl_challan_col",
			"fieldtype": "Column Break",
			"insert_after": "dispatched_by",
		},
		{
			"fieldname": "eway_bill_number",
			"label": "E-Way Bill Number",
			"fieldtype": "Data",
			"description": "Required above the GST threshold — accounts team to confirm and enter",
			"insert_after": "sl_challan_col",
		},
		{
			"fieldname": "stores_quantity_verified",
			"label": "Stores Quantity Verified",
			"fieldtype": "Check",
			"reqd": 1,
			"description": "Stores must tick before dispatch — confirms quantities match the challan",
			"insert_after": "eway_bill_number",
		},
		{
			"fieldname": "sl_signed_challan_section",
			"label": "Signed Challan",
			"fieldtype": "Section Break",
			"insert_after": "stores_quantity_verified",
		},
		{
			"fieldname": "signed_challan_received",
			"label": "Signed Challan Received",
			"fieldtype": "Check",
			"description": "Dispatch ticks this when the signed copy returns from site",
			"insert_after": "sl_signed_challan_section",
		},
		{
			"fieldname": "signed_challan_date",
			"label": "Signed Challan Date",
			"fieldtype": "Date",
			"insert_after": "signed_challan_received",
		},
		{
			"fieldname": "sl_signed_challan_col",
			"fieldtype": "Column Break",
			"insert_after": "signed_challan_date",
		},
		{
			"fieldname": "signed_by_at_site",
			"label": "Signed By at Site",
			"fieldtype": "Data",
			"insert_after": "sl_signed_challan_col",
		},
		{
			# Unlabeled boundary — without it, native fields that follow
			# (Date, Posting Time, Is Return, ...) render as if they belong
			# under the "Signed Challan" heading above.
			"fieldname": "sl_challan_end_section",
			"fieldtype": "Section Break",
			"insert_after": "signed_by_at_site",
		},
	]
}


def setup_delivery_note_customization():
	import frappe

	# Drop the earlier "driver_name" custom field — it collided with Delivery
	# Note's own native field of that name and was replaced by sl_driver_name.
	frappe.db.delete("Custom Field", {"dt": "Delivery Note", "fieldname": "driver_name"})
	create_custom_fields(CUSTOM_FIELDS, ignore_validate=True)
	frappe.clear_cache(doctype="Delivery Note")
