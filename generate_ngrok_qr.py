import qrcode

url = "https://858b9786364a.ngrok-free.app"  # your ngrok URL
img = qrcode.make(url)
img.save("restaurant_qr.png")
print("✅ QR code saved as restaurant_qr.png")
