
# Pomodoro Timer Application

## Overview / Vue d'ensemble

This Pomodoro Timer application is an advanced tool designed to enhance productivity through the Pomodoro Technique. By structuring work sessions around focused intervals followed by short breaks, it aims to optimize efficiency and mental acuity. Built with PyQt5 for the graphical user interface and pygame for audio notifications, it offers a robust platform for managing time effectively. / L'application Pomodoro Timer est un outil avancé conçu pour améliorer la productivité grâce à la technique Pomodoro. En structurant les sessions de travail autour d'intervalles ciblés suivis de courtes pauses, elle vise à optimiser l'efficacité et l'acuité mentale. Construite avec PyQt5 pour l'interface graphique et pygame pour les notifications audio, elle offre une plateforme robuste pour gérer efficacement son temps. /

## Features / Fonctionnalités

- **Customizable Durations:** Users can set personalized durations for work, short break, and long break periods to suit their productivity rhythms. / **Durées personnalisables :** Les utilisateurs peuvent définir des durées personnalisées pour les périodes de travail, de courte pause et de longue pause pour s'adapter à leurs rythmes de productivité.
- **Audio Notifications:** Utilizes pygame for gentle audio cues signaling the end of work and break sessions, facilitating seamless transitions. / **Notifications audio :** Utilise pygame pour des signaux audio doux indiquant la fin des sessions de travail et de pause, facilitant les transitions sans heurt.
- **Session History Tracking:** Records each session's details, including type, timestamp, and goals, for performance analysis and motivation. / **Suivi de l'historique des sessions :** Enregistre les détails de chaque session, y compris le type, l'horodatage et les objectifs, pour l'analyse des performances et la motivation.
- **Theme Toggle:** Offers light and dark theme options, accommodating user preference and reducing eye strain. / **Basculement de thème :** Offre des options de thème clair et sombre, s'adaptant à la préférence de l'utilisateur et réduisant la fatigue oculaire.

## Installation

### Requirements / Prérequis

- Python 3.6 or later / Python 3.6 ou ultérieur
- PyQt5
- pygame

### Installing Dependencies / Installation des dépendances

Install the required Python packages using pip:

```bash
pip install PyQt5 pygame
```

## Quick Start / Démarrage rapide

Clone the repository and launch the application:

```bash
git clone https://github.com/SilentForge/EffectivePomodoro.git
cd EffectivePomodoro
python pomodoro_gui.py
```

## Usage / Utilisation

Upon starting the application, configure the durations for your work and break periods through the user interface. Hit the start button to begin a focused work session. The application will notify you when it's time to take a break, allowing for a structured workday that maximizes productivity. / Après avoir démarré l'application, configurez les durées de vos périodes de travail et de pause via l'interface utilisateur. Appuyez sur le bouton de démarrage pour commencer une session de travail concentrée. L'application vous avertit lorsqu'il est temps de faire une pause, ce qui permet de structurer la journée de travail et de maximiser la productivité.

## Code Documentation / Documentation du code

The application is divided into two primary files for clarity and maintainability:

- `pomodoro_gui.py`: Contains the PyQt5-based GUI. It handles user interactions and visual feedback. / Contient l'interface graphique basée sur PyQt5. Il gère les interactions utilisateur et les retours visuels.
- `pomodoro_logic.py`: Implements the timer's backend logic, managing session transitions and audio notifications. / Implémente la logique backend du minuteur, gérant les transitions de session et les notifications audio.

## Contributing / Contribuer

We welcome contributions to enhance the Pomodoro Timer application. Please fork the repository, commit your changes, and submit a pull request for review. / Nous accueillons les contributions pour améliorer l'application de minuterie Pomodoro. Veuillez forker le dépôt, soumettre vos modifications et envoyer une demande de tirage pour examen.

## License / Licence

This project is available under the MIT License, promoting open and collaborative development. See the LICENSE file in the repository for full details. / Ce projet est disponible sous la licence MIT, favorisant un développement ouvert et collaboratif. Consultez le fichier LICENSE dans le dépôt pour tous les détails.
