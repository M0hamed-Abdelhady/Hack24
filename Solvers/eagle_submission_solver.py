import copy
import warnings
import requests
import numpy as np
from LSBSteg import *
from Model import model

api_base_url = "http://3.70.97.142:5000"
team_id = "kNgGFJe"
warnings.filterwarnings("ignore")


def init_eagle(team_id):
    """
    In this function you need to hit to the endpoint to start the game as an eagle with your team id.
    If a successful response is returned, you will receive back the first footprints.
    """
    response = requests.post(api_base_url + "/eagle/start", json={"teamId": team_id})

    print(f"init_eagle ---> {response.status_code}")
    if response.status_code < 300:
        response_data = response.json()
        return response_data["footprint"]
    else:
        return None


def select_channel(footprints):
    """
    According to the footprint you received (one footprint per channel)
    you need to decide if you want to listen to any of the 3 channels or just skip this message.
    Your goal is to try to catch all the real messages and skip the fake and the empty ones.
    Refer to the documentation of the Footprints to know more what the footprints represent to guide you in your approach.        
    """
    # max_footprints = (float(-1), float(0))
    pres = []

    for key, value in footprints.items():
        prediction = model.make_prediction(np.array(value))
        print(key, prediction)
        if prediction == 1:
            pres.append(int(key))

    # rep = 0
    # # pres.sort()
    # for i in pres:
    #     if i > 0.85:
    #         rep += 1

    if 2 > len(pres) > 0:
        id_ = pres[0] % 4
        if id_ > 0:
            return id_
        else:
            return None
    else:
        return None


def skip_msg(team_id):
    """
    If you decide to NOT listen to ANY of the 3 channels then you need to hit the end point skipping the message.
    If successful request to the end point , you will expect to have back new footprints IF ANY.
    """
    response = requests.post(api_base_url + "/eagle/skip-message", json={"teamId": team_id})

    print(f"skip_msg ---> {response.status_code}")
    if response.status_code < 300:
        response_data = response.json()
        if 'nextFootprint' in response_data:
            return response_data["nextFootprint"]
        else:
            return None
    else:
        print(f"skip_msg: {response.status_code} | {response.text}")
        return None


def request_msg(team_id, channel_id):
    """
    If you decide to listen to any of the 3 channels then you need to hit the end point of selecting a channel to hear on (1,2 or 3)
    """
    response = (
        requests.post(api_base_url + "/eagle/request-message",
                      json={
                          "teamId": team_id,
                          "channelId": int(channel_id)

                      }))
    print(f"request_msg ---> {response.status_code}")
    if response.status_code < 300:
        response_data = response.json()
        msg_ = copy.deepcopy(np.array(response_data["encodedMsg"]))
        return msg_
    else:
        print(f"request_msg: {response.status_code} | {response.text}")
        return None


def submit_msg(team_id, decoded_msg):
    """
    In this function you are expected to:
        1. Decode the message you requested previously
        2. call the api end point to send your decoded message
    If successful request to the end point , you will expect to have back new footprints IF ANY.
    """
    response = (
        requests.post(api_base_url + "/eagle/submit-message",
                      json={
                          "teamId": team_id,
                          "decodedMsg": str(decoded_msg)
                      }))

    print(f"submit_msg ---> {response.status_code}")
    if response.status_code < 300:
        response_data = response.json()
        if 'nextFootprint' in response_data:
            return response_data["nextFootprint"]
        else:
            return None
    else:
        print(f"submit_msg: {response.status_code} | {response.text}")
        return None


def end_eagle(team_id):
    """
    Use this function to call the api end point of ending the eagle  game.
    Note that:
    1. Not calling this function will cost you in the scoring function
    """
    response = requests.post(api_base_url + "/eagle/end-game", json={"teamId": team_id})
    print(f"end_eagle ---> {response.status_code}")
    if response.status_code < 300:
        res_data = response.json()
        print(f"end_eagle: {res_data}")
    else:
        print(f"end_eagle: {response.status_code} | {response.text}")


def submit_eagle_attempt(team_id):
    """
     Call this function to start playing as an eagle.
     You should submit with your own team id that was sent to you in the email.
     Remember you have up to 15 Submissions as an Eagle In phase1.
     In this function you should:
        1. Initialize the game as fox
        2. Solve the footprints to know which channel to listen on if any.
        3. Select a channel to hear on OR send skip request.
        4. Submit your answer in case you listened on any channel
        5. End the Game
    """

    footprints = 1
    footprints = init_eagle(team_id)
    while footprints:
        if footprints != 1:
            channel = select_channel(footprints)
            if channel is None:
                footprints = skip_msg(team_id)
            else:
                msg = np.array(request_msg(team_id, channel))
                decoded_msg = decode(msg)
                footprints = submit_msg(team_id, decoded_msg)
        else:
            footprints = skip_msg(team_id)

    end_eagle(team_id)


submit_eagle_attempt(team_id)
