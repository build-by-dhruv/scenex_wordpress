import openai
import woocommerce
from jinaai import JinaAI
import json
import base64
import requests
from woocommerce import API
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Access the variables

uri = os.getenv("URI")
user = os.getenv("USER")
password = os.getenv("PASSWORD")
SCENEX_GENERATED_SECRET = os.getenv('SCENEX_GENERATED_SECRET')
# autentication_key = os.getenv("AUTENTICATION_KEY")  # Uncomment this line if you want to use this variable
api_key_input = os.getenv('OPENAI_API')


login_data={
    'uri':uri,
    'user':user,
    'password':password,
}


def generate_json_for_tag(text_content, api_key_input):
    # openai.api_key = "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"
    openai.api_key = api_key_input
    system_message="""
                    You are a assitant and clothes expert by given a paragraph or context you use your extreme knowledge 
                    to extract brand and size, you always give json response
                    example {"brand":"nikee",
                    "size":"x/xl/32/..", 
                    }
                    """
    # try:
    messages=[
            {"role": "system", "content":system_message},
            {
                "role": "assistant",
                "content": 
                            """
                            I am a cloth specialist and a fashion designer.give me context i'll give json response
                            """,
            },
            {
                "role": "user",
                "content": 
                            f"""
                            i'll give you images of cloth and you have to extract size , color ,brand name from the image in a json format
                            instead of size small , large , extra large use short for like S,L ,XL ,M , XXl
                            json format - "color":"mehrun","size":"m","brand":"nike"
                            "color":"mehrun","size":"m","brand":"none"
                            if you will not able to detect any of these return None 
                            note :
                            your response only should be a valid json no other text. Text content ->{text_content}       
                            """,
            },
        ]
    print(messages)
    completion1 = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        # model="gpt-4"
        # ,
        messages=messages,
        temperature=0.9,
        # max_tokens=15000,
    )
    data_for_next_filter = completion1["choices"][0]["message"]["content"]
    print(data_for_next_filter)
    return data_for_next_filter





def generate_json_for_cloth(text_content, api_key_input):
    # openai.api_key = "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"
    openai.api_key = api_key_input
    # try:
    completion1 = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        # model="gpt-4",
        messages=[
            {
                "role": "assistant",
                "content": """
            I am a cloth specialist and a fashion designer.
            Your goal is to analyse given text and response with an out 
            """,
            },
            {
                "role": "user",
                "content": f"""
                Your goal is to analyse given text and response with an output with json .
                I don't need any explanation just give me the json response nothing else , if you have something to pay put in key "explanation":"your explanaiton"
        I want to u analyze the text and must be able to define some characteristics of the item such as Type of Garment, Season of wearing, Gender, and color.

        <"{text_content}">
        you just need to return a json with format 
            
            "type_of_dress":"here contain  type of dress"
            "season":"here contains the season that garment can be wore select summer or winter"
            "gender":"here contain the gender of the cloth male or female"
            "color":"contain the dominant color of the cloth"
        
        Analyze yourself and assign it audience as either male or female.
        Remember to give me single values in all key mappings
        Also, analyze it twice and make decision of what season the cloth is right for and assign it
    
        And remember the audience can either Male or Female nothing else
        double check all conditions with the result before giving me in form of a json file.        
                """,
            },
        ],
        temperature=0.9,
        # max_tokens=15000,
    )
    data_for_next_filter = completion1["choices"][0]["message"]["content"]
    print("GPT response for Main Cloth:\n", data_for_next_filter)

    return data_for_next_filter





def image_to_data_uri(file_path):
    with open(file_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
        return f"data:image/jpeg;base64,{encoded_image}"
    
def scenex_image_expanation_for_cloth(file_path):
    # Initialize the JinaAI client with your authentication secrets
    jinaai = JinaAI(
    secrets = {
    'scenex-secret': SCENEX_GENERATED_SECRET
    }
    )

    # Convert the image from file path to data URI
    image_path = file_path
    image_data_uri = image_to_data_uri(image_path)

    # Set the options for the describe method
    options = {
        'languages': ['en'] , # Assuming you want the response in English
        'output_length':300
    }

    # Get the description of the image
    description = jinaai.describe(image_data_uri, options)


    # Print the JSON response
    print(description['results'])

    cloth_image_explanation = description['results'][0]['output']
    return cloth_image_explanation



def scenex_image_expanation_for_tag(file_path):
    # Initialize the JinaAI client with your authentication secrets
    jinaai = JinaAI(
    secrets = {
    'scenex-secret': SCENEX_GENERATED_SECRET
    }
    )

    # Convert the image from file path to data URI
    image_path = file_path
    image_data_uri = image_to_data_uri(image_path)

    # Set the options for the describe method
    options = {
        'languages': ['en'] , # Assuming you want the response in English
        # 'output_length':300
    }

    # Get the description of the image
    description = jinaai.describe(image_data_uri, options)


    # Print the JSON response
    print(description['results'])

    cloth_image_explanation = description['results'][0]['output']
    return cloth_image_explanation




def upload_image_to_wordpress(image_path, image_name):
    uri = login_data['uri']
    user = login_data['user']
    password = login_data['password']
    
    creds = f"{user}:{password}"
    token = base64.b64encode(creds.encode('utf-8')).decode('utf-8')


    # Step 1: Upload the image to WordPress media library
    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()

    image_upload_endpoint = f'{uri}/media'
    image_headers = {
        'Authorization': f'Basic {token}',
    }
    image_data_payload = {
        'file': (f"{image_name}.png", image_data, 'image/png'),  # Adjust filename and MIME type accordingly
    }

    response = requests.post(image_upload_endpoint, files=image_data_payload, headers=image_headers)
    print(response)
    
    # Check the response status code
    if response.status_code == 201:
        try:
            response_data = response.json()
            image_url = response_data.get('source_url')
            image_id = response_data.get('id')
            if image_url and image_id:
                print(f"Image uploaded successfully! Image ID: {image_id}, Image URL: {image_url}")
                return image_url, image_id
            else:
                print(f"Unexpected response format: {response_data}")
        except ValueError:
            print("Error parsing JSON response. The response may not be in JSON format.")




def upload_product_to_woocommerce(json_final , cloth_image_path):
    # Initialize the WooCommerce API
    wcapi = API(
        url='https://rosettaai-7ed033.ingress-erytho.ewp.live',
        consumer_key='ck_f4009ee61d8a8f6a6a5e419e1579af9a017c8200',
        consumer_secret='cs_e360672ee21eaff01f2980d2a5a13f0398c0f777',
        version="wc/v3"
    )

    # Upload an image to WordPress (replace with your actual upload_image_to_wordpress function)
    img_link, img_id = upload_image_to_wordpress(cloth_image_path, "qwerty" )

    # Define the product data with the base64-encoded image
    data = {
        "name": "testing",
        "status": "draft",
        "type": "simple",
        # "regular_price": "21.99",
        "description": f'<strong>Type of Garment</strong>: {json_final["type_of_dress"]}\n\n<strong>Brand</strong>: {json_final["brand"].title()}\n\n<strong>Color</strong>: {json_final["color"].title()}\n\n<strong>Gender</strong>: {json_final["gender"].title()}\n\n<strong>Season</strong>: {json_final["season"].title()}\n\n<strong>Size</strong>: {json_final["size"].title()}',
        "short_description": f'<strong>Type of Garment</strong>: {json_final["type_of_dress"]}\n\n<strong>Brand</strong>: {json_final["brand"].title()}\n\n<strong>Color</strong>: {json_final["color"].title()}\n\n<strong>Gender</strong>: {json_final["gender"].title()}\n\n<strong>Season</strong>: {json_final["season"].title()}\n\n<strong>Size</strong>: {json_final["size"].title()}',
        "categories": [
            {
                "id": 14
            }
        ],
        "images": [
            {
                "src": str(img_link)  # Include the base64-encoded image data
            }
        ],
        "attributes": [
            {
                "name": "Color",
                "options": json_final["color"]
            },
            {
                "name": "Brand",
                "options": json_final["brand"]
            },
            {
                "name": "Season",
                "options": json_final["season"]
            },
            {
                "name": "Size",
                "options": json_final["size"]
            },
            {
                "name": "Gender",
                "options": json_final["gender"]
            },
            {
                "name":"Type of Garment",
                "Options": json_final["type_of_dress"]
            }
        ]
    }



    post_response = wcapi.post("products", data).json()
    print(post_response)
    return post_response

