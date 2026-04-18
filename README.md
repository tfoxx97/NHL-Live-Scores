# 🏒 NHL Live Score Tracker

A simple Python script that allows users to select their favorite NHL team and receive real-time score updates when they are playing.

---

## 📌 Features

* 🏒 Select your favorite NHL team
* 📡 Polls live game data for real-time score updates
* ⏱️ Detects and displays score changes
* 📅 Smart status reporting:

  * Team is **currently playing** : LIVE
  * Team **already played today** : FINAL
  * Team **plays later today** : PREVIEW
  * Team is **not playing today**

---

## 🚀 Getting Started
### Prerequisites: 
* Python 3.12 or higher

### Installation
Clone the repository:

```bash
git clone https://github.com/tfoxx97/NHL-Live-Scores.git
cd nhl-live-score-tracker
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ▶️ Usage

Run the script:

```bash
python NHLScoresToday.py
```

You will be prompted to enter your favorite NHL team.

Example:

```
Enter your favorite NHL team: ANA
```
** ana or Anaheim Ducks also acceptable inputs

---

## 🧠 How It Works

1. The script sends a GET request to the URL in the main .py file
2. It determines if your selected team has a game today
3. Based on the result:

   * If **playing now** → begins polling for live score updates
   * If **already played** or **playing later** or **not playing**  → notifies user, no polling
4. While a game is live:

   * The script polls periodically as specified by user
   * Detects score changes
   * Outputs updates in real time

---

## ⚠️ Notes

* This project uses API from https://nhl-score-api.herokuapp.com/
* Git: https://github.com/peruukki/nhl-score-api
* Data may be delayed by a few seconds
* API endpoints may change without notice

---

## 💡 Future Improvements

* 🔊 Goal notifications (sound or hardware trigger)
* 💡 LED integrations (Raspberry Pi / microcontroller)
* 📱 GUI or web interface
* 🔔 Push notifications

---

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

---
