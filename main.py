import openai

def initialize_openai_api(api_key):
    """
    Initialize the OpenAI API client with the given API key.
    
    :param api_key: API key for OpenAI.
    """
    openai.api_key = api_key

def generate_repair_proposal(prompt_text, api_key):
    """
    Generate structured repair proposals using GPT-4 based on text input.

    :param prompt_text: Text to process with GPT-4.
    :param api_key: API key for OpenAI.
    :return: Generated proposal text.
    """
    initialize_openai_api(api_key)
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an AI trained to create structured repair proposals."},
            {"role": "user", "content": prompt_text}
        ],
        max_tokens=2048
    )
    return response.choices[0].message.content if response.choices else ""

def analyze_image_with_gpt4(image_data, question, api_key):
    """
    Analyze an image using GPT-4 with Vision and return the analysis result.

    :param image_data: Base64 encoded string of the image or URL to the image.
    :param question: Question or description prompt for the image analysis.
    :param api_key: API key for OpenAI.
    :return: Analysis result from GPT-4.
    """
    initialize_openai_api(api_key)
    response = openai.ChatCompletion.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": question},
                    {"type": "image", "data": image_data}
                ]
            }
        ],
        max_tokens=300
    )
    return response.choices[0].message.content if response.choices else ""
