# WowDiscordPriceBot

## Setup
1. Go to `discordapp.com/developers/applications`
1. Create application
1. Go to `Bot` sub menu and create a bot user
1. Copy the bot TOKEN and paste into the `.env` file
1. Go to `OAuth2` sub menu
1. In `SCOPES` select `bot` and in `BOT PERMISSIONS` select `View Channels`, `Send Message`, `Manage Messages` and `Embed Links`
1. Copy the generated URL and paste it into your web browser of choice
1. Select which server to add bot user to
1. Run `docker-compose up -d`
