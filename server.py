from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import numpy as np
import cv2
import os
from io import BytesIO
from PIL import Image

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"]
    }
})

#``members api route 
@app.route("/members")
def members():
    return {"members": ["Member1", "Member2", "Member3"]}

@app.route("/")
def home():
    return {"message": "Welcome to the API! Try /members to see the members list."}

# Load the pre-trained colorization model
prototxt = "colorization_deploy_v2.prototxt"
model = "colorization_release_v2.caffemodel"
points = "pts_in_hull.npy"

# Load the model
net = cv2.dnn.readNetFromCaffe(prototxt, model)
pts = np.load(points)

# Add the cluster centers as 1x1 convolutions to the model
class8 = net.getLayerId("class8_ab")
conv8 = net.getLayerId("conv8_313_rh")
pts = pts.transpose().reshape(2, 313, 1, 1)
net.getLayer(class8).blobs = [pts.astype("float32")]
net.getLayer(conv8).blobs = [np.full([1, 313], 2.606, dtype="float32")]

@app.route("/colorize", methods=["POST"])
def colorize():
    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    # Load the input image from the uploaded file
    file = request.files["image"]
    image = Image.open(file.stream)
    image = np.array(image)

    if image.ndim == 2 or image.shape[2] == 1:  # Ensure the image is 3-channel
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    scaled = image.astype("float32") / 255.0
    lab = cv2.cvtColor(scaled, cv2.COLOR_BGR2LAB)

    # Extract the L channel
    L = cv2.split(lab)[0]
    L -= 50

    # Predict the ab channels
    net.setInput(cv2.dnn.blobFromImage(L))
    ab = net.forward()[0, :, :, :].transpose((1, 2, 0))

    # Resize the predicted ab channels to match the input image size
    ab = cv2.resize(ab, (image.shape[1], image.shape[0]))

    # Combine L channel with predicted ab channels
    L = cv2.split(lab)[0]
    colorized = np.concatenate((L[:, :, np.newaxis], ab), axis=2)

    # Convert back to BGR color space
    colorized = cv2.cvtColor(colorized, cv2.COLOR_LAB2BGR)
    colorized = np.clip(colorized, 0, 1)

    # Convert to 8-bit integers
    colorized = (255 * colorized).astype("uint8")

    # Convert the colorized image to a format Flask can send
    _, buffer = cv2.imencode(".jpg", colorized)
    response = BytesIO(buffer)

    # Return the colorized image
    return send_file(
        response,
        mimetype="image/jpeg",
        as_attachment=True,
        download_name="colorized_image.jpg",
    )

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)