# Club World Cup 2025 Prediction Bot

A Telegram bot built for friendly match predictions during the 2025 FIFA Club World Cup. Users can predict match scores, earn points based on prediction accuracy, and compete on a live leaderboard. Ideal for private groups of friends or family.

---

## ✨ Features
- Integrated match viewing and prediction interface
- Status indicators with emojis for better UX
- Score predictions for both group and knockout stages
- Inline keyboards (no typing needed)
- Scoring based on correctness (winner, goal diff, etc.)
- Points displayed alongside results for completed matches
- Manual + API-based result input
- Live leaderboard
- Admin panel for managing matches and results
- CSV export of all data
- Cloud deployment via Heroku with Firebase backend

---

## 🌐 Demo
*Coming soon after first deployment.*

---

## 💡 Tech Stack
- Python 3.11+
- aiogram (Telegram bot framework)
- Firebase Realtime Database (for cloud storage)
- pandas / csv (for exports)
- apscheduler (for scheduling)

---

## 📂 Project Structure
```
club_world_cup_bot/
|
|— bot.py                  # main entry point
|— firebase_init.py        # Firebase initialization
|— firebase_helpers.py     # Firebase database operations
|— config/
|   |— scoring_rules.py     # scoring configuration
|— handlers/
|   |— user_commands.py     # user-facing bot commands
|   |— admin_commands.py    # admin-only commands
|— keyboards/
|   |— prediction_keyboard.py
|   |— persistent_keyboard.py
|— messages/
|   |— strings.py           # user-facing text messages
|— services/
|   |— prediction.py        # logic for prediction handling
|   |— scoring.py           # scoring engine
|   |— export_csv.py        # data export logic
|   |— api_fetch.py         # result fetching from football API
```

---

## 🚀 Getting Started

### Prerequisites
1. **Firebase Setup:**
   - Create a Firebase project at [Firebase Console](https://console.firebase.google.com)
   - Enable Realtime Database in your project
   - Download the service account key JSON file
   - Save it as `serviceAccountKey.json` in the project root

2. **Telegram Bot Setup:**
   - Create a bot using [@BotFather](https://t.me/BotFather)
   - Get your bot token

### Local Development
1. Clone this repo
2. Create your credentials file:
```bash
cp credentials.env.sample credentials.env
# Edit credentials.env to add your Telegram token and admin username
```
3. Place your Firebase service account key as `serviceAccountKey.json` in the project root
4. Install dependencies:
```bash
pip install -r requirements.txt
```
5. Run the bot:
```bash
python run_bot.py
```

### Heroku Deployment
1. Base64 encode your Firebase service account key:
```bash
base64 -w 0 serviceAccountKey.json
```
2. Deploy to Heroku:
```bash
heroku create your-bot-name
heroku config:set TELEGRAM_TOKEN=your_token_here
heroku config:set ADMIN_USER_ID=your_username
heroku config:set FIREBASE_KEY=your_base64_encoded_key_here
heroku stack:set container
git push heroku main
```

---

## 🔐 Security Note
The `credentials.env` file and `serviceAccountKey.json` contain sensitive information and are excluded from version control by `.gitignore`. Never commit these files to your repository.

---

## 🗄️ Database Structure
Firebase Realtime Database structure:
```
/
├── users/
│   └── {user_id}/
│       ├── username
│       ├── first_name
│       ├── last_name
│       ├── score
│       ├── is_admin
│       ├── whitelisted
│       └── registered_at
├── matches/
│   └── {match_id}/
│       ├── team1
│       ├── team2
│       ├── time
│       ├── is_knockout
│       ├── locked
│       └── result/
│           ├── home_goals
│           ├── away_goals
│           └── resolution_type
├── predictions/
│   └── {user_id}/
│       └── {match_id}/
│           ├── home_goals
│           ├── away_goals
│           └── resolution_type
└── current_stage/
    └── current_stage
```

---

## 🏆 Scoring System
You can customize the scoring logic in `config/scoring_rules.py`. All calculations are done dynamically using these rules.

---

## 🎮 User Interface
The bot features an intuitive interface with emoji status indicators:
- ⏳ Upcoming matches ready for prediction
- ✅ Matches you've already predicted
- 🔒 Locked matches (no longer accepting predictions)
- ⚽ Ongoing matches
- 🏁 Completed matches with results

Users can view all matches, make predictions, and see their scoring results all in one interface.

---

## 🔐 Admin Commands
- Admin Panel – show admin options
- Add Match – create new matches
- Set Result – add match results
- Update Scores – recalculate points
- Export CSV – export all data
- Whitelist User – approve users to access the bot

### User Access Control
The bot implements a whitelisting system where:
- New users are automatically registered but not whitelisted
- Only whitelisted users (and admins) can access bot features
- Admins can whitelist users using `/whitelist @username`
- Non-whitelisted users see an access restriction message

---

## 📅 Planning to Extend?
- Add team photos and badges
- Create user profiles with stats
- Enable public scoreboard on web

---

## ✅ License
MIT License

---

## 🙌 Made for fun with friends and family 