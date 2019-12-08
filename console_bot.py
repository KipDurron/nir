def start_console_bot():
    flag = True

    while flag:
        user_response = input()

        user_response = user_response.lower()
        if user_response != 'пока':
            if sampling(user_response) is not None:
                answer = sampling(user_response)
            else:
                answer = response(user_response)
            print(answer)
        else:
            flag = False


start_console_bot()