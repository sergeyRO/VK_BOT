from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotEventType
from Bot.vkBot import vkBot
from BotDB.BotDB import BotDB


if __name__ == '__main__':
    db = BotDB()
    bot = vkBot(db)
    for event in bot.longpoll.listen():
        random_id = get_random_id()
        if event.type == VkBotEventType.MESSAGE_NEW:
            peer_id = event.object.message['peer_id']
            event_command = event.object.message['text'].lower()
            bot.bot_command(event_command, event, peer_id, random_id)

        elif event.type == VkBotEventType.MESSAGE_EVENT:
            peer_id = event.object.peer_id
            event_command = event.object.payload['type']
            bot.bot_command(event_command, event, peer_id, random_id)
