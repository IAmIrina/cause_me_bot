# Interaval repeting word Bot

## Entrypoints

Entrypoints:
- main.process_event: telegram web hook to handler messages from users: register, add new words and etc.
- main.remind: entrypoint to run notification part (timer trigger runs the part) 

The database schemas will be created at the first "/start" command from any user if it doesn't exist.

## Infrastracture

- YDB - authorization with ydb.iam.MetadataUrlCredentials, so you should link service account with YDB access to the serverless function which will invoke YDB connection (entrypoint  main.process_event)
- Serverless public function with entrypoint main.process_event. Url set up on telegram webhook (https://api.telegram.org/bot.../setWebhook).
- Serverless function with entrypoint main.remind. Run byt triggers one time a day. Send notification.
- Yandex Translate: you need to get token for your service account and than set it in enviroments.
- Yandex Dictionary: you can get token here https://yandex.com/dev/dictionary/ and than set it  in enviroments.
- Telegram messager: set up your bot token in enviroments.

# ENV example
DICTIONARY_TOKEN=dict.1.1....c
TELEGRAM_TOKEN=6275882280:AAH...c
TRANSLATE_TOKEN=AQVNxffIMW-rE...G
YDB_DATABASE=/ru-central1/b1g6251p1o0qlsnpmlq3/e...c

