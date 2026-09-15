"""Order Lifecycle Workflow — Sales Order, state field: Deployment Status.

"Who Can Edit"/"Allowed Roles" list multiple roles per state/transition;
Workflow Document State and Workflow Transition only take one Role per row,
so multiple roles are expressed as repeated rows with the same state (or
state+action+next_state) — frappe.workflow / get_transitions() evaluate each
row independently and OR the results together (see
frappe/public/js/frappe/model/workflow.js get_document_state_roles and
frappe/model/workflow.py get_transitions).

Transition conditions run server-side via frappe.safe_eval with `doc` (the
Sales Order) in scope, plus frappe.db.get_value/get_list and
frappe.utils date helpers — see get_workflow_safe_globals() in
frappe/model/workflow.py. "Signed Challan Received" lives on Delivery Note,
not Sales Order, so that condition looks up the linked Delivery Note by
job_id instead of a doc field.
"""

import frappe

WORKFLOW_NAME = "Sales Order Deployment Lifecycle"

# Frappe's Workflow State "style" options are Primary/Info/Success/Warning/
# Danger/Inverse — there's no "Secondary". Blank (the default muted/grey
# badge) is the closest match for Dismantled.
STATE_STYLES = {
	"Active": "Primary",
	"Dispatched": "Info",
	"Installation": "Warning",
	"Handed Over": "Success",
	"AMC": "Success",
	"Dismantled": "",
}

# (state, doc_status, allow_edit role), in spec order.
STATE_ROLE_ROWS = [
	("Active", "1", "SL Manufacturing"),
	("Active", "1", "SL Billing"),
	("Active", "1", "SL Admin"),
	("Dispatched", "1", "SL Dispatch"),
	("Dispatched", "1", "SL Admin"),
	("Installation", "1", "SL Manufacturing"),
	("Installation", "1", "SL Admin"),
	("Handed Over", "1", "SL Manufacturing"),
	("Handed Over", "1", "SL Admin"),
	("AMC", "1", "SL Service Manager"),
	("AMC", "1", "SL Admin"),
	("Dismantled", "1", "SL Admin"),
]


# (from_state, next_state, action, condition, [roles...])
TRANSITIONS = [
	(
		"Active",
		"Dispatched",
		"Mark Dispatched",
		"doc.advance_received or doc.dispatch_override_approved",
		["SL Dispatch", "SL Admin"],
	),
	(
		"Dispatched",
		"Installation",
		"Signed Challan Received",
		'frappe.db.get_value("Delivery Note", {"job_id": doc.name, "signed_challan_received": 1}, "name")',
		["SL Dispatch", "SL Admin"],
	),
	(
		"Installation",
		"Handed Over",
		"Confirm Handover",
		"doc.handover_date",
		["SL Manufacturing", "SL Admin"],
	),
	(
		"Handed Over",
		"AMC",
		"Start AMC",
		"doc.amc_start_date and frappe.utils.get_datetime(doc.amc_start_date) <= frappe.utils.now_datetime()",
		["SL Admin"],
	),
	(
		"AMC",
		"Dismantled",
		"Confirm Dismantling",
		"doc.dismantle_instruction_received and doc.all_amc_billing_raised"
		" and doc.final_pm_visit_logged and doc.dismantling_billing_trigger_created",
		["SL Manufacturing", "SL Admin"],
	),
]


def _ensure_workflow_states():
	for state, style in STATE_STYLES.items():
		if frappe.db.exists("Workflow State", state):
			frappe.db.set_value("Workflow State", state, "style", style)
		else:
			frappe.get_doc(
				{"doctype": "Workflow State", "workflow_state_name": state, "style": style}
			).insert(ignore_permissions=True)


def _ensure_workflow_actions():
	for _from, _to, action, _cond, _roles in TRANSITIONS:
		if not frappe.db.exists("Workflow Action Master", action):
			frappe.get_doc(
				{"doctype": "Workflow Action Master", "workflow_action_name": action}
			).insert(ignore_permissions=True)


def setup_deployment_workflow():
	_ensure_workflow_states()
	_ensure_workflow_actions()

	if frappe.db.exists("Workflow", WORKFLOW_NAME):
		wf = frappe.get_doc("Workflow", WORKFLOW_NAME)
	else:
		wf = frappe.new_doc("Workflow")
		wf.workflow_name = WORKFLOW_NAME
		wf.document_type = "Sales Order"
		wf.workflow_state_field = "deployment_status"

	wf.is_active = 1
	wf.set("states", [])
	for state, doc_status, role in STATE_ROLE_ROWS:
		wf.append("states", {"state": state, "doc_status": doc_status, "allow_edit": role})

	wf.set("transitions", [])
	for from_state, next_state, action, condition, roles in TRANSITIONS:
		for role in roles:
			wf.append(
				"transitions",
				{
					"state": from_state,
					"action": action,
					"next_state": next_state,
					"allowed": role,
					"condition": condition,
				},
			)

	wf.save(ignore_permissions=True)
