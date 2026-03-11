import numpy as np
import pandas as pd
import pulp

# locations where you can place drones
dx = [1,5,9,1,9]
dy = [1,5,9,9,1]
drone_df = pd.DataFrame(zip(range(len(dx)),dx,dy),columns=['did','dx','dy'])

# locations of crime incidents + counts
cx = [2,6,9]
cy = [2,6,8]
cn = [10,20,3]
crime_df = pd.DataFrame(zip(range(len(cx)),cx,cy,cn),columns=['cid','cx','cy','count'])

# getting all pairwise distances
dist = pd.merge(drone_df,crime_df,how='cross')
dist.set_index(['did','cid'],inplace=True)
dist['dist'] = np.sqrt((dist['dx'] - dist['cx'])**2 + (dist['dy'] - dist['cy'])**2)

# Create the problem
prob = pulp.LpProblem("Drone_Location", pulp.LpMinimize)

# Decision variables
# x[i] = 1 if drone is placed at location i, 0 otherwise
x = pulp.LpVariable.dicts("drone_location", 
                         drone_df['did'].tolist(), 
                         cat='Binary')

# y[i,j] = 1 if crime location j is assigned to drone at location i, 0 otherwise
y = pulp.LpVariable.dicts("assignment", 
                         [(i, j) for i in drone_df['did'] for j in crime_df['cid']], 
                         cat='Binary')

# Objective function: minimize total weighted distance
prob += pulp.lpSum([crime_df.loc[j, 'count'] * dist.loc[(i,j), 'dist'] * y[(i,j)] 
                   for i in drone_df['did'] for j in crime_df['cid']])

# Constraint 1: Select exactly 2 drone locations
prob += pulp.lpSum([x[i] for i in drone_df['did']]) == 2

# Constraint 2: Each crime location must be assigned to exactly one drone
for j in crime_df['cid']:
    prob += pulp.lpSum([y[(i,j)] for i in drone_df['did']]) == 1

# Constraint 3: Can only assign to selected drone locations
for i in drone_df['did']:
    for j in crime_df['cid']:
        prob += y[(i,j)] <= x[i]

# Solve the problem
prob.solve()

# Print results
print("Status:", pulp.LpStatus[prob.status])
print("Optimal total weighted distance:", pulp.value(prob.objective))
print("\nSelected drone locations:")
for i in drone_df['did']:
    if x[i].varValue == 1:
        print(f"Drone {i}: position ({drone_df.loc[i, 'dx']}, {drone_df.loc[i, 'dy']})")

print("\nCrime assignments:")
for j in crime_df['cid']:
    for i in drone_df['did']:
        if y[(i,j)].varValue == 1:
            crime_pos = (crime_df.loc[j, 'cx'], crime_df.loc[j, 'cy'])
            drone_pos = (drone_df.loc[i, 'dx'], drone_df.loc[i, 'dy'])
            distance = dist.loc[(i,j), 'dist']
            count = crime_df.loc[j, 'count']
            print(f"Crime {j} at {crime_pos} (count: {count}) assigned to Drone {i} at {drone_pos} (distance: {distance:.2f})")

import matplotlib.pyplot as plt

# Create the plot
plt.figure(figsize=(6,4)) # figsize=(10, 8)

# Plot crime locations as graduated points (size based on count)
crime_sizes = crime_df['count'] * 20  # Scale factor for visibility
plt.scatter(crime_df['cx'], crime_df['cy'], s=crime_sizes, 
           c='blue', alpha=0.7, label='Crime Locations', edgecolors='black')

# Add crime count labels
for i, row in crime_df.iterrows():
    #plt.annotate(f'C{i}\n({row["count"]})', 
    #            (row['cx'], row['cy']), 
    #            xytext=(5, 5), textcoords='offset points',
    #            fontsize=9, ha='left')

# Plot drone locations
selected_drones = [i for i in drone_df['did'] if x[i].varValue == 1]
not_selected_drones = [i for i in drone_df['did'] if x[i].varValue == 0]

# Plot non-selected drones as grey
for i in not_selected_drones:
    plt.scatter(drone_df.loc[i, 'dx'], drone_df.loc[i, 'dy'], 
               s=100, c='grey', marker='s', alpha=0.5, edgecolors='black')
    #plt.annotate(f'D{i}', 
    #            (drone_df.loc[i, 'dx'], drone_df.loc[i, 'dy']), 
    #            xytext=(5, -15), textcoords='offset points',
    #            fontsize=9, ha='center', color='grey')

# Plot selected drones as larger red
for i in selected_drones:
    plt.scatter(drone_df.loc[i, 'dx'], drone_df.loc[i, 'dy'], 
               s=200, c='red', marker='s', edgecolors='black', linewidth=2)
    #plt.annotate(f'D{i}', 
    #            (drone_df.loc[i, 'dx'], drone_df.loc[i, 'dy']), 
    #            xytext=(5, -15), textcoords='offset points',
    #            fontsize=10, ha='center', color='red', weight='bold')

# Draw assignment lines
for j in crime_df['cid']:
    for i in drone_df['did']:
        if y[(i,j)].varValue == 1:
            plt.plot([crime_df.loc[j, 'cx'], drone_df.loc[i, 'dx']], 
                    [crime_df.loc[j, 'cy'], drone_df.loc[i, 'dy']], 
                    'k--', alpha=0.5, linewidth=1)

# Formatting
plt.xlabel('X Coordinate')
plt.ylabel('Y Coordinate')
plt.title('Drone Location Solution')
plt.grid(True, alpha=0.3)

# Create custom legend
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', 
           markersize=10, alpha=0.7, label='Crime Locations (size = count)'),
    Line2D([0], [0], marker='s', color='w', markerfacecolor='red', 
           markersize=12, label='Selected Drone Locations'),
    Line2D([0], [0], marker='s', color='w', markerfacecolor='grey', 
           markersize=8, alpha=0.5, label='Non-selected Drone Locations'),
    Line2D([0], [0], color='black', linestyle='--', alpha=0.5, 
           label='Assignments')
]
plt.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc='upper left')

plt.tight_layout()
plt.show()