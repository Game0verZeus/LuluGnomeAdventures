# Lulu’s Gnome Adventures

A small 8-bit style Python/Pygame game created in **half an evening**, because I wanted to explore my creativity and have fun!

In this retro adventure, you guide **Lulu**, a brave gnome capable of triple jumping and collecting a **magic hammer** to throw axes at mushrooms, birds, and even the fearsome BadLu.

---

## Table of Contents
1. [Features](#features)
2. [Screenshots / Demo](#screenshots--demo)
3. [Installation & Requirements](#installation--requirements)
4. [How to Play](#how-to-play)
5. [Known Bugs / Limitations](#known-bugs--limitations)
6. [Contributing](#contributing)
7. [Credits & Resources](#credits--resources)
8. [License](#license)

---

## Features
- **8-bit style** graphics and retro vibe.  
- **Triple jump**: Lulu can jump up to three times in a row.  
- **Bonus pickups**: hearts to regain HP, and a hammer to unlock axe-throwing.  
- **Single key for axe-throwing** (`E`):  
  - On the ground, it targets enemies like shrooms.  
  - In the air, it targets flying enemies (birds) and the BadLu boss.  
- **Background scroller** & multiple enemies (mushrooms, birds, plus the menacing BadLu).  
- **Fun music and sound effects** for jumps, throws, hits, etc.

---

## Screenshots / Demo
[![Watch Gameplay]][(https://youtu.be/example-video](https://youtube.com/shorts/NHmBIguTlNk?feature=share))
![Gnome Adventure Screenshot 1]([https://i.ibb.co/M2JCpxT "Gnome Adventure Screenshot 1](https://i.ibb.co/8KQ72L3/Screenshot-2025-01-07-204426.png)")

![Gnome Adventure Screenshot 2](https://i.ibb.co/HD1TcQC "Gnome Adventure Screenshot 2")

```md
![Gameplay Example](images/gameplay.png)
Here is the entire text formatted in Markdown for you:

```markdown
# Installation & Requirements

## Requirements:
- Python 3.8+
- Pygame

## Steps:

### Clone or download this repository:
```bash
git clone https://github.com/YourUsername/eight-bit-lulu.git
cd eight-bit-lulu
```

### Install Pygame:
```bash
pip install pygame
```
*(Or use your preferred virtual environment method.)*

### Run the game:
```bash
python game.py
```

Enjoy the retro experience of **Lulu’s Gnome Adventures**!

---

# How to Play
- **Move:** Left/Right arrow keys to move Lulu around.
- **Jump:** Press Space (up to three jumps in a row!).
- **Get the Hammer:** Move over the hammer pickup to unlock axe-throwing.
- **Throw Axes (E):**
  - If Lulu is on the ground, the axe targets ground enemies (shrooms).
  - If Lulu is jumping, the axe targets flying enemies (birds) or BadLu.
- **Objective:** Survive, collect hearts, defeat enemies, and take down BadLu by hurling axes at him.

---

# Known Bugs / Limitations
- Sometimes, defeated enemies blink a bit longer than expected before disappearing, but eventually, they go away.
- The triple jump is quite generous *(intentionally!)*.
- Balance is pretty simplistic—it’s a quick project made in half an evening.

Feel free to open Issues or Pull Requests if you spot other bugs or have suggestions!

---

# Contributing
Are you interested in adding:
- New levels (extra backgrounds, enemy patterns)
- Special powers or more boss fights
- Multiplayer or co-op mode  
Any improvement is welcome!

## Basic Steps:
1. **Fork this repo**
2. Create a feature branch:  
   ```bash
   git checkout -b my-awesome-feature
   ```
3. Commit your changes:  
   ```bash
   git commit -m "Add new feature"
   ```
4. Push:  
   ```bash
   git push origin my-awesome-feature
   ```
5. Open a Pull Request.

---

# Credits & Resources
- **Developer:** Myself, in just half an evening, exploring creativity.
- **Sprites & Artwork:** 8-bit style, either handmade or from open sources.
- **Sounds & Music:**
  - `main.mp3`, `start_menu.mp3`, hammer throw sounds, etc., included in `sounds/`.
  - Some are self-made, others are free resources with credits, most of them from envato elements.
- **Python & Pygame:** Big thanks to the open-source community!

---

# License
*(You can choose MIT, GPL, etc., or leave it unlicensed if personal. Example:)*

```css
MIT License

Copyright (c) 2025 Game0verZeus

Permission is hereby granted, free of charge, to any person obtaining a copy ...
```

---

Thank you for checking out **Lulu’s Gnome Adventures**—feel free to explore, customize, and share.  

**Have fun throwing axes at pixelated mushrooms!**
```
