"""
# OpenAI Chat Completions Serialization Example

## Description
This code snippet demonstrates how to serialize the response from the OpenAI Chat Completions API into a JSON format which is useful for sending using REST.
It includes a helper function, `serialize_completion`, that takes the completion response object and converts it into a JSON-compatible dictionary.

## Usage
To use this code, you will need to have a .env file in the same directory as this script with your openai key:
OPENAI_API_KEY = "sk-your_key_here"

Author
@CivilEngineerUK

Date
05-12-2023
"""

import json
import openai
from dotenv import load_dotenv

load_dotenv()
client = openai.OpenAI()

def serialize_completion(completion):
    return {
        "id": completion.id,
        "choices": [
            {
                "finish_reason": choice.finish_reason,
                "index": choice.index,
                "message": {
                    "content": choice.message.content,
                    "role": choice.message.role,
                    "function_call": {
                        "arguments": json.loads(
                            choice.message.function_call.arguments) if choice.message.function_call and choice.message.function_call.arguments else None,
                        "name": choice.message.function_call.name
                    } if choice.message and choice.message.function_call else None
                } if choice.message else None
            } for choice in completion.choices
        ],
        "created": completion.created,
        "model": completion.model,
        "object": completion.object,
        "system_fingerprint": completion.system_fingerprint,
        "usage": {
            "completion_tokens": completion.usage.completion_tokens,
            "prompt_tokens": completion.usage.prompt_tokens,
            "total_tokens": completion.usage.total_tokens
        }
    }


prompt = "Write an informative story about Leonard Euler flying a hang-glider."

completion = client.chat.completions.create(
    model='gpt-4-1106-preview',
    messages=[
        {"role": "user", "content": prompt},
    ],
)

print(serialize_completion(completion))

"""
{
  "id": "chatcmpl-8SLnOloVnfshTHyeZW9zayg0ZxVnF",
  "choices": [
    {
      "finish_reason": "stop",
      "index": 0,
      "message": {
        "content": "In the lush valleys of the Swiss countryside, in a realm of history that defies the shackles of time, let us envision a story that marries the grandeur of 18th-century intellectual exploration with the thrill of modern adventure sports. Here, the great mathematician and physicist of the Enlightenment, Leonhard Euler, is about to take a curious leap into the realm of the impossible: flying a hang-glider.\n\nThe year was none, for this event never occurred in history, but in our tale, it might be perceived as a sunny day in the mid-1700s, with the air crisp and the sky a canvas of soft azure blue. Euler, having dedicated much of his life to mathematics, physics, and astronomy, was a man who understood the laws of nature like few others in his time.\n\nImagine his inquisitive mind, fueled by discoveries and theorems that resonate through time, now taken by the idea of human flight—a concept that had captivated humankind since the myth of Icarus. Euler, despite having lost vision in one eye due to an intense bout with fever, and later in life in the other eye, didn't lose his vision for exploration.\n\nOur story finds Euler in a rustic field, encompassed by the Swiss Alps, which offered the perfect setting for his newest intellectual pursuit: the dynamics of hang-gliding. Euler's fascination wasn't with the act of thrill-seeking, but rather with the physics of lift, drag, and air currents. To him, the hang-glider was not merely a recreational device but a practical illustration of his beloved mathematical principles in action.\n\nThe hang-glider itself, not as refined as the ones we see today, was a rudimentary construction of canvas and wood, resembling the sketches and ideas of early aviation pioneers like Leonardo da Vinci. Euler approached the contraption with both trepidation and awe, surveying its form and questioning the sanity of his endeavor.\n\nAmong Euler's entourage was a group of devoted students and fellow scholars, who were as intrigued as they were concerned about this unusual foray into practical experimentation. Euler reassured them with a quiet confidence, the sort that comes from an intimate knowledge of the fundamental forces governing their universe. He explained the principles of aerodynamics and the necessary conditions for sustained flight to his rapt audience.\n\nThe moment of truth arrived. Euler, having calculated the optimal point of launch considering wind velocity and direction, strapped himself into the harness of the hang-glider. With a nod to his assistants, he was pushed forward, running down the gentle slope until the ground abruptly ceased to be beneath his feet.\n\nFor a brief, heart-stopping moment, Euler was aloft, buoyed by the invisible currents he had long theorized about. The wind filled the canvas wings, and Euler—for the first time in his illustrious career—experienced the physical manifestation of his equations. His mind and heart soared in tandem, with the fields and the mountains sweeping by below, a testament to the potential of human intellect and ingenuity.\n\nUnfortunately, as all earthbound flights go, Euler's airborne excursion was brief. The winds shifted, reminding those present of the capriciousness of the elements. Euler, sensing the change, prepared for descent using his understanding of vectors and airflow to control the glide downward with surprising grace. He landed safely, his heart racing with the exhilaration of flight, his mind ablaze with new hypotheses.\n\nAs he stood there on solid ground, Euler's face wore an expression of triumph. His venture into hang-gliding, though imaginary in our historical context, emphasized the timeless truth that the pursuit of knowledge is not confined to dusty books and dark observatories—it also belongs in the open air, where ideas can literally take flight.\n\nThis blend of reality and fiction reminds us of the indomitable human spirit to push beyond the boundaries of the known world and the endless contributions of a mind as brilliant as Euler's to the collective wisdom of mankind. Even today, Euler's work continues to resonate in fields as diverse as engineering, computer science, and yes, in the principles that allow hang-gliders to soar gracefully across the sky.",
        "role": "assistant",
        "function_call": None
      }
    }
  ],
  "created": 1701767658,
  "model": "gpt-4-1106-preview",
  "object": "chat.completion",
  "system_fingerprint": "fp_a24b4d720c",
  "usage": {
    "completion_tokens": 839,
    "prompt_tokens": 20,
    "total_tokens": 859
  }
}
"""