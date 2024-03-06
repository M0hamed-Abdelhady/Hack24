import copy
import json
import sys
import warnings
from time import sleep
import requests
import numpy as np
import LSBSteg as LSBSteg
from LSBSteg import SteganographyException
from riddle_solvers import *

api_base_url = "http://3.70.97.142:5000"
team_id = "kNgGFJe"
warnings.filterwarnings("ignore")


def init_fox(team_id):
    """
    In this function you need to hit to the endpoint to start the game as a fox with your team id.
    If a sucessful response is returned, you will recive back the message that you can break into chunkcs
    and the carrier image that you will encode the chunk in it.
    """
    response = requests.post(api_base_url + "/fox/start", json={"teamId": team_id})
    response_data = response.json()
    message = response_data["msg"]
    print(f"Message: {message}")
    return [np.array(response_data["carrier_image"]), message]


def solving_problems():
    current_fake = 0
    test_case = get_riddle(team_id, "problem_solving_easy")
    sol = solve_problem_solving_easy(test_case)
    sleep(0.5)
    if solve_riddle(team_id, sol):
        current_fake += 1

    test_case = get_riddle(team_id, "problem_solving_medium")
    sol = solve_problem_solving_medium(test_case)
    sleep(0.5)
    if solve_riddle(team_id, sol):
        current_fake += 2

    test_case = get_riddle(team_id, "problem_solving_hard")
    sol = solve_problem_solving_hard(test_case)
    sleep(0.5)
    if solve_riddle(team_id, sol):
        current_fake += 3

    test_case = get_riddle(team_id, "sec_medium_stegano")
    sol = solve_sec_medium(test_case)
    sleep(0.5)
    if solve_riddle(team_id, sol):
        current_fake += 2
    return current_fake


# generate one chunk
def generate_message_array(message, image_carrier) -> np.array:
    """
    In this function you will need to create your own startegy. That includes:
        1. How you are going to split the real message into chunks
        2. Include any fake chunks
        3. Decide what 3 chunks you will send in each turn in the 3 channels & what is their entities (F,R,E)
        4. Encode each chunk in the image carrier
    """
    encoded_np_image = LSBSteg.encode(np.array(image_carrier), message)
    return np.array(encoded_np_image)


def get_riddle(team_id, riddle_id):
    """
    In this function you will hit the api end point that requests the type of riddle you want to solve.
    use the riddle id to request the specific riddle.
    Note that:
        1. Once you requested a riddle you cannot request it again per game.
        2. Each riddle has a timeout if you didnot reply with your answer it will be considered as a wrong answer.
        3. You cannot request several riddles at a time, so requesting a new riddle without answering the old one
          will allow you to answer only the new riddle and you will have no access again to the old riddle.
    """
    response = requests.post(
        api_base_url + "/fox/get-riddle",
        json={"teamId": team_id, "riddleId": riddle_id},
    )
    if response.status_code == 200:
        response_data = response.json()
        # print(f"get_riddle: {response_data}")
        return response_data["test_case"]
    else:
        print(f"get_riddle: {response.status_code} | {response.text}")


def solve_riddle(team_id, solution):
    """
    In this function you will solve the riddle that you have requested.
    You will hit the API end point that submits your answer.
    Use te riddle_solvers.py to implement the logic of each riddle.
    """
    response = requests.post(
        api_base_url + "/fox/solve-riddle",
        json={"teamId": team_id, "solution": solution},
    )
    if response.status_code == 200:
        res_data = response.json()
        print(f"solve_riddle: [budget increase: {res_data}")
        if res_data["status"] == "success":
            return True
        else:
            return False
    else:
        print(f"solve_riddle: {response.status_code} | {response.text}")
        return False


def send_message(
        team_id, messages, message_entities
):  # messages must be np.array  =["F", "E", "R"]
    """
    Use this function to call the api end point to send one chunk of the message.
    You will need to send the message (images) in each of the 3 channels along with their entites.
    Refer to the API documentation to know more about what needs to be send in this api call.
    """

    response = requests.post(
        api_base_url + "/fox/send-message",
        json={
            "teamId": team_id,
            "messages": [messages[0].tolist(), messages[1].tolist(), messages[2].tolist()],
            "message_entities": message_entities,
        }
    )
    if response.status_code == 200:
        res_data = response.json()
        print(f"send_message: {res_data}")
    else:
        print(f"send_message: {response.status_code} | {response.text}")


def end_fox(team_id):
    """
    Use this function to call the api end point of ending the fox game.
    Note that:
    1. Not calling this function will cost you in the scoring function
    2. Calling it without sending all the real messages will also affect your scoring fucntion
      (Like failing to submit the entire message within the timelimit of the game).
    """
    response = requests.post(api_base_url + "/fox/end-game", json={"teamId": team_id})
    if response.status_code == 200:
        res_data = response.json()
        print(f"end_fox: {res_data}")
    else:
        print(f"end_fox: {response.status_code} | {response.text}")


def submit_fox_attempt(team_id):
    """
    Call this function to start playing as a fox.
    You should submit with your own team id that was sent to you in the email.
    Remeber you have up to 15 Submissions as a Fox In phase1.
    In this function you should:
        1. Initialize the game as fox
        2. Solve riddles
        3. Make your own Strategy of sending the messages in the 3 channels
        4. Make your own Strategy of splitting the message into chunks
        5. Send the messages
        6. End the Game
    Note that:
        1. You HAVE to start and end the game on your own. The time between the starting and ending the game is taken into the scoring function
        2. You can send in the 3 channels any combination of F(Fake),R(Real),E(Empty) under the conditions that
            2.a. At most one real message is sent
            2.b. You cannot send 3 E(Empty) messages, there should be at least R(Real)/F(Fake)
        3. Refer To the documentation to know more about the API handling
    """
    with open('output.txt', 'w') as f:
        sys.stdout = f
        tmp = init_fox(team_id)
        carrier_image, msg = tmp[0], tmp[1]
        real_0 = copy.deepcopy(carrier_image)
        real_1 = copy.deepcopy(carrier_image)
        real_2 = copy.deepcopy(carrier_image)
        fake_0 = copy.deepcopy(carrier_image)

        # print(carrier_image)
        print(str(carrier_image.tolist()))
        print('\n\n')
        print(msg)

        current_fake = solving_problems()
        real_msg_channel = [0, 2, 1, 0, 1]
        chunks = 1
        l, r = 0, 4

        real_message_0 = generate_message_array(message=msg[:7], image_carrier=real_0)
        real_message_1 = generate_message_array(message=msg[7:14], image_carrier=real_1)
        real_message_2 = generate_message_array(message=msg[14:], image_carrier=real_2)
        fake_message_0 = generate_message_array(message="faka", image_carrier=fake_0)

        messages = [np.array(real_message_0), np.array(fake_message_0), np.array(fake_message_0)]
        channels = ["R", "F", "F"]
        send_message(team_id, messages=messages, message_entities=channels)

        messages = []
        channels = []
        messages = [np.array(fake_message_0), np.array(real_message_1), np.array(fake_message_0)]
        channels = ["F", "R", "F"]
        send_message(team_id, messages=messages, message_entities=channels)

        messages = []
        channels = []
        messages = [np.array(fake_message_0), np.array(real_message_2), np.array(fake_message_0)]
        channels = ["F", "R", "F"]
        send_message(team_id, messages=messages, message_entities=channels)

        # for i in range(chunks):
        #     encoded_msg = generate_message_array(
        #         message=msg, image_carrier=carrier_image
        #     )
        #     messages = [0] * 3
        #     channels = ["0"] * 3
        #     l += 4
        #     r += 4
        #     messages[real_msg_channel[i]] = encoded_msg
        #     channels[real_msg_channel[i]] = "R"
        #     for j in range(3):
        #         if j == real_msg_channel[i]:
        #             continue
        #         messages[j] = carrier_image
        #         channels[j] = "E"
        #     send_message(team_id, messages=messages, message_entities=channels)
        end_fox(team_id)
    sys.stdout = sys.__stdout__


submit_fox_attempt(team_id)
print("Finished!")
