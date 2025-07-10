import qrcode

# Only ONE QR pointing to login
qr_url = "http://localhost:5000/"  # Replace with your IP if needed
img = qrcode.make(qr_url)
img.save("static/images/table_login_qr.png")
print(f"Single QR code generated for: {qr_url}")
