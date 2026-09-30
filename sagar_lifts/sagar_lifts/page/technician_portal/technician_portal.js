frappe.pages['technician-portal'].on_page_load = function (wrapper) {
	frappe.ui.make_app_page({
		parent: wrapper,
		title: 'My Maintenance Visits',
		single_column: true,
	})
}

frappe.pages['technician-portal'].on_page_show = function (wrapper) {
	load_portal(wrapper)
}

function load_portal(wrapper) {
	const $parent = $(wrapper).find('.layout-main-section')
	$parent.empty()

	frappe.require('technician_portal.bundle.js').then(() => {
		if (!frappe.ui.TechnicianPortal) {
			$parent.html(
				`<div class="text-muted" style="padding:40px;text-align:center">
					Technician Portal assets are not built yet. Run <b>bench build --app sagar_lifts</b> and reload.
				</div>`,
			)
			return
		}
		frappe.technician_portal = new frappe.ui.TechnicianPortal({ wrapper: $parent })
	})
}
