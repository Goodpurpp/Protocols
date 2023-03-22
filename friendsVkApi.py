import csv
import json
import time
from argparse import ArgumentParser
from art import tprint

import requests

with open("token.txt", "r") as file:
    token = file.readline()


def get_user_friends(user_id):
    return requests.get("https://api.vk.com/method/friends.get?user_id=210700286&v=5.52",
                        params={
                            'access_token': token,
                            'user_id': user_id,
                            'v': 5.131
                        }).json()


def get_user_info(user_id):
    return requests.get("https://api.vk.com/method/users.get?user_id=210700286&v=5.52",
                        params={
                            'access_token': token,
                            'user_id': user_id,
                            'v': 5.131
                        }).json()


def parse_and_write_csv(data, count):
    counter = 1
    with open("friends.csv", "w") as file:
        a_pen = csv.writer(file, delimiter=",")
        a_pen.writerow(('first name', 'last name'))
        tprint('first name', 'last name', sep=" ")
        for user in data:
            try:
                friend_info = get_user_info(user)['response'][0]
                print(friend_info['first_name'], friend_info['last_name'], sep=" ")
                a_pen.writerow((friend_info['first_name'], friend_info['last_name']))
                counter += 1
                if counter % 5 == 0:
                    time.sleep(0.5)
            except KeyError:
                pass
    print("Saved in friends.csv!")


def main():
    parser = ArgumentParser(description="Парсер друзей по user_id")
    parser.add_argument("-id", type=int, help="Айди юзера в VK")
    arguments = parser.parse_args()
    tprint("VK  FRIENDS  PARSER")
    info = get_user_friends(arguments.id)['response']
    parse_and_write_csv(info['items'], info['count'])


if __name__ == "__main__":
    main()
