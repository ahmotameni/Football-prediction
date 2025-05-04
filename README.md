# Club World Cup 2025 Prediction Bot

A Telegram bot built for friendly match predictions during the 2025 FIFA Club World Cup. Users can predict match scores, earn points based on prediction accuracy, and compete on a live leaderboard. Ideal for private groups of friends or family.

---

## ✨ Features
- Score predictions for both group and knockout stages
- Inline keyboards (no typing needed)
- Scoring based on correctness (winner, goal diff, etc.)
- Manual + API-based result input
- Live leaderboard
- Admin panel for managing matches and results
- CSV export of all data
- Cheap hosting via Heroku

---

## 🌐 Demo
*Coming soon after first deployment.*

---

## 💡 Tech Stack
- Python 3.11+
- aiogram (Telegram bot framework)
- JSON (for storage)
- pandas / csv (for exports)
- apscheduler (for scheduling)

---

## 📂 Project Structure
```
club_world_cup_bot/
|
|— bot.py                  # main entry point
|— config/
|   |— scoring_rules.py     # scoring configuration
|— handlers/
|   |— user_commands.py     # user-facing bot commands
|   |— admin_commands.py    # admin-only commands
|— keyboards/
|   |— prediction_keyboard.py
|— messages/
|   |— strings.py           # user-facing text messages
|— services/
|   |— prediction.py        # logic for prediction handling
|   |— scoring.py           # scoring engine
|   |— export_csv.py        # data export logic
|   |— api_fetch.py         # result fetching from football API
|— data/
    |— users.json
    |— predictions.json
    |— matches.json
    |— scores.csv
```

---

## 🚀 Getting Started
1. Clone this repo
2. Create a `.env` file with your `TELEGRAM_TOKEN`
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Run the bot locally:
```bash
python bot.py
```
5. Deploy to Heroku:
```bash
heroku create
heroku config:set TELEGRAM_TOKEN=your_token_here
heroku stack:set container
git push heroku main
```

---

## 🏆 Scoring System
You can customize the scoring logic in `config/scoring_rules.py`. All calculations are done dynamically using these rules.

---

## 🔐 Admin Commands
- `/admin` – show admin options
- `/addmatch` – manually add a new match
- `/setresult` – input final result or trigger API fetch
- `/updateleaderboard` – recalculate points
- `/exportcsv` – export all data

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
