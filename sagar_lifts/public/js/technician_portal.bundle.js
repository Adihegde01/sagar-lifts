import { createApp } from "vue";
import TechnicianPortalApp from "./technician_portal/TechnicianPortalApp.vue";

// Same class-instantiated-by-the-page pattern as orbit's order_entry —
// page/technician_portal/technician_portal.js calls this after
// frappe.require() resolves the bundle.
frappe.provide("frappe.ui");
frappe.ui.TechnicianPortal = class TechnicianPortal {
	constructor({ wrapper }) {
		hideDeskChrome();
		const el = wrapper?.jquery ? wrapper.get(0) : wrapper;
		this.app = createApp(TechnicianPortalApp);
		this.vm = this.app.mount(el);
	}
};

// SL Technician has no permission on anything but this one page (see
// setup/role_permissions.py) — the navbar/sidebar just point at screens
// they can't open, so hide them. ".body-sidebar-container" is Desk's real
// class for this in the current Frappe version — ".desk-sidebar" (the
// plain-JS page this replaces used) doesn't exist and silently matched
// nothing, which is why that version still showed the sidebar live.
function hideDeskChrome() {
	if (!document.getElementById("tp-chrome-style")) {
		document.head.insertAdjacentHTML(
			"beforeend",
			`<style id="tp-chrome-style">
				body.tp-hide-chrome .navbar,
				body.tp-hide-chrome .body-sidebar-container,
				body.tp-hide-chrome .page-head {
					display: none !important;
				}
			</style>`
		);
	}
	document.body.classList.add("tp-hide-chrome");
	$(window)
		.off("hashchange.tp-hide-chrome")
		.on("hashchange.tp-hide-chrome", () => {
			if (frappe.get_route()[0] !== "technician-portal") {
				document.body.classList.remove("tp-hide-chrome");
				$(window).off("hashchange.tp-hide-chrome");
			}
		});
}
