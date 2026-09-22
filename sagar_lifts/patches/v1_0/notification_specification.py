from sagar_lifts.sagar_lifts.setup.sales_invoice import setup_sales_invoice_customization
from sagar_lifts.sagar_lifts.setup.notifications import setup_notifications


def execute():
	# Re-run to pick up the new Collection Lead fetch field added here.
	setup_sales_invoice_customization()
	setup_notifications()
