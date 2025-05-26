"""
Message strings for the Club World Cup 2025 prediction bot.
"""

# General messages
WELCOME_MESSAGE = """
Welcome to the Club World Cup 2025 Prediction Bot! 🏆⚽

Make predictions for upcoming matches and compete with friends and family!

Use the command buttons below to navigate the bot.

Good luck! ⚽🍀

به ربات پیش‌بینی جام باشگاه‌های جهان 2025 خوش آمدید! 🏆⚽

پیش‌بینی‌های خود را برای مسابقات آینده انجام دهید و با دوستان و خانواده رقابت کنید!

از دکمه‌های دستوری زیر برای هدایت ربات استفاده کنید.

موفق باشید! ⚽🍀

Benvenuto al Bot di Previsioni della Coppa del Mondo per Club 2025! 🏆⚽

Fai previsioni per le partite imminenti e competi con amici e famiglia!

Usa i pulsanti dei comandi qui sotto per navigare nel bot.

Buona fortuna! ⚽🍀
"""

HELP_MESSAGE = """
Use the keyboard buttons to navigate the bot:

⚽ Matches - View all matches and make predictions
📋 My Predictions - View your current predictions
🏆 Leaderboard - View the current standings
🥇 My Rank - See your position in the leaderboard
❓ Help - Show this help message

The matches interface allows you to:
• See upcoming matches with ⏳
• Make predictions by tapping on matches
• See your predictions marked with ✅
• View results for completed matches 🏁
• Check points earned for each prediction

از دکمه‌های کیبورد برای هدایت ربات استفاده کنید:

⚽ مسابقات - مشاهده تمام مسابقات و پیش‌بینی
📋 پیش‌بینی‌های من - مشاهده پیش‌بینی‌های فعلی شما
🏆 جدول امتیازات - مشاهده رتبه‌بندی فعلی
🥇 رتبه من - مشاهده موقعیت شما در جدول امتیازات
❓ راهنما - نمایش این پیام راهنما

رابط مسابقات به شما امکان می‌دهد:
• مشاهده مسابقات آینده با ⏳
• پیش‌بینی با کلیک روی مسابقات
• مشاهده پیش‌بینی‌های شما با علامت ✅
• مشاهده نتایج مسابقات تمام شده 🏁
• بررسی امتیازات کسب شده برای هر پیش‌بینی

Usa i pulsanti della tastiera per navigare nel bot:

⚽ Partite - Visualizza tutte le partite e fai previsioni
📋 Le mie previsioni - Visualizza le tue previsioni attuali
🏆 Classifica - Visualizza la classifica attuale
🥇 Il mio rango - Vedi la tua posizione in classifica
❓ Aiuto - Mostra questo messaggio di aiuto

L'interfaccia delle partite ti permette di:
• Vedere le partite imminenti con ⏳
• Fare previsioni toccando le partite
• Vedere le tue previsioni contrassegnate con ✅
• Visualizzare i risultati delle partite completate 🏁
• Controllare i punti guadagnati per ogni previsione
"""

# Prediction messages
PREDICTION_START = "Select a match to predict:"
NO_MATCHES_TO_PREDICT = "There are no upcoming matches to predict at the moment."
PREDICTION_SUCCESS = "Your prediction has been saved! ✅"
PREDICTION_UPDATED = "Your prediction has been updated! ✅"
PREDICTION_LOCKED = "This match is locked and can no longer be predicted."
NO_PREDICTIONS = "You haven't made any predictions yet."

# Match messages
MATCH_LIST_HEADER = "📅 Upcoming Matches:"
NO_UPCOMING_MATCHES = "There are no upcoming matches at the moment."
MATCH_ADDED = "Match added successfully! ✅"
RESULT_SET = "Match result set successfully! ✅"

# Enhanced matches messages
ENHANCED_MATCHES_HEADER = """⚽ All Matches:

Legend:
⏳ - Upcoming match
✅ - You have predicted
🔒 - Locked (no longer accepting predictions)
⚽ - Ongoing match
🏁 - Match finished
"""
NO_MATCH_RESULTS = "Match results not available yet."

# Leaderboard messages
LEADERBOARD_HEADER = "🏆 Current Leaderboard:"
EMPTY_LEADERBOARD = "No scores available yet."
RANK_MESSAGE = "Your current rank: #{} with {} points."

# Admin messages
ADMIN_PANEL = """
⚙️ Admin Panel

Use the buttons below to manage the tournament:
• Add Match
• Set Result
• Update Leaderboard
• Export CSV
• Whitelist User
"""

ADMIN_ONLY = "This command is only available to admins."
LEADERBOARD_UPDATED = "Leaderboard has been updated! ✅"
CSV_EXPORTED = "CSV file has been exported! ✅"

# Whitelisting messages
USER_NOT_WHITELISTED = """
🚫 Access Restricted

You need to be approved to use this bot. Please contact the admin after paying the entrance fee to get whitelisted.

Once whitelisted, you'll be able to:
• View and predict matches
• See leaderboards
• Access all bot features

🚫 دسترسی محدود شده

برای استفاده از این ربات نیاز به تایید دارید. لطفا پس از پرداخت هزینه ورودی با ادمین تماس بگیرید تا در لیست سفید قرار بگیرید.

پس از تایید، می‌توانید:
• مسابقات را مشاهده و پیش‌بینی کنید
• جدول امتیازات را ببینید
• به تمام ویژگی‌های ربات دسترسی داشته باشید

🚫 Accesso Limitato

Devi essere approvato per utilizzare questo bot. Contatta l'amministratore dopo aver pagato la quota di iscrizione per essere inserito nella whitelist.

Una volta approvato, potrai:
• Visualizzare e prevedere le partite
• Vedere le classifiche
• Accedere a tutte le funzionalità del bot
"""

USER_WHITELISTED_SUCCESS = "✅ User {} has been successfully whitelisted!"
USER_ALREADY_WHITELISTED = "ℹ️ User {} is already whitelisted."
USER_NOT_FOUND = "❌ User {} not found. They need to start the bot first with /start command."
WHITELIST_INVALID_FORMAT = "❌ Invalid format. Please use: /whitelist @username"

# Error messages
GENERAL_ERROR = "An error occurred. Please try again later."
INVALID_FORMAT = "Invalid format. Please try again." 