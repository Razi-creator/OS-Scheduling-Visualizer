# 🖥️ CPU Scheduling Visualizer

## 📖 Overview:

The CPU Scheduling Visualizer is an interactive, web-based simulation tool designed to demonstrate the mathematical execution of Operating System (OS) process scheduling algorithms. Built entirely in Python using the Streamlit framework, this application bridges the gap between theoretical OS concepts and practical observation. It allows users to input custom process parameters and instantly visualize CPU allocation through dynamically generated Gantt charts and chronologically sorted execution tables.

## ✨ Key Features:

7 Core Scheduling Algorithms Supported:

First-Come, First-Served (FCFS)

Shortest Job First (SJF) - Non-Preemptive

Priority Scheduling (Non-Preemptive & Preemptive)

Round Robin (RR) - Includes dynamic Time Quantum input

Multi-Level Queue (MLQ)

Multi-Level Feedback Queue (MLFQ) - Simulates dynamic queue demotion

Real-Time Gantt Chart Generation: A custom HTML/CSS rendering pipeline dynamically creates color-coded, block-based Gantt charts to track millisecond-by-millisecond CPU execution and context switches.

Chronological Execution Tables: Overcomes asynchronous sorting issues by forcing the Pandas-rendered CPU table to strictly map its rows to the chronological start times of the processes.

Automated Metric Calculation: Instantly computes and displays critical OS performance metrics, including Average Completion Time (CT), Turnaround Time (TAT), and Waiting Time (WT).

Persistent State Management: Utilizes Streamlit's session_state to maintain the user's Ready Queue while interacting with different algorithms and UI elements.

## 🛠️ Technology Stack

Frontend: Streamlit (Python UI Framework), Custom HTML/CSS Injection

Backend: Pure Python 3.x (Object-Oriented Programming for Process Control Block simulation)

Data Handling: Pandas (for structured UI table rendering)

## 🗂️ Project Structure:

### app.py: 
The presentation layer. Manages the Streamlit user interface, dynamic conditional inputs, state memory, and custom HTML table/Gantt chart rendering.

### core_engine.py: 
The isolated backend mathematical engine. Contains the Object-Oriented Process class and the logic for all scheduling algorithms (handling 1-millisecond tick loops, preemption, and queue management).

### launch.json: 
VS Code debugging configuration file to easily launch the Streamlit local server.

### logo.jpg: 
(Optional) Local image file seamlessly blended into the UI header using CSS.

## 🚀 How to Run Locally:

### Prerequisites: 
Ensure you have Python 3.x installed along with the required libraries.

### Bash

pip install streamlit pandas

### Execution:

You can run the application directly from your terminal:

### Bash

streamlit run app.py

Alternatively, if you are using VS Code, you can use the provided .vscode/launch.json configuration to run and debug the app directly from the editor.
