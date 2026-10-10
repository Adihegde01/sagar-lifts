"""Sales Module reports (Sales Module Guide, Section 8.2).

The guide describes these as saved list-view filters ("CRM -> Lead ->
Filter by Assigned Caller"), fitting its own "no-code" framing. Built here
as Query Reports instead — same information, but shareable, independently
filterable, and verifiable by actually running the SQL rather than by
screenshotting a filtered list view.

"Used By" maps to the flat SL Sales/SL Admin/SL Management roles (Supervisor
duties fold into SL Admin — see sales_module_notifications.py docstring for
the same reasoning).
"""

import frappe

REPORTS = [
	{
		"report_name": "SL All Active Leads by Caller",
		"ref_doctype": "Lead",
		"roles": ["SL Admin"],
		"query": """
			select name, lead_name, company_name, assigned_caller, site_city,
				lead_quality, status, next_follow_up_date
			from `tabLead`
			where status not in ('Converted', 'Do Not Contact')
			order by assigned_caller, next_follow_up_date
		""",
	},
	{
		"report_name": "SL Leads with No Activity 7+ Days",
		"ref_doctype": "Lead",
		"roles": ["SL Admin"],
		"query": """
			select name, lead_name, assigned_caller, last_follow_up_date,
				datediff(curdate(), last_follow_up_date) as days_since_activity
			from `tabLead`
			where last_follow_up_date is not null
				and last_follow_up_date < date_sub(curdate(), interval 7 day)
				and status not in ('Converted', 'Do Not Contact')
			order by last_follow_up_date
		""",
	},
	{
		"report_name": "SL Quotations Expiring This Week",
		"ref_doctype": "Quotation",
		"roles": ["SL Admin", "SL Sales"],
		"query": """
			select name, party_name, valid_till, status, grand_total
			from `tabQuotation`
			where valid_till between curdate() and date_add(curdate(), interval 7 day)
				and status = 'Open'
			order by valid_till
		""",
	},
	{
		"report_name": "SL Opportunity Conversion Rate",
		"ref_doctype": "Opportunity",
		"roles": ["SL Admin", "SL Management"],
		"query": """
			select
				count(*) as total_opportunities,
				sum(case when status = 'Converted' then 1 else 0 end) as converted_count,
				round(100.0 * sum(case when status = 'Converted' then 1 else 0 end)
					/ nullif(count(*), 0), 1) as conversion_rate_percent
			from `tabOpportunity`
		""",
	},
	{
		"report_name": "SL Scouter Performance - Leads Generated",
		"ref_doctype": "SL Scout Report",
		"roles": ["SL Admin", "SL Management"],
		"query": """
			select scouter_name,
				count(*) as reports_submitted,
				sum(case when lead_created = 1 then 1 else 0 end) as leads_generated
			from `tabSL Scout Report`
			group by scouter_name
			order by leads_generated desc
		""",
	},
	{
		"report_name": "SL Caller Performance - Conversions",
		"ref_doctype": "Lead",
		"roles": ["SL Admin"],
		"query": """
			select assigned_caller,
				count(*) as total_leads,
				sum(case when status = 'Converted' then 1 else 0 end) as converted_count
			from `tabLead`
			where assigned_caller is not null
			group by assigned_caller
			order by converted_count desc
		""",
	},
	{
		"report_name": "SL Monthly Incentives Paid",
		"ref_doctype": "SL Incentive Record",
		"roles": ["SL Admin", "SL Management"],
		"query": """
			select date_format(payment_date, '%Y-%m') as payment_month,
				count(*) as incentives_paid,
				sum(total_shares_allocated) as total_amount_paid
			from `tabSL Incentive Record`
			where incentive_paid = 1
			group by date_format(payment_date, '%Y-%m')
			order by payment_month desc
		""",
	},
	{
		"report_name": "SL Pipeline Value - Open Opportunities",
		"ref_doctype": "Opportunity",
		"roles": ["SL Admin", "SL Management"],
		"query": """
			select count(*) as open_opportunities,
				sum(estimated_contract_value) as total_pipeline_value
			from `tabOpportunity`
			where status = 'Open'
		""",
	},
]


def setup_sales_module_reports():
	for spec in REPORTS:
		if frappe.db.exists("Report", spec["report_name"]):
			doc = frappe.get_doc("Report", spec["report_name"])
		else:
			doc = frappe.new_doc("Report")
			doc.report_name = spec["report_name"]

		doc.ref_doctype = spec["ref_doctype"]
		doc.report_type = "Query Report"
		doc.module = "sagar-lifts"
		doc.is_standard = "No"
		doc.query = spec["query"].strip()
		doc.set("roles", [])
		for role in spec["roles"]:
			doc.append("roles", {"role": role})
		doc.save(ignore_permissions=True)
