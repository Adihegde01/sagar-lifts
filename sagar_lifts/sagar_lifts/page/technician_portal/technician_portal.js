frappe.pages['technician-portal'].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'My Maintenance Visits',
		single_column: true,
	})
	hide_desk_chrome()
	render(page)
}

frappe.pages['technician-portal'].on_page_show = function (wrapper) {
	hide_desk_chrome()
	render(wrapper.page)
}

// Technicians get this page as their home_page (see setup/roles.py) and have
// no permission on any other doctype — the desk navbar/sidebar are dead
// weight pointing at screens they can't open, so hide them, same trick as
// orbit/orders/page/order_entry/order_entry.js uses for its own page-head.
function hide_desk_chrome() {
	if (!document.getElementById('sl-technician-portal-style')) {
		$(`<style id="sl-technician-portal-style">
			body.sl-technician-portal .navbar,
			body.sl-technician-portal .desk-sidebar,
			body.sl-technician-portal .page-head {
				display: none !important;
			}
			body.sl-technician-portal .content,
			body.sl-technician-portal #body_div {
				margin-left: 0 !important;
				padding-top: 0 !important;
			}
		</style>`).appendTo('head')
	}
	document.body.classList.add('sl-technician-portal')
	$(window)
		.off('hashchange.sl-technician-portal')
		.on('hashchange.sl-technician-portal', () => {
			if (frappe.get_route()[0] !== 'technician-portal') {
				document.body.classList.remove('sl-technician-portal')
				$(window).off('hashchange.sl-technician-portal')
			}
		})
}

function render(page) {
	page.main.empty()
	const $wrap = $(`
		<div style="max-width: 480px; margin: 0 auto; padding: 16px 8px;">
			<button class="btn btn-primary btn-block sl-new-visit" style="margin-bottom: 20px;">
				${__('+ New Visit')}
			</button>
			<div class="sl-visit-list text-muted">${__('Loading your visits…')}</div>
		</div>
	`).appendTo(page.main)

	$wrap.find('.sl-new-visit').on('click', () => frappe.new_doc('Maintenance Visit'))

	// No manual filter needed — the SL Technician DocPerm on Maintenance
	// Visit is if_owner=1 (setup/role_permissions.py), so the server already
	// scopes this list to visits the logged-in technician created.
	frappe.call({
		method: 'frappe.client.get_list',
		args: {
			doctype: 'Maintenance Visit',
			fields: ['name', 'mntc_date', 'customer_name', 'visit_type', 'docstatus', 'job_name'],
			order_by: 'mntc_date desc',
			limit_page_length: 50,
		},
	}).then((r) => {
		const visits = r.message || []
		const $list = $wrap.find('.sl-visit-list')
		if (!visits.length) {
			$list.text(__('No visits logged yet.'))
			return
		}
		$list.empty()
		visits.forEach((v) => {
			const status = v.docstatus === 1 ? __('Submitted') : __('Draft')
			$(`<div class="sl-visit-row" style="padding:12px 4px;border-bottom:1px solid var(--border-color);cursor:pointer;">
				<div style="font-weight:600;">${frappe.utils.escape_html(v.job_name || v.customer_name || v.name)}</div>
				<div class="text-muted" style="font-size:12px;">
					${frappe.datetime.str_to_user(v.mntc_date) || ''} · ${frappe.utils.escape_html(v.visit_type || '')} · ${status}
				</div>
			</div>`)
				.on('click', () => frappe.set_route('maintenance-visit', v.name))
				.appendTo($list)
		})
	})
}
