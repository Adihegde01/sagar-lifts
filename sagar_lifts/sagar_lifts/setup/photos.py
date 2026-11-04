"""Photos tab on the challan, PO, GRN and invoice — site and dispatch photos
kept with the document. allow_on_submit so they can be added after the
document is submitted (e.g. the signed challan photographed at site)."""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

DOCTYPES = ["Delivery Note", "Purchase Order", "Purchase Receipt", "Sales Invoice"]


def setup_photos():
	for dt in DOCTYPES:
		last = next(f.fieldname for f in reversed(frappe.get_meta(dt, cached=False).fields) if f.fieldname not in ("sl_photos_tab", "sl_photos"))
		create_custom_fields(
			{
				dt: [
					{"fieldname": "sl_photos_tab", "label": "Photos", "fieldtype": "Tab Break", "insert_after": last},
					{"fieldname": "sl_photos", "label": "Photos", "fieldtype": "Table", "options": "SL Photo", "allow_on_submit": 1, "insert_after": "sl_photos_tab"},
				]
			},
			ignore_validate=True,
		)
