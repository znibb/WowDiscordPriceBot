# WowDiscordPriceBot

## Setup
1. Clone this repo somewhere appropriate: `git clone -b master https://github.com/znibb/WowDiscordPriceBot.git`
1. Go to `http://discordapp.com/developers/applications`
1. Create a new application
1. Go to `Bot` sub menu and create a bot user
1. Copy `.env-template` to `.env`
1. Copy the bot TOKEN and paste into the `.env` file
1. Go to `OAuth2` sub menu
1. In `SCOPES` select `bot` and in `BOT PERMISSIONS` select `View Channels`, `Send Message`, `Manage Messages` and `Embed Links`
1. Copy the generated URL and paste it into your web browser of choice
1. Select which server to add bot user to
1. From the repo dir, run `docker-compose up -d`

## Pull profession database updates
1. git submodule update --remote

## Changelog
### 2.0.2
#### Bug fixes
- Changed the mats for Enchant Cloak - Subtlety to the BCC ones

### 2.0.1
#### Bug fixes
- Enabled logging to console for easier fault tracing

### 2.0.0
#### Features added
- Included BCC crafts/enchants

### 1.2.0
#### Features added
- Added command "craftwrit" which shows prices for completing "Craftman's Writ" quests if both the writ and items are purchased from the AH

### 1.1.0
#### Features added
- Added command aliases.

#### Bug fixes
- Querying for craftprice for something that's not craftable now throws 'no match' error instead of 'unknown' error.
- Removed duplicate "Cloak Dodge" enchant.

### 1.0.4
#### Bug fixes
- Now handles names containing brackets or colons correctly.

### 1.0.3
#### Bug fixes
- Fixed craftprice not taking into consideration that some crafts generate multiples of an item.

### 1.0.2
#### Bug fixes
- Updated error messages to reflect the correct command prefix.
- Increased verbosity slightly for `enchantprice` error message.

### 1.0.1
#### Bug fixes
- Fixed craft price not considering the amount of a reagent into the total price.

### 1.0.0
- Initial release.
