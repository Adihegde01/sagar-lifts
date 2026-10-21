"""Lift models — Item Groups per lift category under "Lift Models", with the
model Items under them. Sales Order.lift_model only offers items from this tree."""

import frappe

ROOT = "Lift Models"

# category -> model items (item_code, item_name, GST HSN/SAC — 84281019 other lifts,
# 995466 lift installation service)
LIFT_MODELS = {
	"Construction Lift": [
		("SCL 1000", "SCL 1000 Construction Lift", "84281019"),
		("SCL 1500", "SCL 1500 Construction Lift", "84281019"),
		("Reinstalling", "Reinstalling", "995466"),
	],
	"Fire Evacuation Lift": [],
	"Construction Cum Fire Lift": [],
	"Car Lift": [],
	"Permanent Lift": [],
	"AMC": [],
}

# Earlier demo lift items, filed into their category so the filtered dropdown still offers them.
EXISTING_ITEMS = {"SC200-200": "Construction Lift", "SC300-250": "Construction Lift", "PL1000-8": "Permanent Lift"}


def _item_group(name, parent, is_group=0):
	if not frappe.db.exists("Item Group", name):
		frappe.get_doc({"doctype": "Item Group", "item_group_name": name, "parent_item_group": parent, "is_group": is_group}).insert(ignore_permissions=True)


def setup_lift_models():
	_item_group(ROOT, "All Item Groups", is_group=1)
	for category, items in LIFT_MODELS.items():
		_item_group(category, ROOT)
		for code, item_name, hsn in items:
			if frappe.db.exists("Item", code):
				continue
			frappe.get_doc({
				"doctype": "Item",
				"item_code": code,
				"item_name": item_name,
				"item_group": category,
				"stock_uom": "Nos",
				"gst_hsn_code": hsn,
				# same settings as the existing lift-model items
				"is_stock_item": 0,
				"include_item_in_manufacturing": 1,
				"is_sales_item": 1,
				"is_purchase_item": 1,
			}).insert(ignore_permissions=True)
	for code, category in EXISTING_ITEMS.items():
		if frappe.db.exists("Item", code):
			frappe.db.set_value("Item", code, "item_group", category)
