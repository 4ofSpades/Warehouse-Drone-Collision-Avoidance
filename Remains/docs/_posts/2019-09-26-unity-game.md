---
title: "Drone Simulator v0.2"
date: 2019-09-26
unity_dir: drone02
categories:
  - Simulation
  - v0.2
tags:
  - Unity
  - Drone 
  - Simulation
  - Training

---
## Patch Notes
Version 0.2 is here with the following changes:

### Added interior spawning
Interior *might* spawn at preset locations. In the default setting, there is a 10% chance for a pair of racks to not spawn.

### Added restart to timer
The stage will restart and regenerate once the timer runs out now. This also means that the timer won't hit negative numbers anymore.

### Added drone spawner
Instead of adding the drone in the editor, the drone will now be spawned at a slighly varying position everytime the stage is generated.

### Removed negative scales
The original prefab models inverted some parts to create symmetry by using a negative scale. This was changed to making use of rotations instead. Since some parts only contain textures on one side, some walls have the textures of the outside now instead of the inside. However, these textures are only for aesthetical purposes and won't affect the gameplay.

### Removed shadows, lowered quality
The rendering quality has been set to the lowest setting, and most shadow casting has been removed to decrease GPU load. This was done in order to save as much processing power for training.

### Fixed rotation
In the previous version rotation was not functioning. This should work from this version onwards again.

### Removed 3rd person camera
While only the 3rd person camera was used, the old version had both a 3rd and 1st person cam attached. The 3rd person cam has been removed in order to decrease computational load.

## Controls
W -- Move forward  
A -- Move left  
S -- Move back  
D -- Move right  
I -- Ascend  
K -- Descend  
Q -- Rotate anti-clockwise  
E -- Rotate clockwise  
