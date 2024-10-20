import google.generativeai as genai
from flask import Flask, render_template, request
from datetime import datetime

# Configure Google Gemini API
genai.configure(api_key="YOUR_API_KEY_HERE")

# Initialize the model
model = genai.GenerativeModel('gemini-1.5-flash')

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        topic = request.form.get('topic')
        number = request.form.get('number')

        # Create the prompt
        prompt = f"""
        make multiple choice question in the format:
        {{
            questions:<>
            answer:<>
            option1:<>
            option2:<>
            option3:<>
            solutions:
        }}

        make {number} multiple choice questions of the topic {topic} in the format.(four options must be meaningful and relevant to the question and do not repeat the options, if possible (needed) make solution also)
        """

        # Generate content using Google Gemini API
        response = model.generate_content(prompt)

        # Save the response to a file (optional)
        with open("response.txt", "w") as file:
            file.write(response.text)

        # Return the generated questions to the template
        return render_template('index.html', questions=response.text)

    return render_template('index.html', questions=None)

if __name__ == '__main__':
    app.run(debug=True)
