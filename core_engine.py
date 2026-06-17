class Process:
    def __init__(self, pid, arrival_time, burst_time, priority=0, queue_level=1):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.priority = priority       # Lower number = higher priority
        self.queue_level = queue_level # 1 = Highest Queue
        
        # Dynamic State
        self.remaining_time = burst_time 
        self.start_time = -1
        self.completion_time = 0
        self.turnaround_time = 0
        self.waiting_time = 0
        
        # For MLFQ tracking
        self.current_queue_time = 0

def reset_processes(process_list):
    """Resets the calculated metrics so the same processes can be re-run."""
    for p in process_list:
        p.remaining_time = p.burst_time
        p.start_time = -1
        p.completion_time = 0
        p.turnaround_time = 0
        p.waiting_time = 0
        p.current_queue_time = 0

def log_gantt(gantt, pid, current_time):
    """Helper to merge contiguous 1ms blocks into smooth Gantt bars."""
    if not gantt or gantt[-1]['pid'] != pid:
        gantt.append({'pid': pid, 'start': current_time, 'end': current_time + 1})
    else:
        gantt[-1]['end'] = current_time + 1

def finalize_process(p, current_time):
    """Calculates final metrics when a process finishes."""
    p.completion_time = current_time
    p.turnaround_time = p.completion_time - p.arrival_time
    p.waiting_time = p.turnaround_time - p.burst_time

# ==========================================
# 1. First-Come, First-Served (FCFS)
# ==========================================
def fcfs(processes):
    reset_processes(processes)
    ready = sorted(processes, key=lambda p: p.arrival_time)
    current_time = 0
    gantt = []
    
    for p in ready:
        if current_time < p.arrival_time: current_time = p.arrival_time
        p.start_time = current_time
        current_time += p.burst_time
        log_gantt(gantt, p.pid, p.start_time)
        gantt[-1]['end'] = current_time # override 1ms helper for pure block
        finalize_process(p, current_time)
    return processes, gantt

# ==========================================
# 2. Shortest Job First (SJF) - Non-Preemptive
# ==========================================
def sjf(processes):
    reset_processes(processes)
    remaining = processes.copy()
    current_time = 0
    gantt = []
    finished = []

    while remaining:
        ready = [p for p in remaining if p.arrival_time <= current_time]
        if not ready:
            current_time += 1
            continue
        
        ready.sort(key=lambda p: (p.burst_time, p.arrival_time))
        p = ready[0]
        
        p.start_time = current_time
        current_time += p.burst_time
        gantt.append({'pid': p.pid, 'start': p.start_time, 'end': current_time})
        finalize_process(p, current_time)
        
        finished.append(p)
        remaining.remove(p)
    return finished, gantt

# ==========================================
# 3. Priority - Non-Preemptive
# ==========================================
def priority_np(processes):
    reset_processes(processes)
    remaining = processes.copy()
    current_time = 0
    gantt = []
    finished = []

    while remaining:
        ready = [p for p in remaining if p.arrival_time <= current_time]
        if not ready:
            current_time += 1
            continue
        
        # Sort by priority (lowest number = highest priority), then arrival
        ready.sort(key=lambda p: (p.priority, p.arrival_time))
        p = ready[0]
        
        p.start_time = current_time
        current_time += p.burst_time
        gantt.append({'pid': p.pid, 'start': p.start_time, 'end': current_time})
        finalize_process(p, current_time)
        
        finished.append(p)
        remaining.remove(p)
    return finished, gantt

# ==========================================
# 4. Shortest Remaining Time First (SRTF) - Preemptive
# ==========================================
def srtf(processes):
    reset_processes(processes)
    remaining = processes.copy()
    current_time = 0
    gantt = []
    finished = []

    while remaining:
        ready = [p for p in remaining if p.arrival_time <= current_time]
        if not ready:
            current_time += 1
            continue
        
        ready.sort(key=lambda p: (p.remaining_time, p.arrival_time))
        p = ready[0]
        
        if p.start_time == -1: p.start_time = current_time
        
        log_gantt(gantt, p.pid, current_time)
        current_time += 1
        p.remaining_time -= 1
        
        if p.remaining_time == 0:
            finalize_process(p, current_time)
            finished.append(p)
            remaining.remove(p)
    return finished, gantt

# ==========================================
# 5. Priority - Preemptive
# ==========================================
def priority_p(processes):
    reset_processes(processes)
    remaining = processes.copy()
    current_time = 0
    gantt = []
    finished = []

    while remaining:
        ready = [p for p in remaining if p.arrival_time <= current_time]
        if not ready:
            current_time += 1
            continue
        
        ready.sort(key=lambda p: (p.priority, p.arrival_time))
        p = ready[0]
        
        if p.start_time == -1: p.start_time = current_time
        
        log_gantt(gantt, p.pid, current_time)
        current_time += 1
        p.remaining_time -= 1
        
        if p.remaining_time == 0:
            finalize_process(p, current_time)
            finished.append(p)
            remaining.remove(p)
    return finished, gantt

# ==========================================
# 6. Round Robin (RR)
# ==========================================
def round_robin(processes, quantum=2):
    reset_processes(processes)
    ready_queue = []
    current_time = 0
    gantt = []
    finished = []
    visited = set()

    while len(finished) < len(processes):
        # Enqueue newly arrived processes
        for p in processes:
            if p.arrival_time <= current_time and p not in visited and p not in finished:
                ready_queue.append(p)
                visited.add(p)

        if not ready_queue:
            current_time += 1
            continue

        p = ready_queue.pop(0)
        if p.start_time == -1: p.start_time = current_time

        run_time = min(p.remaining_time, quantum)
        gantt.append({'pid': p.pid, 'start': current_time, 'end': current_time + run_time})
        
        current_time += run_time
        p.remaining_time -= run_time

        # Check for arrivals DURING execution to maintain strict FIFO queue order
        for new_p in processes:
            if new_p.arrival_time <= current_time and new_p not in visited and new_p not in finished:
                ready_queue.append(new_p)
                visited.add(new_p)

        if p.remaining_time > 0:
            ready_queue.append(p)
        else:
            finalize_process(p, current_time)
            finished.append(p)

    return processes, gantt

# ==========================================
# 7. Multi-Level Queue (MLQ)
# (Q1: Priority 1 uses RR(q=2) | Q2: Priority 2 uses FCFS)
# ==========================================
def mlq(processes):
    reset_processes(processes)
    remaining = processes.copy()
    current_time = 0
    gantt = []
    finished = []
    q1_queue = [] # RR, quantum 2
    visited = set()

    while remaining:
        # Load queues
        for p in remaining:
            if p.arrival_time <= current_time and p not in visited:
                if p.queue_level == 1: q1_queue.append(p)
                visited.add(p)

        q2_ready = [p for p in remaining if p.arrival_time <= current_time and p.queue_level == 2]

        if q1_queue:
            p = q1_queue.pop(0)
            if p.start_time == -1: p.start_time = current_time
            
            run_time = min(p.remaining_time, 2)
            gantt.append({'pid': p.pid, 'start': current_time, 'end': current_time + run_time})
            current_time += run_time
            p.remaining_time -= run_time
            
            # Load mid-execution arrivals
            for new_p in remaining:
                if new_p.arrival_time <= current_time and new_p not in visited:
                    if new_p.queue_level == 1: q1_queue.append(new_p)
                    visited.add(new_p)
                    
            if p.remaining_time > 0: q1_queue.append(p)
            else: 
                finalize_process(p, current_time)
                finished.append(p)
                remaining.remove(p)
                
        elif q2_ready:
            # Q2 uses FCFS, but is preempted by Q1
            q2_ready.sort(key=lambda p: p.arrival_time)
            p = q2_ready[0]
            if p.start_time == -1: p.start_time = current_time
            
            log_gantt(gantt, p.pid, current_time)
            current_time += 1
            p.remaining_time -= 1
            
            if p.remaining_time == 0:
                finalize_process(p, current_time)
                finished.append(p)
                remaining.remove(p)
        else:
            current_time += 1
            
    return finished, gantt

# ==========================================
# 8. Multi-Level Feedback Queue (MLFQ)
# (Q1: RR(q=2) -> Q2: RR(q=4) -> Q3: FCFS)
# ==========================================
def mlfq(processes):
    reset_processes(processes)
    remaining = processes.copy()
    current_time = 0
    gantt = []
    finished = []
    
    q1 = [] # q=2
    q2 = [] # q=4
    q3 = [] # FCFS
    visited = set()

    while remaining:
        # All new arrivals go straight into Q1
        for p in remaining:
            if p.arrival_time <= current_time and p not in visited:
                q1.append(p)
                visited.add(p)

        if q1:
            p = q1[0]
            if p.start_time == -1: p.start_time = current_time
            log_gantt(gantt, p.pid, current_time)
            current_time += 1
            p.remaining_time -= 1
            p.current_queue_time += 1
            
            if p.remaining_time == 0:
                finalize_process(p, current_time)
                finished.append(p)
                remaining.remove(p)
                q1.pop(0)
            elif p.current_queue_time == 2: # Q1 Quantum expired, demote
                p.current_queue_time = 0
                q2.append(q1.pop(0))
                
        elif q2:
            p = q2[0]
            if p.start_time == -1: p.start_time = current_time
            log_gantt(gantt, p.pid, current_time)
            current_time += 1
            p.remaining_time -= 1
            p.current_queue_time += 1
            
            if p.remaining_time == 0:
                finalize_process(p, current_time)
                finished.append(p)
                remaining.remove(p)
                q2.pop(0)
            elif p.current_queue_time == 4: # Q2 Quantum expired, demote
                p.current_queue_time = 0
                q3.append(q2.pop(0))
                
        elif q3:
            p = q3[0]
            if p.start_time == -1: p.start_time = current_time
            log_gantt(gantt, p.pid, current_time)
            current_time += 1
            p.remaining_time -= 1
            
            if p.remaining_time == 0:
                finalize_process(p, current_time)
                finished.append(p)
                remaining.remove(p)
                q3.pop(0)
        else:
            current_time += 1

    return finished, gantt

# ==========================================
# Testing Ground
# ==========================================
if __name__ == "__main__":
    test_processes = [
        Process("P1", arrival_time=0, burst_time=5, priority=2, queue_level=1),
        Process("P2", arrival_time=1, burst_time=4, priority=1, queue_level=2),
        Process("P3", arrival_time=2, burst_time=2, priority=3, queue_level=1),
        Process("P4", arrival_time=4, burst_time=6, priority=2, queue_level=2)
    ]

    print("Running Preemptive Priority Simulation...")
    # Change priority_p to srtf, mlfq, round_robin, etc. to test different algorithms!
    finished_procs, chart = priority_p(test_processes) 

    print(f"\n{'PID':<5} | {'Arr':<4} | {'Brst':<4} | {'Pri':<3} | {'Wait':<5} | {'Turn':<5}")
    print("-" * 45)
    for p in sorted(finished_procs, key=lambda x: x.pid):
        print(f"{p.pid:<5} | {p.arrival_time:<4} | {p.burst_time:<4} | {p.priority:<3} | {p.waiting_time:<5} | {p.turnaround_time:<5}")

    print("\nGantt Chart Timeline:")
    print(chart)