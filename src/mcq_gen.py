import google.generativeai as genai

# Configure Google Gemini API
genai.configure(api_key="AIzaSyCjsqbMcPSRUrDjAyiP4A8UfKiI75FizG0")

# Initialize the model
model = genai.GenerativeModel('gemini-1.5-flash')


def generate_mcq(topic: str, number: int) -> str:
    """
    Generate multiple choice questions based on the given topic and number.

    Args:
        topic (str): The topic for the questions.
        number (int): The number of questions to generate.

    Returns:
        str: The generated multiple choice questions.
    """
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

        make {number} multiple choice questions of the topic {topic} in the format. 
        (four options must be meaningful and relevant to the question and do not repeat the options, if possible (needed) make solution also)
    """

    # Generate content using Google Gemini API
    response = model.generate_content(prompt)

    # Save the response to a file
    with open("response.txt", "w") as file:
        file.write(response.text)

    return response.text
