app_name = "sagar_lifts"
app_title = "sagar-lifts"
app_publisher = "Adi"
app_description = "sagar-lifts"
app_email = "hegdeadi01@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "sagar_lifts",
# 		"logo": "/assets/sagar_lifts/logo.png",
# 		"title": "sagar-lifts",
# 		"route": "/sagar_lifts",
# 		"has_permission": "sagar_lifts.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/sagar_lifts/css/sagar_lifts.css"
# app_include_js = "/assets/sagar_lifts/js/sagar_lifts.js"

# include js, css files in header of web template
# web_include_css = "/assets/sagar_lifts/css/sagar_lifts.css"
# web_include_js = "/assets/sagar_lifts/js/sagar_lifts.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "sagar_lifts/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "sagar_lifts/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "sagar_lifts.utils.jinja_methods",
# 	"filters": "sagar_lifts.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "sagar_lifts.install.before_install"
after_install = [
	"sagar_lifts.sagar_lifts.setup.roles.after_install",
	"sagar_lifts.sagar_lifts.setup.sales_order.setup_sales_order_customization",
	"sagar_lifts.sagar_lifts.setup.job_id.setup_job_id_links",
	"sagar_lifts.sagar_lifts.setup.delivery_note.setup_delivery_note_customization",
	"sagar_lifts.sagar_lifts.setup.maintenance_visit.setup_maintenance_visit_customization",
	"sagar_lifts.sagar_lifts.setup.purchase_invoice.setup_purchase_invoice_customization",
	"sagar_lifts.sagar_lifts.setup.purchase_order.setup_purchase_order_customization",
	"sagar_lifts.sagar_lifts.setup.sales_invoice.setup_sales_invoice_customization",
	"sagar_lifts.sagar_lifts.setup.deployment_workflow.setup_deployment_workflow",
	"sagar_lifts.sagar_lifts.setup.role_permissions.setup_role_permissions",
	"sagar_lifts.sagar_lifts.setup.naming_series.setup_naming_series",
	"sagar_lifts.sagar_lifts.setup.notifications.setup_notifications",
]

# Uninstallation
# ------------

# before_uninstall = "sagar_lifts.uninstall.before_uninstall"
# after_uninstall = "sagar_lifts.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "sagar_lifts.utils.before_app_install"
# after_app_install = "sagar_lifts.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "sagar_lifts.utils.before_app_uninstall"
# after_app_uninstall = "sagar_lifts.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "sagar_lifts.build.after_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "sagar_lifts.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

doc_events = {
	"Sales Order": {
		"validate": [
			"sagar_lifts.sagar_lifts.doc_events.sales_order_set_job_number",
			"sagar_lifts.sagar_lifts.doc_events.sales_order_validate_contract_value",
		],
	},
	"Purchase Invoice": {
		"validate": "sagar_lifts.sagar_lifts.doc_events.purchase_invoice_set_manufacturing_approval",
	},
	"Maintenance Visit": {
		"validate": "sagar_lifts.sagar_lifts.doc_events.maintenance_visit_set_quarter",
	},
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	"daily": [
		"sagar_lifts.sagar_lifts.tasks.flag_overdue_amc_billing",
	],
}

# Testing
# -------

# before_tests = "sagar_lifts.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "sagar_lifts.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "sagar_lifts.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "sagar_lifts.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["sagar_lifts.utils.before_request"]
# after_request = ["sagar_lifts.utils.after_request"]

# Job Events
# ----------
# before_job = ["sagar_lifts.utils.before_job"]
# after_job = ["sagar_lifts.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"sagar_lifts.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

