from io import BytesIO
from pathlib import Path
import sys
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A6

root = Path(__file__).resolve().parents[1]
qr = qrcode.make('https://example.test/checkin/MMKDEMO?sig=abc123')
buf = BytesIO(); qr.save(buf, format='PNG'); assert buf.getvalue().startswith(b'\x89PNG')
pdf = BytesIO(); c=canvas.Canvas(pdf, pagesize=A6); c.drawString(20,100,'MMK Demo Ticket'); c.showPage(); c.save(); assert pdf.getvalue().startswith(b'%PDF')
print('QR artifact smoke test: PASSED')
print('PDF artifact smoke test: PASSED')
