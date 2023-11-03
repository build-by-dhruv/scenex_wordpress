from tkinter import filedialog
from tkinter.filedialog import askopenfile
import tkinter as tk
from tkinter import ttk
from woocommerce import API
import openai
import woocommerce
from jinaai import JinaAI
import json
import base64
import requests
import os
from dotenv import load_dotenv
import concurrent.futures
import threading
import random
import ast
import time


# Load environment variables from the .env file
load_dotenv()



uri = os.getenv("URI")
user = os.getenv("USER")
password = os.getenv("PASSWORD")
consumer_key = os.getenv("consumer_key")
consumer_secret = os.getenv("consumer_secret")
SCENEX_GENERATED_SECRET = os.getenv('SCENEX_GENERATED_SECRET')
# autentication_key = os.getenv("AUTENTICATION_KEY")  # Uncomment this line if you want to use this variable
api_key_input = os.getenv('OPENAI_API')


login_data={
    'uri':uri,
    'user':user,
    'password':password,
}




def generate_json_for_tag(text_content):
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





def generate_json_for_cloth(text_content):
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
        Also the cloth is never a bed sheet  , or any other ulitily cloth than an wearable dress .
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
    global task_completed , consumer_secret , consumer_key
    # Initialize the WooCommerce API
    wcapi = API(
        url='https://rosettaai-7ed033.ingress-erytho.ewp.live',
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        version="wc/v3"
    )

    def generate_dress_name(dress_dict):
        # Check if 'type_of_dress' is in the dictionary and not set to 'none'
        if 'type_of_dress' in dress_dict and dress_dict['type_of_dress'].lower() != 'none':
            dress_type = dress_dict['type_of_dress'].replace(' ', '_')  # Replace spaces with underscores for the name
            random_number = random.randint(100000, 999999)  # Generate a 6-digit random number
            return f"{dress_type}_{random_number}"
        else:
            # 'type_of_dress' is not in the dictionary or is set to 'none', so generate a default name
            random_number = random.randint(10000, 99999)  # Generate a 5-digit random number
            return f"dress_{random_number}"
        
    dress_name = generate_dress_name(json_final)

    # Upload an image to WordPress (replace with your actual upload_image_to_wordpress function)
    img_link, img_id = upload_image_to_wordpress(cloth_image_path, dress_name )

    # Define the product data with the base64-encoded image
    data = {
        "name": dress_name,
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
    # task_complted +=1
    return post_response





def get_path_listdict():
    global folder_path
    sub_folders = os.listdir(folder_path)

    # empty list to put path 
    data_list = []

    for sub_folder_name in sub_folders:
        sub_folder_path = os.path.join(folder_path, sub_folder_name)
        image_files = os.listdir(sub_folder_path)

        # Ensure there are at least two image files in the subfolder
        if len(image_files) >= 2:
            cloth_image_path = os.path.join(sub_folder_path, image_files[0])
            tag_image_path = os.path.join(sub_folder_path, image_files[1])

            # Create a dictionary with only "cloth_image_path" and "tag_image_path"
            data_entry = {
                "cloth_image_path": cloth_image_path,
                "tag_image_path": tag_image_path
            }

            data_list.append(data_entry)

    return data_list
    # Print the list of dictionaries
    # for data_entry in data_list:
    #     print("Data Entry:")
    #     print("Cloth Image Path:", data_entry["cloth_image_path"])
    #     print("Tag Image Path:", data_entry["tag_image_path"])
    #     print("\n")




def main():

    global root  ,  total_dress , log_text
    

    update_log(log_text, f'Started.....\nData posted ({task_completed}/Calculating)')

    def worker(dress_path_dict):
        global    task_completed
        # print('Started')
        # timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        # update_log(log_text, f' Started')

        cloth_image_explanation=scenex_image_expanation_for_cloth(file_path=dress_path_dict['cloth_image_path'])
        clot_detail_dict_str = generate_json_for_cloth(text_content=cloth_image_explanation )
        tag_image_explanation = scenex_image_expanation_for_tag(file_path=dress_path_dict['tag_image_path'])
        tag_detail_dict_str = generate_json_for_tag(text_content=tag_image_explanation)


        merged_dict = {**ast.literal_eval(clot_detail_dict_str), **ast.literal_eval(tag_detail_dict_str)}
        post_details = upload_product_to_woocommerce(json_final  = merged_dict, cloth_image_path = dress_path_dict['cloth_image_path'])
        print(post_details)

        # time.sleep(4)

        task_completed +=1
        update_log(log_text,log_message=f'Started.....\nData posted ({task_completed}/{total_dress})')
    # create_ui()
    cloth_list_dict  = get_path_listdict()

    total_dress = len(cloth_list_dict)

    # Define the number of workers you want to run in parallel
    max_workers = 3

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:

        # Submit worker tasks for each dictionary in cloth_list_dict
        future_to_dict = {executor.submit(worker, some_dict): some_dict for some_dict in cloth_list_dict}
    # Wait for all tasks to complete
    concurrent.futures.wait(future_to_dict)
    # update_log(log_text, log_message=f'Processing in batch of 5 \nTask completed: ({task_complted/total_dress}) ')

    




# Access the variables
task_completed = 0
total_dress = 0
log_text  = None

global folder_path
cloth_image_path = ""
cloth_tag_path = ""


def update_log(log_text, log_message):
    log_text.delete(1.0, tk.END)
    log_text.insert(tk.END, log_message + "\n")  # Add the log message to the Text widget
    log_text.see(tk.END)  # Scroll to the end of the text

def create_ui():
    global root
    global folder_path
    global log_text

    cloth_image_path = ""
    cloth_tag_path = ""
    folder_path = ""

    root = tk.Tk()
    root.geometry("600x400")  # Larger window size
    root.resizable(False, False)
    root.title("Upload Cloth")

    def upload_cloth():
        global folder_path
        folder_path = filedialog.askdirectory()
    
    style = ttk.Style()
    style.configure("TButton", padding=10, font=("Arial", 12))
    style.map("TButton",
              foreground=[('active', 'black')],
              background=[('active', '#1E90FF')])

    # Create a frame to hold the buttons
    button_frame = tk.Frame(root)
    button_frame.pack(pady=20)

    main_btn = ttk.Button(
        button_frame,
        text="Select Main Cloth Image",
        command=upload_cloth,
        style="TButton",
    )
    main_btn.grid(row=0, column=0, padx=10, pady=5)

    def run_function_in_background():
        sub_btn.config(state="disabled")

        # Create a separate thread to run the long-running function
        thread = threading.Thread(target=main)
        thread.start()
    sub_btn = ttk.Button(
        button_frame,
        text="Confirm",
        command=run_function_in_background,  # Use a function as the command
        style="TButton",
    )
    sub_btn.grid(row=1, column=0, padx=10, pady=5)

    # Create a frame to display logs
    log_frame = tk.Frame(root)
    log_frame.pack(pady=10)

    # Create a Text widget for displaying log messages
    log_text = tk.Text(log_frame, width=50, height=10, wrap=tk.WORD )
    log_text.pack(padx=10, pady=10)

    return root


if __name__ == "__main__":

    # Outside of create_ui function, you can call the function and use the returned Tk instance and Text widget to update the log messages:
    root = create_ui()  
    root.mainloop()

