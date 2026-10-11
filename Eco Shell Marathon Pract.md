| Physical Effect                     | Formula                                 | Reason                                                                                                                                                                                                                                |
| ----------------------------------- | --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Drag                                | $F_{drag} = \frac{1}{2} \rho v^2 C_d A$ | small changes in the drag coefficient ($C_d$) or frontal area ($A$) can effect energy  consumption significantly                                                                                                                      |
| Electric Motor Efficiency           | N/A                                     | Plotting a graph of torque vs RPM vs energy consumption, will allow us to find the optimal RPM/ Torque to operate the car at                                                                                                          |
| Battery Internal Resistance         | $P =I^2 R$                              | As the battery drains, its voltage drops, meaning more current is required to maintain the same power output. Other factors could also be cold temperaturs which would then increase the internal resistance, increasing energy waste |
| Transmission Losses                 |                                         | Through data collection will need to collect average loss due to frictional losses, which will then be incorperated as a constant into the moddel                                                                                     |
| Other                               |                                         |                                                                                                                                                                                                                                       |
| Driver strategy                     |                                         | Lift and coast is a common technique used in F1 to reduce energy losses due to braking and improve fuel economy, a similar approach can be used for this challenge.                                                                   |
| Gradient Resistance                 | $F_{grad} = m g \sin(\theta)$           | Track elevation can lead to different strategies, eg slower speeds up hill since more energy is required, and coasting down hill                                                                                                      |
| Wind Speed & Direction              |                                         | Adding in a wind speed vector can be usefull to test for worst case senarios                                                                                                                                                          |
| Temperature, Location, and Altitude |                                         | As temperature or altitude increase, air density will deccrease, as a result the drag will decrease , this will lead to a change in strategy (longer coasting periods)                                                                |
|                                     |                                         |                                                                                                                                                                                                                                       |
|                                     |                                         |                                                                                                                                                                                                                                       |

# Calculating % of Battery left (State of Charge (SOC))
## Method - Coulomb Counting
- measuring how much current flows in and out of the battery over time
- Formula: SoC(t) = SoC(initial) + (efficiency / battery capacity) $\int C dt$ where $C = Current$  
- $SOC=\frac{C_{releasable}}{C_{rated}}$ 
- Where $C_{releasable}$ is the charge level of the battery, in Ah, and $C_{rated}$ is the battery rated capacity, in Ah
## Temperature and Discharge Rate Effects
- capacity changes with temperature
- model the capacity loss as a function of both discharge rate and temperature
- **Peukert’s law**: the faster you drain a battery, the less total capacity you get
- Capacity = $C^k*t$ where k = Peukert constant (typically between 1.1 and 1.4 for lead-acid)
## Kalman filters
- Predict the future state of charge of the battery and update this prediction based on new measurements. I won't implement this cuz I don't have actual values
## Equivalent Circuit
- Assuming the battery as a perfect voltage source in series with a resistor.
- $V_{term}(t) = V_{OCV}(SOC, T) - I(t) \cdot R_{int}(SOC, T)$
- $V_{term}$ is the actual terminal voltage delivered to the motor controller.    
- $V_{OCV}$ is the resting voltage of the battery.    
- $R_{int}$ is the internal resistance.
- Using a LUT to find $V_{OCV}$ and $R_{int}$ at each time step
## Battery Heat Generation
- Ohmic part: $P = I^2R$
- The Bernardi equation: heat associated with entropy changes in the electrode reactions
- Formula: $Q_{gen} = \frac{1}{V_{b}}[(E_{OC} - V_{T})-IT \frac{\partial E_{OC}}{\partial T}]$ Units of q: $Wm^{-3}$ Lowk I don't rlly know what is goin on here but the code is right soo...
- Updating Cell temperature: $T(t) = T(t-1) + \frac{\dot{Q}_{gen} - \dot{Q}_{cool}}{m \cdot c_p} \cdot \Delta t$

| Symbol                                 | Meaning                                               | Units                                                       |
| -------------------------------------- | ----------------------------------------------------- | ----------------------------------------------------------- |
| *I*                                    | Current                                               | A                                                           |
| *$V_b$*                                | Cell Volume                                           | $m^3$                                                       |
| *$E_{OC}$*                             | Open-circuit voltage at current SOC and TT            | V                                                           |
| *$V_T$*                                | Terminal voltage under load                           | V                                                           |
| *T*                                    | Cell temperature                                      | K                                                           |
| *$\frac{\partial E_{OC}}{\partial T}$* | Entropic coefficient at fixed SOC                     | $VK^{-1}$                                                   |
| $c_p$                                  | specific heat capacity of the battery cells           | $800 \text{ to } 1000 \text{ J}/(\text{kg} \cdot \text{K})$ |
| $m$                                    | masss                                                 | Kg                                                          |
| $\dot{Q}_{cool}$                       | heat loss through cooling via Newton's Law of Cooling | $Wm^{-2}$                                                   |
|                                        |                                                       |                                                             |
|                                        |                                                       |                                                             |
|                                        |                                                       |                                                             |

# Conclusion from the code
- Lift and Coasting strat is actually pretty bad for battery efficienies and regulating temperatures
- This is because doubling the current draw more than doubles the capacity drain. So spikes drain the battery fastes than steady usage
- A spike in current increase lost volts, the energy is lost as heat in the battery
- However it is not enough information to conclude that lift and coast is a poor strategy since overall it might be more efficient when looking at the whole picture.
	Data to support conclusion
	--- Strategy: Constant Current (Steady Speed) ---
	Total Energy Delivered: 8307.86 Joules
	Remaining SOC:          98.74%
	Final Temperature:      24.99 °C
	
	--- Strategy: Coasting (fast then no throttle) ---
	Total Energy Delivered: 7985.98 Joules
	Remaining SOC:          98.26%
	Final Temperature:      25.05 °C

# Future developments
- I would incoperate the Kalman filter and work with live inputs of current draw form sensors.
- Would further develop the model to include more resistive forces such as drag
- I would model the entire track and then run a evolutionary algorithm to find the best areas to accelerate.
## Verification and Validation
- To verify the data, I would track every joule leavigng the battery, see where it is going, eg kinetic energy, energy lost due to friction (or drag) or heat
- Test the code with boundary cases.
- To validate the battery simulation, could isolate the battery and then just pull current similiar to the simulation and see if the results match
- Some errors will have more significant effects then others such as Peukert constant which is used as an exponent, and compound errors always a threat in computer simulations. So would need to test with a small range of "constants" around the predicted constant to see its effect over a longer period of time.
## References 
- [How to Calculate SOC of a Battery: All Key Methods](https://scienceinsights.org/how-to-calculate-soc-of-a-battery-all-key-methods/)
- [Explore Techniques to Estimate Battery State of Charge](https://www.mathworks.com/help/simscape-battery/ug/estimate-battery-soc-using-kalman-filter-example.html)
- [Battery Heat Generation](https://www.batterydesign.net/battery-heat-generation/)
# Task
- [x] Identify main physical effects you would include, and explain your reasoning
- [x] Demonstrate one part of your proposed model through a worked numerical example, using hand calculations, a spreadsheet or a short piece of code
- [x] Use this example to investigate how changing one vehicle parameter or operating condition affects predicted energy consumption and explain what the result tells you.
- [ ] Explain how you would extend this calculation into a simulation of a complete run
- [ ] Assess confidence in predictions through verification and validation, and assess its sensitivity to uncertain inputs.
- [x] Support your proposal with equations, diagrams or plots where appropriate.