---
title: "Drone Simulator v1.0"
date: 2019-10-02
unity_dir: drone03
categories:
  - Simulation
  - v1.0
tags:
  - Unity
  - Drone 
  - Simulation
  - Training

---
## Patch Notes
Version 1.0 is here with the following changes:

### Added training mode
Added a training mode that minimizes the GPU/CPU overhead so that the game can be run faster. Training mode cannot be toggled within the web game.

### Added targets
Targets *might* spawn randomly within a preset area. Collect the targets to increase your score.

### Fixed bouncy & invisible collider bug
Version 0.2 had weird interactions with the colliders whenever interior would spawn. This was caused by an animation script that would make the drone sway slightly while hovering, which has subsequently been removed.

### Adjusted drone forces 
As the hover script mentioned above significantly impacted the drone physics, some forces (climbing speed, velocity etc.) have been adjusted to make it feel more like a real drone.

### Changed lighting
All lights have been substituted for a prebaked lightmap to increase performance.

### Added restarts upon collision and collecting all targets
The game now reloads the scene after colliding or after obtaining all targets in that stage.

## Controls
W -- Move forward  
A -- Move left  
S -- Move back  
D -- Move right  
I -- Ascend  
K -- Descend  
Q -- Rotate anti-clockwise  
E -- Rotate clockwise  
