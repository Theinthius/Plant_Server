import os
import time
import base64
from flask import Flask, request, jsonify
import openai

app = Flask(__name__)

# --- Load OpenAI key safely ---
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    print("WARNING: OPENAI_API_KEY environment variable not set!")
    print("Set it with 'set OPENAI_API_KEY=your_key_here' in this terminal.")
    # You can uncomment the next line to stop execution if you want strict requirement
    # raise ValueError("OPENAI_API_KEY environment variable not set!")

@app.route('/')
def home():
    return "Plant AI server is running."

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        # Get raw JPEG bytes
        image_data = request.data
        if not image_data:
            return jsonify({"error": "No image received"}), 400

        # Save image locally (optional)
        save_folder = os.path.dirname(os.path.abspath(__file__))
        filename = f"photo_{int(time.time())}.jpg"
        filepath = os.path.join(save_folder, filename)
        with open(filepath, "wb") as f:
            f.write(image_data)

        # Convert to base64
        image_b64 = base64.b64encode(image_data).decode('utf-8')

        if not openai.api_key:
            return jsonify({"error": "OPENAI_API_KEY not set. Cannot call OpenAI."}), 500

        # Call OpenAI Responses API
        response = openai.responses.create(
            model="gpt-4.1-mini",
            input=[{
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Analyze this leaf image. "
                            "If the plant is healthy, reply ONLY 'Your plant is OK'. "
                            "If diseased, reply 'Your plant is diseased: [disease name], cure: [instructions]'."
                        )
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{image_b64}"
                    }
                ]
            }]
        )

        description = response.output_text.strip()
        return jsonify({"description": description})

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"Starting server on port {port}...")
    app.run(host="0.0.0.0", port=port)
