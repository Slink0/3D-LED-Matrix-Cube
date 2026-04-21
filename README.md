# CSCE 462 Final Project  
## 8x8x8 LED Matrix Cube

## Overview
This project involves the design and implementation of an **8×8×8 3D LED matrix cube**. The system integrates hardware and software to create dynamic lighting patterns in three dimensions, along with a real-time visualization.

## Features
- 512 LEDs arranged in an 8×8×8 cube structure  
- Layered multiplexing for efficient control  
- Real-time simulation using Python and Matplotlib  
- Hardware-driven animations via Raspberry Pi  

## Hardware Components
- 8 × 74HC595 Shift Registers  
- 8 × IRFZ44N MOSFETs  
- Raspberry Pi (controller)  
- 512 LEDs  
- Supporting resistors, wiring, and power supply  

## System Architecture
The cube is controlled using a combination of shift registers and MOSFETs:

- **74HC595 Shift Registers** handle column data (LED states)  
- **IRFZ44N MOSFETs** control each layer (8 layers total)  
- **Multiplexing** is used to rapidly switch between layers, creating the illusion that all LEDs are lit simultaneously  

## Software
- The Raspberry Pi runs control code to:
  - Send data to the shift registers  
  - Manage timing for multiplexing  
  - Generate animation patterns  

- A **Matplotlib-based simulation** mirrors the physical cube in real time for debugging and visualization.

## How It Works
1. Data for a single layer is sent to the shift registers  
2. The corresponding MOSFET activates that layer  
3. The system rapidly cycles through all 8 layers  
4. Persistence of vision creates a stable 3D image  

## Applications
- 3D visual displays  
- Educational demonstrations of multiplexing and embedded systems  
- Interactive lighting effects  

## Future Improvements
- Increase refresh rate for smoother animations  
- Add user input or network control  
- Implement more complex 3D animation algorithms  

## Authors
Nicolas Medina, Ty Macaulay
