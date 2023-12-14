import http.client
import os
import sys
import openai
import subprocess

# Hardcoded API keys (Replace with your actual keys for testing)
OPENAI_API_KEY = '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'
ATTOM_DATA_API_KEY = '1c69e1c6a6036307e2abfac26ea55fc5'

# Setting the API keys
openai.api_key = OPENAI_API_KEY

# Now you can use openai.api_key and ATTOM_DATA_API_KEY in your application


def format_address(address):
  """Formats the address to be URL-friendly. This function takes a string address as input and returns a URL-encoded version of the address."""
  return address.replace(" ", "%20")


def get_property_data(street_address, city_state_zip, api_key):
  """Retrieves property data from Attom Data API."""
  conn = http.client.HTTPSConnection("api.gateway.attomdata.com")
  headers = {'accept': "application/json", 'apikey': api_key}

  formatted_address1 = format_address(street_address)
  formatted_address2 = format_address(city_state_zip)

  endpoints = [
      "/propertyapi/v1.0.0/property/detail?address1={}&address2={}".format(
          formatted_address1, formatted_address2)
  ]
  property_data = {}

  for endpoint in endpoints:
    try:
      conn.request("GET", endpoint, headers=headers)
      res = conn.getresponse()
      data = json.loads(res.read().decode("utf-8"))
      property_data[endpoint] = data
    except Exception as e:
      sys.stderr.write(f"Error retrieving data from {endpoint}: {e}\n")
      return None

  return property_data


def preprocess_property_data(raw_data):
  """Preprocesses and formats the raw property data for GPT-4."""
  if not raw_data:
    return "No data available for the given address."

  formatted_data = []

  for endpoint, data in raw_data.items():
    if 'property' in data and data['property']:
      property_info = data['property'][
          0]  # Assuming the first item is relevant
      formatted_str = "Address: {}\nYear Built: {}\nLot Size: {} sqft\nBuilding Size: {} sqft\nBedrooms: {}\nBathrooms: {}\n".format(
          property_info.get('address', {}).get('oneLine', 'N/A'),
          property_info.get('summary', {}).get('yearbuilt', 'N/A'),
          property_info.get('lot', {}).get('lotsize2', 'N/A'),
          property_info.get('building',
                            {}).get('size', {}).get('universalsize', 'N/A'),
          property_info.get('building', {}).get('rooms',
                                                {}).get('beds', 'N/A'),
          property_info.get('building', {}).get('rooms',
                                                {}).get('bathstotal', 'N/A'))
      formatted_data.append(formatted_str)

  return "\n".join(formatted_data)



def generate_property_report(formatted_data):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "user", "content": formatted_data}
            ],
            model="gpt-3.5-turbo"  # or "gpt-4" based on your preference
        )
        return chat_completion.choices[0].text
    except Exception as e:
        sys.stderr.write(f"Error generating report: {e}\n")
        return "Unable to generate report due to an error."




def handle_user_query(query, context):
  try:
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{
            "role": "system",
            "content": "You are a knowledgeable assistant."
        }, {
            "role": "user",
            "content": context
        }, {
            "role": "user",
            "content": query
        }])
    return response.choices[0].message['content']
  except Exception as e:
    sys.stderr.write(f"Error handling user query: {e}\n")
    return "Sorry, I couldn't process your query."


class InteractivePropertySession:

  def __init__(self, initial_context):
    self.context = initial_context
    self.conversation_history = []

  def update_context(self, new_context):
    self.context = new_context

  def add_message_to_history(self, role, content):
    self.conversation_history.append({"role": role, "content": content})

  def ask_question(self, question):
    self.add_message_to_history("user", question)
    try:
      response = openai.ChatCompletion.create(
          model="gpt-4",
          messages=[{
              "role":
              "system",
              "content":
              "You are a knowledgeable assistant about real estate properties."
          }, {
              "role": "user",
              "content": self.context
          }, *self.conversation_history, {
              "role": "user",
              "content": question
          }])
      answer = response.choices[0].message['content']
      self.add_message_to_history("assistant", answer)
      return answer
    except Exception as e:
      sys.stderr.write(f"Error during conversation: {e}\n")
      return "Sorry, I couldn't process your query."


# Example usage:
# session = InteractivePropertySession(initial_context=formatted_property_info)
# print(session.ask_question("Tell me about the schools in this area"))
# print(session.ask_question("Any recent renovations?"))
# print(session.ask_question("What is the history of renovations for this property?"))


import openai

def main():
    print("Welcome to the Property Information Assistant!")

    # Get user input for address
    street_address = input("Enter the street address (e.g., 123 Main St): ")
    city_state_zip = input("Enter the city, state, and ZIP code (e.g., Anytown, CA 12345): ")

    # Retrieve and process property data
    print("Fetching and processing property data...")
    property_data = get_property_data(street_address, city_state_zip, ATTOM_DATA_API_KEY)
    formatted_data = preprocess_property_data(property_data)
    if not formatted_data:
        print("Failed to retrieve or process property data.")
        return

    # Generate property report using GPT-4
    print("Generating property report...")
print("Calling generate_property_report...")
report = generate_property_report(formatted_data)
print("Report generated. Checking contents...")


    # Save the report to a file
file_name = f"{street_address.replace(' ', '_')}_{city_state_zip.replace(' ', '_').replace(',', '')}.txt"
with open(file_name, 'w') as file:
        file.write(report)
print(f"Report saved to {file_name}")

    # Interactive query session
print("\nYou can now ask specific questions about the property. Type 'exit' to end the session.")
while True:
        user_query = input("Your question: ")
        if user_query.lower() == 'exit':
            print("Session ended. Thank you for using the Property Information Assistant.")
            break


response = openai.ChatCompletion.create(
          model="gpt-3.5-turbo",  # or "gpt-4"
          messages=[
              {"role": "system", "content": "You are a knowledgeable assistant."},
              {"role": "user", "content": report},
              {"role": "user", "content": user_query}
          ]
      )

answer = response.choices[0].message['content']
print("Answer:\n", answer)

if __name__ == "__main__":
    main()
