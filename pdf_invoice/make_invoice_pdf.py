import os
import uuid
import traceback
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django_tenants.utils import schema_context

SITE_URL = "http://127.0.0.1:8000"


class UpdateReceiptUrl:
    def update_invoice(self, invoice_name, file_url, tenant_schema):
        try:
            with schema_context(tenant_schema):
                from base.models import Sale
                sale = Sale.objects.get(cis_invc_no=str(invoice_name))
                sale.generated_invoice = file_url
                sale.save()
            return "Done"
        except Sale.DoesNotExist:
            return f"Sale with invoice {invoice_name} does not exist in schema {tenant_schema}"
        except Exception as e:
            traceback.print_exc()
            return f"Error updating invoice: {str(e)}"


class InvoicePDF:
    def __init__(self, invoice_data, tenant_schema):
        self.invoice_data = invoice_data
        self.tenant_schema = tenant_schema

    def draw_nav(self, c, width, height):
        logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
        logo_width, logo_height = 2 * inch, 1 * inch
        top_y = height - 1 * inch
        try:
            logo = ImageReader(logo_path)
            c.drawImage(
                logo,
                width - logo_width - 1 * inch,
                top_y - logo_height + 0.2 * inch,
                width=logo_width,
                height=logo_height,
                preserveAspectRatio=True,
                mask="auto",
            )
        except Exception:
            pass

        text_y = top_y
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(colors.black)
        c.drawString(1 * inch, text_y, self.invoice_data["company"]["name"])
        c.setFont("Helvetica", 10)
        text_y -= 0.2 * inch
        tpin = self.invoice_data["company"].get("tpin", "N/A")
        c.drawString(1 * inch, text_y, f"TPIN: {tpin}")
        text_y -= 0.2 * inch
        c.drawString(1 * inch, text_y, f"Phone: {self.invoice_data['company'].get('phone','')}")
        text_y -= 0.2 * inch
        c.drawString(1 * inch, text_y, f"Email: {self.invoice_data['company'].get('email','')}")
        c.setStrokeColor(colors.grey)
        c.setLineWidth(1)
        c.line(1 * inch, text_y - 0.2 * inch, width - 1 * inch, text_y - 0.2 * inch)
        return text_y - 0.6 * inch

    def draw_hero(self, c, width, start_y):
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1 * inch, start_y, "Bill To:")
        c.setFont("Helvetica", 10)
        cust = self.invoice_data.get("customer", {})
        c.drawString(1 * inch, start_y - 0.2 * inch, cust.get("name", ""))
        c.drawString(1 * inch, start_y - 0.4 * inch, f"TPIN: {cust.get('tpin','N/A')}")
        inv = self.invoice_data.get("invoice", {})
        c.drawRightString(width - 1 * inch, start_y, f"Invoice No: {inv.get('number','')}")
        c.drawRightString(width - 1 * inch, start_y - 0.3 * inch, f"Date: {inv.get('date','')}")
        return start_y - 0.8 * inch

    def draw_invoice_title(self, c, width, start_y):
        invoice_type = self.invoice_data.get("invoice", {}).get("type", "TAX INVOICE")
        c.setFont("Helvetica-Bold", 18)
        c.setFillColor(colors.HexColor("#2c3e50"))
        c.drawCentredString(width / 2, start_y, invoice_type)
        return start_y - 0.4 * inch

    def draw_items_table(self, c, width, start_y):
        currency = self.invoice_data.get("totals", {}).get("currency", "ZMW")
        data = [["#", "Name", "Qty", "Unit Price", f"Total ({currency})", "Tax Cat"]]
        for idx, item in enumerate(self.invoice_data["items"], start=1):
            total_value = item.get("total", item["qty"] * item["price"])
            data.append([
                str(idx),
                item.get("name", ""),
                str(item.get("qty", 0)),
                f"{item.get('price',0):.2f}",
                f"{total_value:.2f} {currency}",
                item.get("tax_type", "Standard Rated"),
            ])
        table = Table(data, colWidths=[0.5*inch,2.5*inch,0.7*inch,1*inch,1.2*inch,1.5*inch])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#2c3e50")),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("ALIGN",(0,0),(-1,-1),'CENTER'),
            ("FONTNAME",(0,0),(-1,0),'Helvetica-Bold'),
            ("FONTSIZE",(0,0),(-1,0),10),
            ("BOTTOMPADDING",(0,0),(-1,0),8),
            ("BACKGROUND",(0,1),(-1,-1),colors.whitesmoke),
            ("GRID",(0,0),(-1,-1),0.5,colors.grey)
        ]))
        table.wrapOn(c, width, start_y)
        table.drawOn(c, 1 * inch, start_y - len(data)*0.28*inch)
        return start_y - (len(data)+1)*0.28*inch

    def draw_totals(self, c, width, start_y):
        totals = self.invoice_data.get("totals", {})
        currency = totals.get("currency","ZMW")
        c.setFont("Helvetica-Bold", 10)
        y = start_y
        for label, value in [("Sub-total", totals.get("subtotal", 0)),
                             ("VAT Total", totals.get("tax", 0)),
                             ("Total Amount", totals.get("grand_total",0))]:
            c.drawString(width/2, y, label)
            c.drawRightString(width-0.5*inch, y, f"{value:,.2f} {currency}")
            y -= 0.25*inch
        return y - 0.2*inch

    def draw_sdc_info(self, c, width, start_y):
        sdc = self.invoice_data.get("sdc_info", {})
        payment = self.invoice_data.get("payment", {})
        left_x = 1*inch
        y = start_y
        c.setFont("Helvetica-Bold",12)
        c.setFillColor(colors.HexColor("#2c3e50"))
        c.drawString(left_x, y, "SDC Information")
        y_offset = 0.25*inch
        y_curr = y - y_offset
        for label, val in [
            ("Invoice Date", sdc.get('invoice_date','')),
            ("SDC ID", sdc.get('sdc_id','')),
            ("Invoice Number", sdc.get('invoice_number','')),
            ("Invoice Type", sdc.get('invoice_type','')),
            ("Payment Type", payment.get('type','Cash'))
        ]:
            c.setFont("Helvetica",8)
            c.drawString(left_x, y_curr, f"{label}: {val}")
            y_curr -= y_offset
        return y_curr - 0.6*inch

    def draw_qrcode_below_sdc(self, c, width, y_start, gap=0.7*inch):
        qr_data = self.invoice_data.get('invoice',{}).get('qrcode','')
        if qr_data:
            qr_code = qr.QrCodeWidget(qr_data)
            bounds = qr_code.getBounds()
            size = 1*inch
            scale_x = size / (bounds[2]-bounds[0])
            scale_y = size / (bounds[3]-bounds[1])
            d = Drawing(size, size, transform=[scale_x,0,0,scale_y,0,0])
            d.add(qr_code)
            x = (width - size)/2
            y = y_start - gap
            renderPDF.draw(d, c, x, y)
    
    def add_watermark(self, c, width, height):
        try:
            logo = os.path.join(os.path.dirname(__file__), "logo.png")
            wm_width, wm_height = width*0.9, height*0.9
            x, y = (width - wm_width)/2, (height - wm_height)/2
            c.saveState()
            c.setFillAlpha(0.05)
            c.drawImage(logo, x, y, width=wm_width, height=wm_height, preserveAspectRatio=True, mask='auto')
            c.restoreState()
        except: pass

    def draw_footer(self, c, width):
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(colors.grey)
        c.drawCentredString(width/2, 0.9*inch, "Powered by ZRA Smart Invoice!")
        c.drawCentredString(width/2, 0.7*inch, f"Created By: {self.invoice_data.get('created_by','Timothy Simwawa')}")

    def build_pdf(self, invoice_name):
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        self.add_watermark(c, width, height)
        hero_y = self.draw_nav(c, width, height)
        hero_y = self.draw_hero(c, width, hero_y)
        hero_y = self.draw_invoice_title(c, width, hero_y)
        totals_y = self.draw_items_table(c, width, hero_y)
        sdc_y = self.draw_totals(c, width, totals_y)
        footer_y = self.draw_sdc_info(c, width, sdc_y)
        self.draw_qrcode_below_sdc(c, width, footer_y)
        self.draw_footer(c, width)

        c.showPage()
        c.save()
        buffer.seek(0)

        # Save in Django media folder correctly
        filename = f"invoice/{uuid.uuid4()}.pdf"  # no extra 'media/'
        file_path = default_storage.save(filename, ContentFile(buffer.getvalue()))
        public_url = default_storage.url(file_path)  # will return /media/invoice/xxx.pdf

        # Update DB
        updater = UpdateReceiptUrl()
        res = updater.update_invoice(invoice_name, public_url, self.tenant_schema)
        print("Update DB result:", res)

        return public_url


class BuildPdf:
    def build_invoice(self, company_info, customer_info, invoice, items, sdc_data, payload, tenant_schema):
        company_name, company_phone, company_email, company_tpin = company_info[0]
        cust_tpin, cust_name = customer_info[0]
        invoice_number, invoice_date, invoice_type, get_qrcode_url = invoice[0]
        current_date, sdc_id = sdc_data[0]

        invoice_data = {
            "company": {
                "name": company_name,
                "phone": company_phone,
                "email": company_email,
                "tpin": company_tpin,
            },
            "customer": {
                "name": cust_name,
                "tpin": cust_tpin
            },
            "invoice": {
                "number": invoice_number,
                "date": invoice_date,
                "type": invoice_type,
                "qrcode": get_qrcode_url,
            },
            "items": [
                {
                    "name": item["itemNm"],
                    "qty": item["qty"],
                    "price": item["prc"],
                    "total": item["totAmt"],
                    "tax_type": item.get("vatCatCd", "")
                } for item in items
            ],
            "totals": {
                "subtotal": payload.get("totTaxblAmt", 0),
                "tax": payload.get("totTaxAmt", 0),
                "grand_total": payload.get("totAmt", 0),
                "currency": payload.get("currencyTyCd", "ZMW"),
            },
            "tax_details": {},
            "sdc_info": {
                "invoice_date": invoice_date,
                "sdc_id": sdc_id,
                "invoice_number": invoice_number,
                "invoice_type": "Normal invoice",
                "current_date": current_date
            },
            "payment": {"type": "Bank transfer"},
            "created_by": "Timothy Simwawa"
        }

        builder = InvoicePDF(invoice_data, tenant_schema)
        public_url = builder.build_pdf(invoice_number)
        print("PDF saved with URL:", public_url)
        return public_url
