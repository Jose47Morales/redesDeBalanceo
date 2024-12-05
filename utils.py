import networkx as nx
import random

def calculate_cycle_time(production_time, required_production):
    return production_time / required_production

def calculate_min_stations(task_times, cycle_time):
    return sum(task_times) / cycle_time

def assign_tasks_to_stations(tasks, cycle_time, precedence_rules):
    stations = []
    current_station = []
    current_time = 0

    while tasks:
        feasible_tasks = [
            task for task in tasks
            if all(pre in [t[0] for s in stations for t in s] or pre in [t[0] for t in current_station]
                   for pre in precedence_rules.get(task[0], []))
        ]

        if not feasible_tasks:
            if current_station:
                stations.append(current_station)
            current_station = []
            current_time = 0
            continue

        feasible_tasks = sorted(feasible_tasks, key=lambda t: t[1], reverse=True)
        task_added = False

        for task in feasible_tasks:
            if current_time + task[1] <= cycle_time:
                current_station.append(task)
                current_time += task[1]
                tasks.remove(task)
                task_added = True
                break;
        
        if not task_added:
            stations.append(current_station)
            current_station = []
            current_time = 0
    
    if current_station:
        stations.append(current_station)
    
    return stations

def calculate_efficiency(task_times, cycle_time, stations):
    total_time = len(stations) * cycle_time
    return (sum(task_times) / total_time) * 100