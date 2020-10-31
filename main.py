from TOKENS import group_token, user_token
from vk_search import VkBot

if __name__ == '__main__':
    print('Для начала общения с ботом напишите любое сообщение в группу')
    bot = VkBot(group_token, user_token)
    bot.vk_search()