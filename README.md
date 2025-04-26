# NHL Playoff Bracket Manager 🏒

A Python tool to manage NHL playoff bracket predictions, track scores, and generate visual brackets.

---

## ✨ Features
- User can create a Playoff Bracket League with custom or default (2025 first round) teams.
- Customizable leagues with any NHL teams and number of players.
- Input player bracket predictions, the correct (actual) playoff bracket, and a custom scoring system to generate a leaderboard.
- Visual bracket images are generated for players and the correct outcomes.  
- Easy-to-run with no web server or database needed.

---

## 📦 Requirements

- Python 3.8+  
- `pip`  
- (Optionally) `git` for cloning the repository  

Python libraries (auto-installed via `requirements.txt`):  
- Pillow  
- Matplotlib  
- NumPy

---

## 🚀 Quickstart Guide

### 1. Windows
```bash
git clone https://github.com/daniel-r-turner/nhl-bracket.git && cd nhl-bracket && setup.bat
```
Or:
- Click the green **Code** button
- Select **Download ZIP** and extract it locally
- Open the NHLBracket folder in Command Prompt
- Run `setup.bat`

### 2. Mac/Linux Command
```bash
git clone https://github.com/daniel-r-turner/nhl-bracket.git && cd nhl-bracket && chmod +x setup.sh && ./setup.sh
```
Or:
- Click the green **Code** button
- Select **Download ZIP** and extract it locally
- Open the NHLBracket folder in Terminal
- Give the setup script permission to execute: `chmod +x setup.sh`
- Run `./setup.sh`

---

## 🗂 Project Structure
```graphql
nhl-bracket/
├── bracket_results/      # Generated bracket images
├── team_logos/           # NHL team logo PNGs
├── bracket.py            # Bracket generation & rendering logic
├── bracket_node.py       # BracketNode data structure
├── league.py             # League scoring & leaderboard management
├── main.py               # CLI entry point
├── round.py              # Round enum definitions
├── team.py               # Team model class
├── requirements.txt      # Python package dependencies
├── .gitignore            # Files and folders ignored by Git
└── README.md             # This file
```

---

## ❓ FAQs

- **Q:** I see no brackets generated!  
  **A:** Make sure you complete all predictions—the generated images will be saved in the `bracket_results/` folder.

<br>

- **Q:** Can I run this without a virtual environment?  
  **A:** Yes, but using one avoids conflicts with other Python projects on your machine.

<br>

- **Q:** How do I update to the latest version?  
  **A:** Inside your repo folder, run:
  ```bash
  git pull
  ```
