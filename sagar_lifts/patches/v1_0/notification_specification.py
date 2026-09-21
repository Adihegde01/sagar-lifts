from sagar_lifts.sagar_lifts.setup.job_id import setup_job_id_links
from sagar_lifts.sagar_lifts.setup.purchase_invoice import setup_purchase_invoice_customization
from sagar_lifts.sagar_lifts.setup.notifications import setup_notifications


def execute():
	setup_job_id_links()
	setup_purchase_invoice_customization()
	setup_notifications()
