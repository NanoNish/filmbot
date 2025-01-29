from huggingface_hub import InferenceClient
from data_models import Shots, Script
import json
import os
from openai import AzureOpenAI
from huggingface_hub import InferenceClient


endpoint = os.getenv("ENDPOINT_URL")

subscription_key = os.getenv(
    "AZURE_OPENAI_API_KEY"
)

chat_client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=subscription_key,
    api_version="2024-05-01-preview",
)

image_client = AzureOpenAI(
    api_version="2024-02-01",
    api_key=subscription_key,
    azure_endpoint=endpoint,
)

hf_api_key = os.getenv("HF_API_TOKEN")
hf_client = InferenceClient(api_key=hf_api_key)

def call_gpt_4o(prompt, sys_prompt=""):
    try:
        chat_prompt = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    }
                ],
            }
        ]

        completion = chat_client.chat.completions.create(
            model="gpt-4o-mini", messages=chat_prompt
        )

        return completion.choices[0].message.content
    except Exception as e:
        print(e)
        return ""

def call_dall_e(prompt):
    try:
        result = image_client.images.generate(
            model="dall-e-3",  # the name of your DALL-E 3 deployment
            prompt=prompt,
            n=1,
        )

        image_url = json.loads(result.model_dump_json())["data"][0]["url"]
        # return "https://dalleproduse.blob.core.windows.net/private/images/9857c792-a04a-4934-88f3-4c8b4bcab221/generated_00.png?se=2025-01-27T03%3A20%3A03Z&sig=waekdyaVCrH3xr0exLWPPsASkcrgOERhdFrdn03jLto%3D&ske=2025-01-30T18%3A23%3A22Z&skoid=09ba021e-c417-441c-b203-c81e5dcd7b7f&sks=b&skt=2025-01-23T18%3A23%3A22Z&sktid=33e01921-4d64-4f8c-a055-5bdaffd5e33d&skv=2020-10-02&sp=r&spr=https&sr=b&sv=2020-10-02"
        return image_url
    except Exception as e:
        print(e)
        return "https://dalleproduse.blob.core.windows.net/private/images/68a7f3f4-6476-47c0-998d-d7c667a67b3f/generated_00.png?se=2025-01-27T02%3A33%3A34Z&sig=QGPhIfcyjthJ9uQIBNd4vbpJDh5ua%2BrUJ8erIv8UvU0%3D&ske=2025-01-31T13%3A27%3A06Z&skoid=09ba021e-c417-441c-b203-c81e5dcd7b7f&sks=b&skt=2025-01-24T13%3A27%3A06Z&sktid=33e01921-4d64-4f8c-a055-5bdaffd5e33d&skv=2020-10-02&sp=r&spr=https&sr=b&sv=2020-10-02"

def call_hf_model(prompt):
    image = hf_client.text_to_image(
        "Astronaut riding a horse", model="stabilityai/stable-diffusion-3.5-large"
    )
    return image

def modify_uploaded_script(uploaded_script):
    full_prompt = f"""
You are a creative screenwriter tasked with editing and improving a film script. Please adhere to the following script:

The old script is as follows:
{uploaded_script}

Modify the screenplay to  for a short film with following instructions:
- Keep true to the old script
- For each shot include dialogues between characters, actions, and camera directions if necessary.
- Fill the unmentioned fields with relevant information

Output in json dump of Script pydantic model which is defined as follows:
class Shot(BaseModel):
    description: str
    dialogues: List[str] = []
    camera_action: str = "" | camera movement like panning
    action: str = "" | describe the characters movement in the shot if any

class MainCharacter(BaseModel):
    name: str
    dressing_style: str | explaig character's dressing sense
    background: str | explain about the character

class Script(BaseModel):
    title: str
    additional_info: str = ""
    main_characters: List[MainCharacter]
    shots: List[Shot]

Only output the json dump.
"""

    try:
        response = call_gpt_4o(full_prompt)
        script = Script(**json.loads(response[7:-3]))
        return script
    except Exception as e:
        response = '```json\n{\n  "title": "The Roar of Stories",\n  "additional_info": "A heartwarming tale of wisdom passed through generations, exploring the themes of courage, legacy, and connection.",\n  "main_characters": [\n    {\n      "name": "Leo",\n      "dressing_style": "Majestic, with a golden mane flowing under the sun, exuding strength and leadership.",\n      "background": "A young, charismatic lion, the current leader of the pride and a gifted storyteller of the savannah."\n    },\n    {\n      "name": "Nia",\n      "dressing_style": "Soft and playful, with a lighter tawny coat, full of energy and curiosity.",\n      "background": "A young lion cub, full of life and wonder, eager to learn about her place in the world."\n    }\n  ],\n  "shots": [\n    {\n      "description": "The sun begins to set over the savannah, painting the sky in hues of orange and pink. Leo and Nia sit on a small hill, overlooking the vast land.",\n      "dialogues": [\n        "Nia: Daddy, tell me a story!",\n        "Leo: Ah, my little one. Which story do you wish to hear today?",\n        "Nia: The one of the brave lion who faced the storm!"\n      ],\n      "camera_action": "wide shot, capturing the expansive savannah and the setting sun.",\n      "action": "Nia nudges Leo playfully while Leo smiles, reminiscing."\n    },\n    {\n      "description": "Leo leans closer to Nia, his eyes sparkling with memories. The camera zooms in.",\n      "dialogues": [\n        "Leo: Once, there was a lion just like me, living in a time of great storms...",\n        "Nia: What did he do?"\n      ],\n      "camera_action": "close-up on Leo\'s face, emphasizing his wise expression.",\n      "action": "Leo gestures with his paw, drawing the scene in the air."\n    },\n    {\n      "description": "The scene transitions to a flashback. A younger Leo stands against dark clouds, bravely facing the wind.",\n      "dialogues": [\n        "Younger Leo: I will not back down! My pride needs me!"\n      ],\n      "camera_action": "dynamic shots of the storm swirling around younger Leo, enhancing the intensity.",\n      "action": "Younger Leo roars defiantly at the storm."\n    },\n    {\n      "description": "Returning to present, Nia\'s eyes are wide with admiration.",\n      "dialogues": [\n        "Nia: Did he win?",\n        "Leo: It wasn\'t about winning. It was about protecting those he loved."\n      ],\n      "camera_action": "medium shot, focusing on Nia\'s captivated expression.",\n      "action": "Leo gently pats Nia with his paw, encouraging her."\n    },\n    {\n      "description": "Nia looks towards the horizon, the last rays of sunlight glimmering as the stars begin to appear.",\n      "dialogues": [\n        "Nia: I want to be brave like him!",\n        "Leo: Courage comes in many forms, my dear."\n      ],\n      "camera_action": "pan to the dusk sky, then back to Leo and Nia.",\n      "action": "Nia stands tall, mimicking a brave lion while Leo watches her proudly."\n    },\n    {\n      "description": "The story comes to a close as the night envelops the savannah. Leo and Nia are silhouetted against the moonlight.",\n      "dialogues": [\n        "Nia: Will you tell me more stories tomorrow?",\n        "Leo: Always, my little cub. Stories are the heartbeats of the pride.",\n        "Nia: I can\'t wait!"\n      ],\n      "camera_action": "wide shot, capturing the bond between them in the quiet night.",\n      "action": "They snuggle together, surrounded by the sounds of the night."\n    }\n  ]\n}\n```'
        script = Script(**json.loads(response[7:-3]))
        return script


def generate_ai_script(prompt, additional_info, genres):
    full_prompt = f"""
You are a creative screenwriter tasked with generating an engaging film script. Please adhere to the following structure:

Story Outline: {prompt}
Genre(s): {','.join(genres)}
Additional Information: {additional_info}


Generate a screenplay for a short film with following instructions:

Separate the story into 5-6 shots.
For each shot include dialogues between characters, actions, and camera directions if necessary.
Maintain a clear narrative flow with rising tension, a climax, and a resolution.
Be detailed and creative while ensuring the script feels authentic to human emotions and storytelling.

Output in json dump of Script pydantic model which is defined as follows:
class Shot(BaseModel):
    description: str
    dialogues: List[str] = []
    camera_action: str = "" | camera movement like panning
    action: str = "" | describe the characters movement in the shot if any

class MainCharacter(BaseModel):
    name: str
    dressing_style: str | explaig character's dressing sense
    background: str | explain about the character

class Script(BaseModel):
    title: str
    additional_info: str = ""
    main_characters: List[MainCharacter]
    shots: List[Shot]

Only output the json dump.
"""

    try:
        response = call_gpt_4o(full_prompt)
        script = Script(**json.loads(response[7:-3]))
        return script
    except Exception as e:
        response = '```json\n{\n  "title": "The Tale of the Brave Cub",\n  "additional_info": "A heartwarming story about courage told from a father\'s perspective.",\n  "main_characters": [\n    {\n      "name": "Leo",\n      "dressing_style": "Majestic and powerful, with a golden mane that glistens under the sun.",\n      "background": "A wise and experienced lion, Leo is the protector of the pride and a storyteller at heart."\n    },\n    {\n      "name": "Cubby",\n      "dressing_style": "Fuzzy and playful, with soft, light brown fur and large curious eyes.",\n      "background": "Leo\'s adventurous cub, eager to learn about the world and prove his bravery."\n    }\n  ],\n  "shots": [\n    {\n      "description": "Leo and Cubby resting under a large tree in the savanna.",\n      "dialogues": [\n        "Cubby: Dad, tell me a story!",\n        "Leo: Alright, but this isn\'t just any story. It\'s about bravery."\n      ],\n      "camera_action": "slow zoom in on Leo\'s face as he begins to speak",\n      "action": "Leo shifts slightly, positioning himself to face Cubby."\n    },\n    {\n      "description": "Leo begins the tale, the background shifts to a vibrant jungle scene.",\n      "dialogues": [\n        "Leo: Once upon a time, there was a young cub who wanted to be the strongest.",\n        "Cubby: Was it me, Dad?"\n      ],\n      "camera_action": "cut to a colorful animated flashback",\n      "action": "Leo gestures with his paw to emphasize the storytelling."\n    },\n    {\n      "description": "The scene shows a fierce competition among young animals.",\n      "dialogues": [\n        "Leo: The cub faced many challenges—defeating a mighty tiger was one of them.",\n        "Cubby: Who won, Dad?"\n      ],\n      "camera_action": "pan over the young animals contest",\n      "action": "Images of the tiger lurking in the shadows flash across the screen."\n    },\n    {\n      "description": "The tension builds as the young cub prepares to confront the tiger.",\n      "dialogues": [\n        "Leo: The cub felt fear but remembered his mother\'s advice: \'Courage is not the absence of fear.\'",\n        "Cubby: What did he do next?"\n      ],\n      "camera_action": "tight shot on Leo\'s intense expression",\n      "action": "Leo leans closer, his voice lowering for suspense."\n    },\n    {\n      "description": "The cub gathers its strength and faces the tiger in a dramatic standoff.",\n      "dialogues": [\n        "Leo: With a roar, the cub charged and surprised the tiger. The entire jungle gasped!",\n        "Cubby: Did he win? Did he?"\n      ],\n      "camera_action": "dynamic cut to the battle scene, intense music builds",\n      "action": "Leo stands up, mimicking the cub\'s fierce charge."\n    },\n    {\n      "description": "The story concludes as they return to the tranquil savanna.",\n      "dialogues": [\n        "Leo: In the end, it wasn’t just strength, but his heart that made him the bravest.",\n        "Cubby: I want to be brave like that too, Dad!"\n      ],\n      "camera_action": "pull back to reveal the vast savanna as the sun sets",\n      "action": "Leo nuzzles Cubby lovingly, their silhouettes glowing in the sunset."\n    }\n  ]\n}\n```'
        script = Script(**json.loads(response[7:-3]))
        return script


def modify_script(old_script, feedback):
    full_prompt = f"""
You are a creative screenwriter tasked with editing and improving a film script. Please adhere to the following structure:

The old script is as follows:
{old_script.model_dump_json()}

However the script had the following feedback:
{feedback}

Alter the screenplay for a short film with following instructions:
- Keep true to the old script
- Take feedback into heavy consideration

Output in json dump of Script pydantic model which is defined as follows:
class Shot(BaseModel):
    description: str
    dialogues: List[str] = []
    camera_action: str = "" | camera movement like panning
    action: str = "" | describe the characters movement in the shot if any

class MainCharacter(BaseModel):
    name: str
    dressing_style: str | explaig character's dressing sense
    background: str | explain about the character

class Script(BaseModel):
    title: str
    additional_info: str = ""
    main_characters: List[MainCharacter]
    shots: List[Shot]

Only output the json dump.
"""

    try:
        response = call_gpt_4o(full_prompt)
        script = Script(**json.loads(response[7:-3]))
        return script
    except Exception as e:
        return old_script


def generate_character_image(dressing_style, background):
    prompt = background + " " + dressing_style
    url = call_dall_e(prompt)
    return url


def generate_shot_images(shot, characters):
    chars = ""
    for char in characters:
        chars += f"{char.name} is {char.background}. "
    prompt = prompt = (
        f"A cinematic film shot depicting {shot.description} with camera movement described as {shot.camera_action}. The characters are {chars}"
    )
    url = call_dall_e(prompt)
    url1 = call_dall_e(prompt)
    url2 = call_dall_e(prompt)
    return [url, url1, url2]
