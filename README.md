# Telegram Bot for interval repeting words

## Entrypoints

Entrypoints:
- main.process_event: telegram web hook to handler messages from users: register, add new words and etc.
- main.remind: entrypoint to run notification part (timer trigger runs the part) 

The database schemas will be created at the first "/start" command from any user if it doesn't exist.

## infrastructure

- YDB - authorization with ydb.iam.MetadataUrlCredentials, so you should link service account with YDB access to the serverless function which will invoke YDB connection (entrypoint  main.process_event)
- Serverless public function with entrypoint main.process_event. Url set up on telegram webhook (https://api.telegram.org/bot.../setWebhook).
- Serverless function with entrypoint main.remind. Run by triggers one time a day. Send notification.
- Yandex Translate: you need to get token for your service account and than set it in enviroments.
- Yandex Dictionary: you can get token here https://yandex.com/dev/dictionary/ and than set it  in enviroments.
- Telegram messager: set up your bot token in enviroments.
- ChatGPT API: generation short texts with studing words. Using gpt-3.5-turb model because of good quality price ratio. You can get ChatGPT API token here https://platform.openai.com/account/api-keys.

## Settings
    Set all tokens  via env variables.
    Set languages for your instance using env:
    - YOUGLISH_LANGUAGE=english 
    - YOUGLISH_ACCENT=us
    You can get your languages and accents from youglish URL. For example, you have url https://youglish.com/pronounce/vrienden/dutch/nl, then you should take "ducth" as a language and "nl" as an accent.

    - TRANSLATE_SOURCE_LANGUAGE_CODE=en
    - TRANSLATE_TARGET_LANGUAGE_CODE=ru
    Language codes for the translate, Yandex Translate API is used now, so you can find possible values for your language in yandex translate API documentation https://cloud.yandex.com/en-ru/docs/translate/concepts/supported-languages.
    - DICTIONARY_SOURCE_LANGUAGE_CODE=en
    - DICTIONARY_TARGET_LANGUAGE_CODE=ru
    Language codes for dictionary, you can find documentation here https://yandex.com/dev/dictionary.

    You can enable/disable creating text examples with env CHATGPT_ON (True or False).
    
    You can enable/disable additional meanings  with env DICTIONARY_ON(True or False)

## ENV example
- DICTIONARY_TOKEN=dict.1.1....c
- TELEGRAM_TOKEN=6275882280:AAH...c
- TRANSLATE_TOKEN=AQVNxffIMW-rE...G
- YDB_DATABASE=/ru-central1/b1g6251p1o0qlsnpmlq3/e...c
- PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
- CHATGPT_TOKEN=sk-B...i

- CHATGPT_ON=True 
- TRANSLATE_SOURCE_LANGUAGE_CODE=en
- TRANSLATE_TARGET_LANGUAGE_CODE=ru

- DICTIONARY_ON=True
- DICTIONARY_SOURCE_LANGUAGE_CODE=en
- DICTIONARY_TARGET_LANGUAGE_CODE=ru

- YOUGLISH_LANGUAGE=english
- YOUGLISH_ACCENT=us

## Manual
Telegram user commands:
- /start: start telegram bot, create data base schema if it doesn't exist and add user to table users
- /help: send user a text constant from messages.HELP
- /more: send user word that the user should repeat
When a user starts the bot and then sends message, he gets translate of the word or phrase and a button ADD. If he presses the button ADD, the word is added to the list of his words.

Telegram admin commands:
- /register: set telegram user commands using setMyCommands API endpoint. Telegam suggests the command to user when user put "/" into the message field and e.i.

