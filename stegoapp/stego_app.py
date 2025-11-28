from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import numpy as np
import io
import uuid
import uvicorn

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

END_MARKER = b'<<<END>>>'

# ---------------- HTML ---------------- #
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Image Steganography</title>
    <style>
        body {font-family: Arial; background: #f2f2f2; padding: 40px;}
        .box {background: white; padding: 20px; width: 400px; margin: auto;
              border-radius: 10px; box-shadow: 0 0 10px #ccc;}
        button {padding: 10px 20px; background: black; color: white;
                border: none; cursor: pointer; margin-top: 10px; border-radius: 5px;}
        input, textarea {width: 100%; padding: 10px; margin-top: 8px; border-radius: 5px;}
        img {margin-top: 15px; width: 100%; border-radius: 10px;}
    </style>
</head>

<body>
<div class="box">
    <h2>Encode Message</h2>
    <input type="file" id="encodeImage">
    <textarea id="secret" placeholder="Enter secret message"></textarea>
    <button onclick="encode()">Encode</button>
    <h3>Encoded Image:</h3>
    <a id="downloadLink" style="display:none" download>Download Encoded Image</a>
    <img id="encodedPreview" />
</div>

<br><br>

<div class="box">
    <h2>Decode Message</h2>
    <input type="file" id="decodeImage">
    <button onclick="decode()">Decode</button>
    <h3>Hidden Message:</h3>
    <p id="decodedMessage"></p>
</div>

<script>
async function encode() {
    let img = document.getElementById("encodeImage").files[0];
    let msg = document.getElementById("secret").value;

    let form = new FormData();
    form.append("image", img);
    form.append("message", msg);

    let res = await fetch("/encode", { method: "POST", body: form });
    let blob = await res.blob();

    // Show encoded image
    let imgUrl = URL.createObjectURL(blob);
    document.getElementById("encodedPreview").src = imgUrl;

    // Show download link
    let link = document.getElementById("downloadLink");
    link.href = imgUrl;
    link.style.display = "block";
    link.innerText = "Download Encoded Image";
}

async function decode() {
    let img = document.getElementById("decodeImage").files[0];

    let form = new FormData();
    form.append("image", img);

    let res = await fetch("/decode", { method: "POST", body: form });
    let data = await res.json();
    document.getElementById("decodedMessage").innerText = data.message;
}
</script>
</body>
</html>
"""

# ---------------- Encode/Decode Functions ---------------- #
def message_to_bits(message_bytes):
    return ''.join(f'{b:08b}' for b in message_bytes)

def encode_image_array(img, message):
    arr = np.array(img.convert("RGBA"), dtype=np.uint8)
    flat = arr.flatten().astype(np.int32)

    bits = message_to_bits(message.encode() + END_MARKER)
    if len(bits) > flat.size:
        raise ValueError("Message too large for this image")

    for i in range(len(bits)):
        flat[i] = (flat[i] & ~1) | int(bits[i])

    encoded_arr = flat.reshape(arr.shape).astype(np.uint8)
    return Image.fromarray(encoded_arr, 'RGBA')

def decode_image_array(img):
    arr = np.array(img.convert("RGBA"), dtype=np.uint8)
    flat = arr.flatten()
    bits = ''.join(str(b & 1) for b in flat)
    ba = bytearray()
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) < 8: break
        ba.append(int(byte, 2))
        if ba.endswith(END_MARKER):
            return ba[:-len(END_MARKER)].decode('utf-8', errors='ignore')
    return None

# ---------------- Routes ---------------- #
@app.get("/", response_class=HTMLResponse)
def home():
    return HTML_PAGE

@app.post("/encode")
async def encode_api(image: UploadFile = File(...), message: str = Form(...)):
    img = Image.open(image.file)
    encoded_img = encode_image_array(img, message)
    buf = io.BytesIO()
    encoded_img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="image/png",
        headers={"Content-Disposition": f"attachment; filename=stego_{uuid.uuid4().hex}.png"}
    )

@app.post("/decode")
async def decode_api(image: UploadFile = File(...)):
    img = Image.open(image.file)
    hidden_message = decode_image_array(img)
    return JSONResponse({"message": hidden_message or "No hidden message found."})

# ---------------- Run App ---------------- #
if __name__ == "__main__":
    uvicorn.run("stego_app:app", host="127.0.0.1", port=8000, reload=True)