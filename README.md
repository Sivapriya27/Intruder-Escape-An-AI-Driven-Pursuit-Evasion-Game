# Intruder Escape - An AI Driven Pursuit Evasion Game 🕹️🤖

An AI-driven pursuit–evasion game where you (the intruder) must survive as long as possible while four robots use **A\*** pathfinding to hunt you down. Built with Python and Pygame.
<p align="center">
  <img src="assets/demo.gif" alt="Intruder Escape demo" width="640"/>
</p>

## 🎮 How to play

- Click **Place Intruder**, then click a white cell to set your starting spot.
- Press **Start Game** or hit **SPACE** to begin.
- Move with **arrow keys**. Survive as long as you can—robots get faster over time.
- Use **New Layout** for a fresh randomized grid.  
- **Clear Grid** resets the state.

---

## ⚙️ Game rules (defaults)

- **Grid:** 15 × 15  
- **Obstacles:** 30  
- **Robots:** 4  
- **Robot speed:** starts at **1.0**, increases by **+0.1 every 100 steps**  
- **Leaderboard:** keeps **top 5 scores** (stored locally in JSON)

> You can tweak these constants at the top of [`src/intruder_escape.py`](src/intruder_escape.py).

---

## 🧩 Key modules & responsibilities

- **Game loop & UI** → handles buttons, grid drawing, overlay, and status text.  
- **A\* pathfinding** → Manhattan heuristic on a 4-neighbor grid (up/down/left/right).  
- **Difficulty scaling** → robot speed increases periodically with your step count.  
- **Persistence** → JSON files store high score and top-5 leaderboard.  

---

## 💡 Design notes

- **Why A\*** → Efficient and optimal on grid graphs with admissible heuristics.  
- **Heuristic** → Manhattan distance (fits 4-direction movement).  
- **Replanning** → Robots continuously recompute paths towards the intruder.  
- **Randomness** → Obstacles and robot spawns vary each run but remain solvable.  

---

## 📊 Algorithm comparison (A\* vs UCS)

We tested **Uniform Cost Search (UCS)** against **A\*** to evaluate efficiency:  

| Metric              | A\* (Manhattan heuristic) | UCS (no heuristic) |
|---------------------|----------------------------|--------------------|
| **Nodes explored**  | ~95.6                     | ~419.4             |
| **Path length**     | 41.8                      | 41.6               |
| **Runtime (ms)**    | 0.052                     | 0.112              |

➡️ **A\*** was ~**2.15× faster**, explored ~**4.4× fewer nodes**, while producing nearly identical path lengths.  
This makes it the clear choice for real-time pursuit–evasion gameplay.

---

## 🚀 Roadmap (nice-to-haves)

- 🔄 Diagonal moves & terrain costs (slows / cover zones).  
- 🧠 Smarter multi-robot coordination (flanking, trapping).  
- 🎚️ Difficulty presets and custom grid sizes.  
- 📦 Packaging as one-file executables for Windows/macOS/Linux.  

---

## 📑 Documentation

For a deeper discussion of methodology, experiments, and results, see the full write-up:  
[`docs/Intruder_Escape-Project Report.pdf`](docs/Intruder_Escape-Project Report.pdf)

---

## ⚡ Quick start

> Requires **Python 3.9+** and **Pygame 2.5+**.

```bash
# 1. Clone
git clone https://github.com/<your-username>/intruder-escape.git
cd intruder-escape

# 2. Setup virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the game
python src/intruder_escape.py
