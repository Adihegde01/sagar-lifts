// Challan from a Material Request: pick the request by name and its items fill in
// (the blank starter row is dropped; rows already on the challan stay).
frappe.ui.form.on("Delivery Note", {
	async material_request(frm) {
		if (!frm.doc.material_request || frm.doc.docstatus !== 0) return;
		const mr = await frappe.db.get_doc("Material Request", frm.doc.material_request);
		frm.doc.items = (frm.doc.items || []).filter((row) => row.item_code);
		for (const src of mr.items) {
			if (frm.doc.items.some((row) => row.material_request_item === src.name)) continue;
			const row = frm.add_child("items");
			await frappe.model.set_value(row.doctype, row.name, "item_code", src.item_code);
			await frappe.model.set_value(row.doctype, row.name, {
				qty: src.qty,
				uom: src.uom,
				conversion_factor: src.conversion_factor,
				warehouse: src.from_warehouse || src.warehouse || row.warehouse,
				material_request: mr.name,
				material_request_item: src.name,
			});
		}
		frm.refresh_field("items");
	},
});
