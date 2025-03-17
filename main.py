import time
import pandas as pd
import numpy as np
import plotly.graph_objects as go 
from itertools import product
from pyslope import (
    Slope,
    Material
)
from database import database

# Create database instance
db = database()

# Define the max fs, point where we will no longer calculate the fs
max_fs = 2

# Function to calculate slope safety factor
def get_slope(height, length, cohesion, friction_angle, weight):
    
    s = Slope(height=height, angle=None, length=length)

    m = Material(
        unit_weight=weight,
        friction_angle=friction_angle,
        cohesion=cohesion
    )
    s.set_materials(m)

    # s.set_water_table(4)
    # s.update_analysis_options(slices=50, iterations=2500)
    s.analyse_slope()

    return s

if __name__ == '__main__':
    
    start_time = time.time()

    # Check last cenario done
    last_cenario = db.get('results', '*', 'id = (SELECT MAX(id) FROM results);')
    if last_cenario == None:
        previous_id = False
        previous_fs = 0
    else:
        previous_height = last_cenario[1]
        previous_length = last_cenario[2]
        previous_cohesion = last_cenario[3]
        previous_friction_angle = last_cenario[4]
        previous_weight = last_cenario[5]
        previous_fs = last_cenario[6]
        previous_id = last_cenario[0]
    
    # Define the grid we will analyse
    height = [5, 10, 15]
    length = [1, 2, 3]
    weight = [x for x in range(15, 25, 1)]
    cohesion = [x for x in range(41)]
    friction_angle = [x for x in range(41)]

    # Create the combinations
    combinations = list(product(height, length, weight, cohesion, friction_angle))

    # Filter the already done combinations
    start_index = previous_id if previous_id else 0
    print(start_index)

    # Iterate over the combinations
    for id, (height, length, weight, cohesion, friction_angle) in enumerate(combinations[start_index:], start=start_index):
        
        # Check if cohesion AND friction angle are zero
        if cohesion == 0 and friction_angle == 0:
            previous_fs = 0
            to_add = {
                'height' : height,
                'length' : height*length,
                'cohesion' : cohesion,
                'friction' : friction_angle,
                'weight' : weight,
                'fs' : 0,
                'id_combinations' : id,
            }
            db.add('results', to_add)
            continue
        
        # Check if friction angle is zero (reset the minimum fs):
        if friction_angle == 0:
            previous_fs = 0

        # Check if the past cenario was greater than max fs
        if previous_fs >= max_fs:
            to_add = {
                'height' : height,
                'length' : length*height,
                'cohesion' : cohesion,
                'friction' : friction_angle,
                'weight' : weight,
                'fs' : previous_fs,
                'id_combinations' : id,
            }
            db.add('results', to_add)
            continue

        # Calculate slope
        s = get_slope(height=height, length=length*height, cohesion=cohesion, friction_angle=friction_angle, weight=weight)
        min_fs = round(s.get_min_FOS(), 2) if round(s.get_min_FOS(), 2) <= max_fs else max_fs
        to_add = {
                'height' : height,
                'length' : length*height,
                'cohesion' : cohesion,
                'friction' : friction_angle,
                'weight' : weight,
                'fs' : min_fs,
                'id_combinations' : id,
            }
        db.add('results', to_add)

        previous_fs = min_fs

        if id % 100 == 0:
            print(f'Progress: {id}/{len(combinations)}')
            print(f'%: {round(id/len(combinations)*100, 2)}%')
            elapsed_time = time.time() - start_time
            hours = int(elapsed_time // 3600)
            minutes = int((elapsed_time % 3600) // 60)
            seconds = int(elapsed_time % 60)
            print(f"Time spent: {hours}:{minutes}:{seconds}")
            print('------------------------------------------------------------')
        