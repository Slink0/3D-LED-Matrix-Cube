# 3D-LED-Matrix-Cube
CSCE 462 Final Project
8×8×8 LED Matrix Cube
Overview

For this project, our group designed and built an 8×8×8 3D LED matrix cube. The system enables control of 512 LEDs arranged in a cubic structure, allowing for dynamic lighting patterns and 3D visual effects.

Hardware Design

The cube is driven using a combination of shift registers and MOSFETs to efficiently control all LEDs:

8 × 74HC595 shift registers
Used to control the columns of the LED matrix through serial-to-parallel data conversion.
8 × IRFZ44N MOSFETs
Used to switch each layer of the cube, enabling multiplexing across the 8 layers.
System Architecture
The cube operates using a layer multiplexing technique, where one layer is activated at a time.
Shift registers handle column data, while MOSFETs control which layer is currently active.
By rapidly cycling through layers, the system creates the illusion that all LEDs are lit simultaneously.
Features
512 individually addressable LEDs
3D animation capability
Efficient control using minimal microcontroller pins
Expandable and modular design
Future Improvements
Add more complex animation patterns
Implement brightness control using PWM
Integrate audio-reactive or sensor-based effects
Improve PCB design for compactness and reliability
Contributors
Nicolas Medina, Ty Macaulay
