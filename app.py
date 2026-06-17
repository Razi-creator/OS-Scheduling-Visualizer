import streamlit as st
import pandas as pd
import core_engine as ce
import os
import base64

# 1. Page Configuration
st.set_page_config(page_title="Razi's Schedular Visualization", layout="wide")

# 2. Custom CSS for Mint Frost Theme
st.markdown("""
    <style>
    .stApp { background-color: #F0FDF4 !important; }
    h1, h2, h3, h4, h5, h6, p, span, label, div { color: black !important; }
    
    .main-title { 
        text-align: center; color: black; font-family: 'Arial', sans-serif; 
        font-size: 46px; font-weight: 900; margin-top: 10px; margin-bottom: 20px; 
        text-transform: uppercase; letter-spacing: 2px;
    }
    
    .stButton>button { font-weight: bold; font-size: 16px; border: 2px solid black !important; color: black !important; background-color: white !important;}
    .stButton>button:hover { background-color: #e0f7fa !important; }
    div[data-testid="stRadio"] label p { font-size: 18px !important; font-weight: bold !important; color: black !important; }
    </style>
""", unsafe_allow_html=True)

COLORS = [
    "#8fbc8f", "#9370db", "#bdb76b", "#deb887", "#c8a2c8", 
    "#ffb6c1", "#87cefa", "#ffa07a", "#20b2aa", "#f08080", 
    "#e6e6fa", "#ffe4b5", "#98fb98", "#afeeee", "#db7093", 
    "#ffdab9", "#dda0dd", "#b0e0e6", "#d8bfd8", "#f5deb3"
]

# --- LOGO INCORPORATION ---
logo_col1, logo_col2, logo_col3 = st.columns([1, 2, 1])
with logo_col2:
    if os.path.exists("logo.jpg"):
        with open("logo.jpg", "rb") as f:
            img_data = f.read()
            b64_img = base64.b64encode(img_data).decode()
            st.markdown(f'<div style="text-align: center;"><img src="data:image/jpeg;base64,{b64_img}" style="width: 50%; mix-blend-mode: multiply;"></div>', unsafe_allow_html=True)
    else:
        st.warning("⚠️ Save your logo image as 'logo.jpg' in the same folder!")

st.markdown("<div class='main-title'>Razi's Schedular Visualization</div>", unsafe_allow_html=True)
st.divider()

# --- ALGORITHM SELECTION ---
algorithm_map = {
    "FCFS (First Come First Serve)": "First-Come, First-Served (FCFS)",
    "SJF (Shortest Job First)": "Shortest Job First (SJF)",
    "Priority (Non-Preemptive)": "Priority (Non-Preemptive)",
    "Priority (Preemptive)": "Priority (Preemptive)",
    "RRS (Round Robin Algorithm)": "Round Robin (RR)",
    "MLQ (Multi-Level Queue)": "Multi-Level Queue (MLQ)",
    "MLFQ (Multi-Level Feedback Queue)": "Multi-Level Feedback Queue (MLFQ)"
}

selected_display_algo = st.radio("Select Your CPU Algorithm:", list(algorithm_map.keys()), index=0)
backend_algo = algorithm_map[selected_display_algo]

needs_priority = backend_algo in ["Priority (Non-Preemptive)", "Priority (Preemptive)"]
needs_queue = backend_algo in ["Multi-Level Queue (MLQ)", "Multi-Level Feedback Queue (MLFQ)"]
needs_quantum = backend_algo in ["Round Robin (RR)", "Multi-Level Queue (MLQ)", "Multi-Level Feedback Queue (MLFQ)"]

quantum = 2
if needs_quantum:
    st.write("")
    quantum = st.number_input("Enter Time Quantum:", min_value=1, step=1, value=2)

st.divider()

# --- STATE MANAGEMENT ---
if 'processes' not in st.session_state:
    st.session_state.processes = []
if 'show_visuals' not in st.session_state:
    st.session_state.show_visuals = False

# --- INPUT SECTION ---
input_col, table_col = st.columns([1, 1.5], gap="large")

with input_col:
    st.markdown("### Add New Process")
    new_arrival = st.number_input("Enter Arrival Time:", min_value=0, step=1, value=0)
    new_burst = st.number_input("Enter Burst Time:", min_value=1, step=1, value=1)
    new_priority, new_queue = 1, 1
    
    if needs_priority or needs_queue:
        p_col1, p_col2 = st.columns(2)
        with p_col1:
            if needs_priority: new_priority = st.number_input("Priority (Min 1):", min_value=1, step=1, value=1)
        with p_col2:
            if needs_queue: new_queue = st.number_input("Queue (1, 2, 3):", min_value=1, max_value=3, step=1, value=1)

    st.write("") 
    b_col1, b_col2 = st.columns(2)
    with b_col1:
        if st.button("➕ Add Task", use_container_width=True):
            if len(st.session_state.processes) < 20: 
                st.session_state.processes.append({"PID": f"P{len(st.session_state.processes) + 1}", "Arrival": new_arrival, "Burst": new_burst, "Priority": new_priority, "Queue": new_queue})
                st.rerun()
    with b_col2:
        if st.button("🗑️ Delete Task", use_container_width=True):
            if len(st.session_state.processes) > 0:
                st.session_state.processes.pop()
                st.rerun()
                
    st.write("")
    if st.button("🚀 Visualized", use_container_width=True):
        st.session_state.show_visuals = True

with table_col:
    st.markdown("### Currently Added Processes")
    if len(st.session_state.processes) > 0:
        df_live = pd.DataFrame(st.session_state.processes)
        if not needs_priority: df_live = df_live.drop(columns=["Priority"])
        if not needs_queue: df_live = df_live.drop(columns=["Queue"])
        st.dataframe(df_live, hide_index=True, use_container_width=True)
    else:
        st.info("No processes added yet. Enter details on the left and click 'Add Task'.")

st.divider()

# --- EXECUTION & RENDERING ---
if st.session_state.show_visuals and len(st.session_state.processes) > 0:
    
    engine_processes = []
    for p in st.session_state.processes:
        engine_processes.append(ce.Process(pid=p["PID"], arrival_time=p["Arrival"], burst_time=p["Burst"], priority=p["Priority"], queue_level=p.get("Queue", 1)))

    # Execute the selected scheduler
    if backend_algo == "First-Come, First-Served (FCFS)":
        finished_procs, gantt_data = ce.fcfs(engine_processes)
    elif backend_algo == "Shortest Job First (SJF)":
        finished_procs, gantt_data = ce.sjf(engine_processes)
    elif backend_algo == "Priority (Non-Preemptive)":
        finished_procs, gantt_data = ce.priority_np(engine_processes)
    elif backend_algo == "Priority (Preemptive)":
        finished_procs, gantt_data = ce.priority_p(engine_processes)
    elif backend_algo == "Round Robin (RR)":
        finished_procs, gantt_data = ce.round_robin(engine_processes, quantum=quantum)
    elif backend_algo == "Multi-Level Queue (MLQ)":
        finished_procs, gantt_data = ce.mlq(engine_processes)
    elif backend_algo == "Multi-Level Feedback Queue (MLFQ)":
        finished_procs, gantt_data = ce.mlfq(engine_processes)

    # DYNAMIC ARRANGEMENT FIX: Read the exact execution order directly from the current Gantt chart!
    gantt_order = []
    for block in gantt_data:
        if block['pid'] not in gantt_order:
            gantt_order.append(block['pid'])
            
    # Force the CPU table to sort itself by strictly following the current scheduler's execution flow
    finished_procs.sort(key=lambda x: gantt_order.index(x.pid) if x.pid in gantt_order else 999)

    total_ct = sum(p.completion_time for p in finished_procs)
    total_tat = sum(p.turnaround_time for p in finished_procs)
    avg_ct = total_ct / len(finished_procs)
    avg_tat = total_tat / len(finished_procs)

    st.markdown(f"""
    <div style="display: flex; gap: 20px; justify-content: center; margin-bottom: 20px;">
        <span style='color:black; font-weight:bold; font-size:18px;'>Avg. Completion Time = <span style='background-color: white; border: 2px solid black; padding: 4px 10px; border-radius: 4px;'>{avg_ct:.1f}</span></span>
        <span style='color:black; font-weight:bold; font-size:18px;'>Avg. Turn Around Time = <span style='background-color: white; border: 2px solid black; padding: 4px 10px; border-radius: 4px;'>{avg_tat:.1f}</span></span>
    </div>
    """, unsafe_allow_html=True)

    table_lines = [
        '<div style="overflow-x: auto;">',
        '<table style="width: 100%; border-collapse: collapse; text-align: left; font-family: Arial, sans-serif; border: 2px solid black; margin-top: 20px; background-color: white;">',
        '  <tr style="background-color: #add8e6; border-bottom: 2px solid black;"><th colspan="10" style="text-align: center; padding: 12px; font-size: 18px; color: black; border-bottom: 2px solid black;">CPU SCHEDULING TABLE</th></tr>',
        '  <tr style="background-color: #e0f7fa; border-bottom: 2px solid black; font-size: 15px;">',
        '    <th style="padding: 10px; color: blue; border-right: 1px solid black;">Process ID</th><th style="padding: 10px; color: green; border-right: 1px solid black;">Arrival Time</th><th style="padding: 10px; color: red; border-right: 1px solid black;">Burst Time</th><th style="padding: 10px; color: brown; border-right: 1px solid black;">Priority</th><th style="padding: 10px; color: purple; border-right: 1px solid black;">Queue</th><th style="padding: 10px; color: #d2691e; border-right: 1px solid black;">Response Time</th><th style="padding: 10px; color: green; border-right: 1px solid black;">TAT</th><th style="padding: 10px; color: red; border-right: 1px solid black;">CT</th><th style="padding: 10px; color: red; border-right: 1px solid black;">Waiting Time</th><th style="padding: 10px; color: blue;">Indicator</th>',
        '  </tr>'
    ]

    for i, p in enumerate(finished_procs):
        bg_color = "#f9f9f9" if i % 2 == 0 else "#e9ecef"
        pid_num = int(p.pid.replace("P", ""))
        indicator_color = COLORS[(pid_num - 1) % 20]
        response_time = p.start_time - p.arrival_time
        display_priority = p.priority if needs_priority else "-"
        display_queue = p.queue_level if needs_queue else "-"
        
        table_lines.append(f'  <tr style="background-color: {bg_color}; border-bottom: 1px solid black; color: black; font-weight: bold;">')
        table_lines.append(f'    <td style="padding: 10px; border-right: 1px solid black;">{p.pid}</td><td style="padding: 10px; border-right: 1px solid black;">{p.arrival_time}</td><td style="padding: 10px; border-right: 1px solid black;">{p.burst_time}</td><td style="padding: 10px; border-right: 1px solid black;">{display_priority}</td><td style="padding: 10px; border-right: 1px solid black;">{display_queue}</td><td style="padding: 10px; border-right: 1px solid black;">{response_time}</td><td style="padding: 10px; border-right: 1px solid black;">{p.turnaround_time}</td><td style="padding: 10px; border-right: 1px solid black;">{p.completion_time}</td><td style="padding: 10px; border-right: 1px solid black;">{p.waiting_time}</td><td style="padding: 10px; background-color: {indicator_color}; border-left: 2px solid black;"></td>')
        table_lines.append('  </tr>')
        
    table_lines.append('</table></div>')
    st.markdown("".join(table_lines), unsafe_allow_html=True)

    st.write("")
    st.markdown('<div style="background-color: white; border: 2px solid black; padding: 10px; text-align: center; border-radius: 5px; margin-bottom: 20px;"><h3 style="margin: 0; color: black;">Visualized Graph 👇 & CPU Table 💻</h3></div>', unsafe_allow_html=True)

    gantt_lines = ["<div style='display: flex; flex-direction: column; width: fit-content; margin: 0 auto; border: 2px solid black; background-color: white;'>"]
    gantt_lines.append("<div style='display: flex; flex-direction: row;'>")
    for block in gantt_data:
        pid_num = int(block['pid'].replace("P", ""))
        block_color = COLORS[(pid_num - 1) % 20]
        gantt_lines.append(f"<div style='background-color: {block_color}; padding: 10px 20px; border-right: 1px solid black; border-bottom: 2px solid black; text-align: center; font-weight: bold; color: black; min-width: 60px;'>{block['pid']}</div>")
    gantt_lines.append("</div><div style='display: flex; flex-direction: row;'>")
    for block in gantt_data:
        duration = block['end'] - block['start']
        gantt_lines.append(f"<div style='background-color: white; padding: 5px 20px; border-right: 1px solid black; text-align: center; font-weight: bold; color: black; min-width: 60px;'>{duration}</div>")
    gantt_lines.append("</div></div>")
    st.markdown("".join(gantt_lines), unsafe_allow_html=True)