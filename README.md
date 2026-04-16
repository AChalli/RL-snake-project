# Autonomous Snake Agent: Tabular Q-Learning

An AI agent that learns to play the classic game of Snake from scratch using Reinforcement Learning (Tabular Q-Learning). Built entirely in Python using PyGame.

## 🧠 The AI (How it Works)
This agent does not use hardcoded pathfinding (like A*). Instead, it learns through trial and error, balancing exploration (random moves) and exploitation (using its Q-Table). 

**Key Technical Challenges Solved:**
* **Curse of Dimensionality:** Standard snake environments have more possible states than atoms in the universe. I engineered a hybrid state-space representation using distance-clipping and localized congestion tracking to keep the Q-table manageable.
* **Reward Shaping:** Implemented distance-based reward shaping using Manhattan distance, heavily penalizing death while offering micro-rewards for moving toward the objective.

## 🎮 Controls & Features
Watch the agent learn in real-time. You can adjust the simulation speed on the fly.
* `UP ARROW` - Speed up simulation
* `DOWN ARROW` - Slow down simulation
* `0` - Reset to normal speed (10 FPS)
* `S` - Save the current Q-Table (Brain) to a `.pkl` file
* `R` - Reset the agent's memory to start over

## 🚀 Getting Started

### Prerequisites
* Python 3.x
* PyGame
* NumPy

### Installation
1. Clone the repo: `git clone [your-repo-link]`
2. Install dependencies: `pip install pygame numpy`
3. Run the agent: `python snake_ai.py`
