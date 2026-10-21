"""Print formats — the Delivery Challan copies Sagar Lifts' paper E, GE and M
challan books (same layout): header, Messrs, Challan No/Date/Order No, item table, GSTIN,
receiver's signature and "For Sagar Lifts" signatory. The Purchase Order copies
the PO letter (PO#SL/23-24/182): office header, M/s supplier, item table,
"Plus GST Extra" and the numbered Terms & Conditions."""

import frappe

CHALLAN_HTML = """
<style>
	.slc th, .slc td { color: #000 !important; background: none !important; }
	.slc th { font-weight: bold; text-align: center; }
	.slc { font-family: Arial, sans-serif; font-size: 12px; color: #222; }
	.slc .c { text-align: center; }
	.slc h4 { margin: 0; letter-spacing: 1px; }
	.slc h2 { margin: 2px 0; font-size: 26px; }
	.slc .line { border-bottom: 1px solid #555; padding: 4px 0; }
	.slc table.items { width: 100%; border-collapse: collapse; margin-top: 8px; }
	.slc table.items th, .slc table.items td { border: 1px solid #555; padding: 4px 6px; }
	.slc table.items td.r { text-align: right; }
	.slc .meta td { padding: 3px 8px 3px 0; }
	.slc .foot { margin-top: 40px; width: 100%; }
</style>
{% set so = frappe.db.get_value("Sales Order", doc.job_id, ["job_number", "transaction_date"], as_dict=1) if doc.job_id else None %}
{% set has_rates = doc.items | selectattr("rate") | list | length %}
<div class="slc">
	<div class="c">
		<h4>DELIVERY CHALLAN</h4>
		<h2>Sagar Lifts</h2>
		<div>111, Veena Industrial Estate, Near to Monginis Factory, Off Link Road, Andheri (W), Mumbai - 400 053.</div>
		<div><b>Mobile : 9223515783 / 9223501198</b></div>
	</div>
	<div class="line" style="margin-top:10px">Messrs <b>{{ doc.customer_name }}</b>
		{% if doc.site_name %} &mdash; {{ doc.site_name }}{% endif %}</div>
	<table class="meta" style="margin-top:6px"><tr>
		<td>Challan No. <b>{{ doc.name }}</b></td>
		<td>Date <b>{{ frappe.utils.formatdate(doc.challan_date or doc.posting_date, "dd/MM/yy") }}</b></td>
		<td>Order No. <b>{{ (so and so.job_number) or doc.job_id or "" }}</b></td>
		<td>Date <b>{{ frappe.utils.formatdate(so.transaction_date, "dd/MM/yy") if so else "" }}</b></td>
	</tr></table>
	<table class="items">
		<tr><th style="width:8%">Sr. No.</th><th>DESCRIPTION</th><th style="width:16%">Quantity</th>
			<th style="width:12%">Rate</th><th style="width:14%">Amount Rs.</th></tr>
		{% for row in doc.items %}
		<tr>
			<td>{{ row.idx }}</td>
			<td>{{ row.item_name }}{% if row.description and row.description != row.item_name %}<br><small>{{ row.description | striptags }}</small>{% endif %}</td>
			<td>{{ row.get_formatted("qty") }} {{ row.uom }}</td>
			<td class="r">{{ row.get_formatted("rate") if has_rates else "" }}</td>
			<td class="r">{{ row.get_formatted("amount") if has_rates else "" }}</td>
		</tr>
		{% endfor %}
		<tr><td colspan="3"><b>GSTIN : {{ frappe.db.get_value("Company", doc.company, "tax_id") or "27AERFS4394C1ZK" }}</b></td>
			<td class="r"><b>TOTAL</b></td>
			<td class="r"><b>{{ doc.get_formatted("total") if has_rates else "" }}</b></td></tr>
	</table>
	<table class="foot"><tr>
		<td style="vertical-align:bottom">{% if doc.vehicle_number %}Vehicle No. <b>{{ doc.vehicle_number }}</b><br><br>{% endif %}Receiver's Signature</td>
		<td style="text-align:right">For <b>Sagar Lifts</b><br><br><br><br>Authorised Signatory</td>
	</tr></table>
</div>
"""


PO_HTML = """
<style>
	.slpo { font-family: Arial, Helvetica, sans-serif; font-size: 14px; color: #000; }
	.slpo th, .slpo td { color: #000 !important; background: none !important; }
	.slpo .c { text-align: center; line-height: 1.5; }
	.slpo .r { text-align: right; }
	.slpo table { width: 100%; border-collapse: collapse; }
	.slpo table.items { border: 1.5px solid #000; margin-top: 12px; }
	.slpo table.items th { border: 1.5px solid #000; padding: 1px 4px !important; font-size: 15px; font-weight: bold; text-align: center; }
	.slpo table.items td { border: 1px solid #000; padding: 0 4px !important; height: 22px; vertical-align: bottom !important; }
	.slpo ol { margin: 0; padding-left: 20px; }
	.slpo ol li { padding-left: 2px; }
</style>
{% set so = frappe.db.get_value("Sales Order", doc.job_id, ["job_number", "site_contact_person", "site_contact_number",
	"site_address_line_1", "site_address_line_2", "site_city", "site_pin_code"], as_dict=1) if doc.job_id else None %}
{% set job_no = (so and so.job_number) or doc.job_id %}
{# One grid row per description line, like the ruled paper PO: item name, extra
   description lines, Make, Job No (first item only), a blank row between items,
   then blank rows to fill the grid and "Plus GST Extra" in the last row. #}
{% set lines = [] %}
{% for row in doc.items %}
	{% set extra = (row.description or "") | replace("<br>", "||") | replace("</p>", "||") | replace("</div>", "||") | striptags %}
	{% set first = namespace(done=false) %}
	{% set texts = [row.item_name] + extra.split("||") | map("trim") | reject("equalto", row.item_name) | select | list %}
	{% for text in texts %}
		{% set _ = lines.append({"no": row.idx if not first.done else "", "text": text | trim, "bold": false,
			"qty": "%g" | format(row.qty) if not first.done else "", "uom": row.uom if not first.done else "",
			"rate": "%.2f" | format(row.rate) if not first.done else ""}) %}
		{% set first.done = true %}
	{% endfor %}
	{% if row.brand %}{% set _ = lines.append({"text": "Make " ~ row.brand, "bold": true}) %}{% endif %}
	{% if job_no and loop.first %}{% set _ = lines.append({"text": "Job No - " ~ job_no, "bold": true}) %}{% endif %}
	{% if not loop.last %}{% set _ = lines.append({"text": ""}) %}{% endif %}
{% endfor %}
<div class="slpo">
	<div class="c">
		<div style="font-size:28px; font-weight:bold; margin-bottom:6px">Sagar Lifts</div>
		Opp. Options Showroom, 18/62, Silver Sand,<br>
		Lokhandwala, Nr Aadarsh Nagar, Nr Infinity Mall<br>
		New Link Road, Andheri West Mumbai Suburban, Maharashtra - 400 102<br>
		Tel : 9223515783 / 9223501198<br>
		Email : purchase@sagarlifts.com<br>
		<b>GST # {{ frappe.db.get_value("Company", doc.company, "tax_id") or "27AERFS4394C1ZK" }}</b>
	</div>
	<table style="margin-top:10px"><tr>
		<td style="vertical-align:top"><b>Purchase Order</b></td>
		<td style="width:32%"><b>PO#{{ doc.name }}<br>Date : {{ frappe.utils.formatdate(doc.transaction_date, "dd/MM/yyyy") }}</b></td>
	</tr></table>
	<div style="margin-top:14px; line-height:1.5"><b>M/s. {{ doc.supplier_name }}</b><br>{{ doc.address_display or "" }}</div>
	<div style="margin-top:22px; line-height:1.5">Sir,<br>We are pleased to place order on you as follows.</div>
	<table class="items">
		<tr><th style="width:7%">S. No.</th><th>Item Description</th><th style="width:10%">Qty</th><th style="width:10%">Unit</th><th style="width:13%">Rate</th></tr>
		{% for l in lines %}
		<tr><td class="c">{{ l.no or "" }}</td><td>{% if l.bold %}<b>{{ l.text }}</b>{% else %}{{ l.text }}{% endif %}</td>
			<td class="c">{{ l.qty or "" }}</td><td class="c">{{ l.uom or "" }}</td><td class="r">{{ l.rate or "" }}</td></tr>
		{% endfor %}
		{% for _ in range([12 - lines | length, 1] | max) %}<tr><td></td><td></td><td></td><td></td><td></td></tr>{% endfor %}
		<tr><td></td><td></td><td colspan="3" class="c" style="border:1.5px solid #000"><b style="font-size:15px">Plus GST Extra</b></td></tr>
	</table>
	<div style="margin-top:2px; line-height:1.45"><b>Terms &amp; Conditions:</b>
		<ol>
			<li>Delivery Date: <b>{{ doc.urgency_level if doc.urgency_level in ("Urgent", "Critical")
				else frappe.utils.formatdate(doc.required_at_site_by or doc.schedule_date, "dd/MM/yyyy") }}</b></li>
			<li>Payments : {{ doc.payment_terms_template or "As agreed" }}.</li>
			<li>Delivery Add : {{ (doc.shipping_address_display | replace(",<br>", ", ") | replace("<br>", ", ") | striptags | trim | trim(",")) if doc.shipping_address_display
				else ((so and [so.site_address_line_1, so.site_address_line_2, so.site_city, so.site_pin_code] | select | join(", ")) or "Our godown") }}</li>
			{% if so and so.site_contact_person %}<li>Contact Person : {{ so.site_contact_person }}{% if so.site_contact_number %} - {{ so.site_contact_number }}{% endif %}</li>{% endif %}
			{% if job_no %}<li>Job No : {{ job_no }}</li>{% endif %}
			<li><b>Please attach this PO along with tax invoice</b></li>
		</ol>
	</div>
	<div style="margin-top:22px"><b>For Sagar Lifts</b><div style="height:70px"></div><b>(Authorised Signatory)</b></div>
</div>
"""

# Tax Invoice (paper SL/238/26-27). Milestone bills show the contract and the
# milestone % table (invoice_print.milestone_bill); other bills (AMC, jumping)
# show the invoice's own items. Proforma Invoices (paper PI/911/26-27) print the
# same layout with "Proforma No", the customer's PO and the tax-invoice note.
INVOICE_HTML = """
<style>
	.slti { font-family: Calibri, Carlito, Arial, sans-serif; font-size: 12.5px; color: #000; }
	.slti table { width: 100%; border-collapse: collapse; }
	.slti th, .slti td { color: #000 !important; background: none !important; }
	.slti .grid td, .slti .grid th { border: 1px solid #000; padding: 2px 5px !important; vertical-align: middle !important; }
	.slti .grid th { font-weight: bold; text-align: center; vertical-align: middle; }
	.slti .serif { font-family: "Times New Roman", Times, serif; font-weight: bold; }
	.slti .c { text-align: center; } .slti .r { text-align: right; } .slti .b { font-weight: bold; }
	.slti .ind { padding-left: 42px; }
	.slti .ms td { height: 40px; vertical-align: middle; }
	.slti .tot td { padding: 1px 5px; }
</style>
{% macro amt(v) %}{{ "%.0f" | format(v or 0) }}{% endmacro %}
{% macro pct(v) %}{{ ("%.2f" | format(v or 0)).rstrip("0").rstrip(".") }}%{% endmacro %}
{% set is_pi = doc.pi_type != "Tax Invoice" %}
{% set gstin = doc.company_gstin or frappe.db.get_value("Company", doc.company, "tax_id") or "27AERFS4394C1ZK" %}
{% set mb = milestone_bill(doc) if doc.billing_trigger_type == "Milestone" and doc.job_id and doc.milestone_number else None %}
{% set words = (doc.in_words or "").replace("INR ", "").replace(",", "").replace(" And ", " ").rstrip(".") %}
{% set words = words[:-4] ~ "Only" if words.lower().endswith("only") else words %}
<div class="slti">
	<div class="c b" style="font-size:17px">SAGAR LIFTS</div>
	<div class="c b">Opp.Options Showroom, 18/62, Silver Sand, Lokhandwala Nr.Adarsh Nagar,Nr Infinity Mall New Link Road,<br>Andheri West Mumbai - 400102</div>
	<div class="c b" style="border:1px solid #000; font-style:italic">{{ "Proforma Invoice" if is_pi else "TAX INVOICE" }}</div>

	<table style="margin-top:2px"><tr>
		<td class="ind" style="width:57%; vertical-align:top">
			<div class="b">{{ doc.customer_name }}</div>
			<div>{{ (doc.address_display or "") | replace("<br>\\n", "<br>") }}</div>
			<br>
			{% if doc.billing_address_gstin %}<div class="{{ '' if is_pi else 'serif' }}">Customer GST TIN - {{ doc.billing_address_gstin }}</div>{% endif %}
			{% set cpan = frappe.db.get_value("Customer", doc.customer, "pan") %}
			{% if cpan %}<div class="{{ '' if is_pi else 'serif' }}">PAN NO : {{ cpan }}</div>{% endif %}
		</td>
		<td style="vertical-align:top; padding-top:12px">
			{% if doc.shipping_address %}<div class="serif">Shipping Add</div>
			<div class="b">{{ doc.customer_name }}</div><div>{{ doc.shipping_address }}</div>{% endif %}
		</td>
	</tr></table>

	<div class="ind serif" style="margin-top:14px">{% set pos = (doc.place_of_supply or "").split("-", 1) %}Place {{ "of" if is_pi else "to" }} Supply : {{ (pos[1] ~ " - " ~ pos[0]) if pos | length == 2 else pos[0] }}</div>
	{% set po_no = doc.po_no or (mb and mb.so.po_no) %}
	{% set po_date = doc.po_date or (mb and mb.so.po_date) %}
	{% if po_no %}<div class="ind serif" style="margin-top:16px">P O No : {{ po_no }}</div>{% endif %}
	{% if po_date %}<div class="ind serif" style="margin-top:6px">P O Date : {{ frappe.utils.formatdate(po_date, "dd.MM.yyyy") }}</div>{% endif %}
	<table style="margin-top:22px"><tr>
		<td class="ind serif" style="width:57%">{{ "Proforma" if is_pi else "Invoice" }} No : {{ doc.name }}</td>
		<td class="serif">Date : - {{ frappe.utils.formatdate(doc.posting_date, "dd.MM.yyyy") }}</td>
	</tr></table>

	{% if mb %}
	{% set first = mb.so["items"][0] if mb.so["items"] else None %}
	<div class="ind serif" style="margin:18px 0 14px; font-size:13.5px">Sub : - " Work order for {{ (first.item_name if first else "") }}."</div>
	<table class="grid" style="width:88%; margin-left:4%">
		<tr><th style="width:46%">Description</th><th style="width:9%">HSN/SAC<br>Code</th><th style="width:7%">Qty</th>
			<th style="width:9%">Unit</th><th style="width:13%">Rate</th><th style="width:13%">Amount</th></tr>
		{% for row in mb.so["items"] %}
		<tr><td>{{ (row.description | striptags | trim) or row.item_name }}</td><td class="c">{{ row.gst_hsn_code or "" }}</td>
			<td class="c">{{ "%g" | format(row.qty) }}</td><td class="c">{{ row.uom }}</td>
			<td class="r">{{ amt(row.rate) }}</td><td class="r">{{ amt(row.amount) }}</td></tr>
		{% endfor %}
		<tr><td class="b">Total Contract value</td><td></td><td></td><td></td><td></td><td class="r b">{{ amt(mb.contract) }}</td></tr>
	</table>
	{% endif %}

	<table class="grid" style="margin-top:22px; border:2px solid #000">
		{% if mb %}
		{% set hsn = (first.gst_hsn_code if first else "") or "" %}
		<tr><th style="width:5%">Sr.No</th><th style="width:36%">Description</th><th style="width:9%">HSN/SAC<br>Code</th>
			<th style="width:9%">%</th><th style="width:8%">Pre</th><th style="width:8%">Curr</th><th style="width:12%">Total</th><th style="width:13%">Amt</th></tr>
		{% for r in mb.rows %}
		<tr class="ms"><td class="c">{{ "abcdefghij"[loop.index0] }}</td><td>Payable {{ pct(r.percent) }} {{ r.label }}</td><td class="c">{{ hsn }}</td>
			<td class="c">{{ pct(r.percent) }}</td><td class="r">{{ pct(r.pre) }}</td><td class="r">{{ pct(r.curr) }}</td>
			<td class="r">{{ pct(r.total) }}</td><td class="r">{{ amt(r.amount) }}</td></tr>
		{% endfor %}
		{% set span = 6 %}
		<tr class="tot"><td></td><td colspan="5"></td><td class="r">TOTAL = A</td><td class="r b">{{ amt(mb.a) }}</td></tr>
		<tr class="tot"><td></td><td colspan="6" class="r">Less Previous bill amt = B</td><td class="r">{{ amt(mb.b) }}</td></tr>
		<tr class="tot"><td></td><td colspan="6" class="r">Current bill amt = C = ( A - B )</td><td class="r b">{{ amt(mb.c) }}</td></tr>
		{% else %}
		<tr><th style="width:5%">Sr.No</th><th>Description</th><th style="width:9%">HSN/SAC<br>Code</th><th style="width:8%">Qty</th>
			<th style="width:8%">Unit</th><th style="width:12%">Rate</th><th style="width:13%">Amt</th></tr>
		{% for row in doc.items %}
		<tr class="ms"><td class="c">{{ row.idx }}</td><td>{{ (row.description | striptags | trim) or row.item_name }}</td><td class="c">{{ row.gst_hsn_code or "" }}</td>
			<td class="c">{{ "%g" | format(row.qty) }}</td><td class="c">{{ row.uom }}</td>
			<td class="r">{{ amt(row.rate) }}</td><td class="r">{{ amt(row.amount) }}</td></tr>
		{% endfor %}
		{% set span = 5 %}
		<tr class="tot"><td></td><td colspan="5" class="r">Current bill amt = C</td><td class="r b">{{ amt(doc.net_total) }}</td></tr>
		{% endif %}
		{% for t in doc.taxes | selectattr("tax_amount") | sort(attribute="description") %}
		<tr class="tot"><td></td>
			{% if is_pi and loop.last %}<td class="b">(S.T.Category - Works Contract)</td><td colspan="{{ span - 1 }}" class="r">
			{% else %}<td colspan="{{ span }}" class="r">{% endif %}Add {{ t.description }} @{{ "%g" | format(t.rate) }} % on C</td><td class="r">{{ amt(t.tax_amount) }}</td></tr>
		{% endfor %}
		<tr class="tot"><td></td><td colspan="{{ span }}" class="r b">Total with Taxes</td><td class="r b">{{ amt(doc.rounded_total or doc.grand_total) }}</td></tr>
		<tr><td colspan="{{ span + 2 }}" class="b" style="font-size:13.5px; border-left:0">Rupees : {{ words }}</td></tr>
		<tr>
			<td colspan="{{ span - 2 }}" class="b" style="padding:10px 0 4px 42px !important; font-size:11.5px; line-height:1.55; vertical-align:top">
				GSTIN - {{ gstin }}<br>PAN NO : {{ gstin[2:12] }}<br>MSME NO : UDYAM-MH-19-0127149<br>
				<span style="font-size:12.5px">Bank Name - Kotak Mahindra Bank</span><br>Branch - Andheri West<br>A/c - 0346148312<br>IFSC - KKBK0000962</td>
			<td colspan="4" style="vertical-align:top; padding:10px 4px 2px">
				<div class="b" style="font-size:13px">FOR M/S SAGAR&nbsp; LIFTS</div>
				<div style="height:92px"></div>
				<div class="serif" style="font-size:15px">Authorised Signatory</div></td>
		</tr>
		<tr><td colspan="{{ span + 2 }}" class="b" style="font-size:11px">Goods are despatched at consignee's risk.Interest will be charged @15 p.a. on all overdue account.Payment requested by<br>cheque or draft payable at Mumbai.Subject to Mumbai Jurisdiction.</td></tr>
		<tr><td colspan="{{ span + 2 }}" class="b" style="font-size:11px">Declaration : - We declare that this invoice shows the actual price of the goods &amp; service described and that<br>all particulars are true and goods &amp; service described and that all particulars are true and correct.</td></tr>
	</table>
	{% if is_pi %}<div class="b" style="margin:4px 0 0 4px; font-size:13px">Note : - We will give you tax invoice After Received Payment</div>{% endif %}
</div>
"""

PRINT_FORMATS = {
	"Sagar Lifts Delivery Challan": ("Delivery Note", CHALLAN_HTML),
	"Sagar Lifts Purchase Order": ("Purchase Order", PO_HTML),
	"Sagar Lifts Invoice": ("Sales Invoice", INVOICE_HTML),
}


def setup_print_formats():
	# renamed to "Sagar Lifts Invoice" once it covered Proformas too
	frappe.delete_doc_if_exists("Print Format", "Sagar Lifts Tax Invoice")
	for name, (doctype, html) in PRINT_FORMATS.items():
		doc = frappe.get_doc("Print Format", name) if frappe.db.exists("Print Format", name) else frappe.new_doc("Print Format")
		doc.update({
			"name": name,
			"__newname": name,
			"doc_type": doctype,
			"module": "sagar-lifts",
			"standard": "No",
			"custom_format": 1,
			"print_format_type": "Jinja",
			"html": html,
		})
		doc.save(ignore_permissions=True)
		frappe.make_property_setter(
			{"doctype": doctype, "doctype_or_field": "DocType", "property": "default_print_format",
			 "value": name, "property_type": "Data"},
			is_system_generated=True,
		)
