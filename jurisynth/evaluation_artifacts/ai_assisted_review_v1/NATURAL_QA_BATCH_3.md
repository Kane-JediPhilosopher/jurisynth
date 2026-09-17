# AI-assisted natural-QA reference and retrieval review

Phase A: validate questions, draft reference answers and answer-bearing retrieval.
No system answers exist for these stored retrieval cases. Do NOT assign system PASS/PARTIAL/FAIL or QA accuracy yet.
Do not accept source applicability, alternate-source equivalence or temporal coherence merely because wording matches.
Return case_id; valid/revise/reject/uncertain; final question; verified reference answer with source quotes;
expected source keys; sufficient/partial/insufficient/irrelevant retrieval; helpful retrieved source keys;
scope/date/version caveats; confidence; and review notes. Use uncertain when sources are inadequate.
Draft references are Codex proposals, not adjudicated gold. Review them independently.

## global_natural_011

Which measurements must be collected during the road-load curve determination procedure?

Draft reference: Elapsed time, vehicle speed and relative air velocity (wind speed/direction) at 5 Hz; synchronised ambient temperature at least 1 Hz. Preserve the procedure-specific scope.

Retrieval execution status: success (NOT relevance)

### Expected: L_2017175EN.01000101 / chunk_157

Resolution: document_chunk_sqlite

```text
4.3.2.2. Selection of vehicle speed range for road load curve determination
The test vehicle speed range shall be selected according to paragraph 2.2. of this Sub-Annex.
4.3.2.3. Data collection
During the procedure, elapsed time, vehicle speed, and air velocity (wind speed, direction) relative to the vehicle, shall be measured at a frequency of 5 Hz. Ambient temperature shall be synchronised and sampled at a minimum frequency of 1 Hz.
4.3.2.4. Vehicle coastdown procedure
The measurements shall be carried out in opposite directions until a minimum of ten consecutive runs (five in each direction) have been obtained. Should an individual run fail to satisfy the required on-board anemometry test conditions, that run and the corresponding run in the opposite direction shall be rejected. All valid pairs shall be included in the final analysis with a minimum of 5 pairs of coastdown runs. See paragraph 4.3.2.6.10. of this Sub-Annex for statistical validation criteria.
The anemometer shall be installed in a position such that the effect on the operating characteristics of the vehicle is minimised.
The anemometer shall be installed according to one of the options below:
(a) Using a boom approximately 2 metres in front of the vehicle's forward aerodynamic stagnation point; (b) On the roof of the vehicle at its centreline. If possible, the anemometer shall be mounted within 30 cm from the top of the windshield. (c) On the engine compartment cover of the vehicle at its centreline, mounted at the midpoint position between the vehicle front and the base of the windshield.
In all cases, the anemometer shall be mounted parallel to the road surface. In the event that positions (b) or (c) are used, the coastdown results shall be analytically adjusted for the additional aerodynamic drag induced by the anemometer. The adjustment shall be made by testing the coastdown vehicle in a wind tunnel both with and without the anemometer installed in the same position as used on the track., The calculated difference shall be the incremental aerodynamic drag coefficient C D combined with the frontal area, which shall be used to correct the coastdown results.
4.3.2.4.1. Following the vehicle warm-up procedure described in paragraph 4.2.4. of this Sub-Annex and immediately prior to each test measurement, the vehicle shall be accelerated to 10 to 15 km/h above the highest reference speed and shall be driven at that speed for a maximum of 1 minute. After that, the coastdown shall be started immediately. 4.3.2.4.2. During a coastdown, the transmission shall be in neutral. Any steering wheel movement shall be avoided as much as possible, and the vehicle's brakes shall not be operated. 4.3.2.4.3. It is recommended that each coastdown run be performed without interruption. Split runs may however be performed if data cannot be collected in a single run for all the reference speed points. For split runs, care shall be taken so that vehicle conditions remain as stable as possible at each split point.
4.3.2.5. Determination of the equation of motion
Symbols used in the on-board anemometer equations of motion are listed in Table A4/4.
Table A4/4
Symbols used in the on-board anemometer equations of motion
4.3.2.5.1. General form
The general form of the equation of motion is as follows:
where:
D mech = D tyre f r D aero = D grav =
In the case that the slope of the test track is equal to or less than 0.1 per cent over its length, D grav may be set to zero.
4.3.2.5.2. Mechanical drag modelling
Mechanical drag consisting of separate components representing tyre D tyre and front and rear axle frictional losses, D f and D r , including transmission losses) shall be modelled as a three-term polynomial as a function of vehicle speed v as in the equation below:
where:
A m , B m , and C m are determined in the data analysis using the least squares method. These constants reflect the combined driveline and tyre drag.
In the case that the tested vehicle is the representative vehicle of a road load matrix family, the coefficient B m shall be set to zero and the coefficients A m and C m shall be recalculated with a least squares regression analysis.
4.3.2.5.3. Aerodynamic drag modelling
The aerodynamic drag coefficient C D (Y) shall be modelled as a four-term polynomial as a function of yaw angle Y as in the equation below:
a 0 to a 4 are constant coefficients whose values are determined in the data analysis.
```

### Retrieved: L_2017175EN.01000101 / chunk_153

Resolution: document_chunk_sqlite

```text
4.2.1.3.1. At the request of the manufacturer and upon fulfilling the criteria of paragraph 5.7. of this Annex, the road load values for vehicles H and L of an interpolation family shall be calculated. 4.2.1.3.2. For the purposes of paragraph 4.2.1.3. of this Sub-Annex, vehicle H of a road load family shall be designated vehicle H R R 4.2.1.3.3. For the purposes of paragraph 4.2.1.3. of this Sub-Annex, vehicle L of a road load family shall be designated vehicle L R R 4.2.1.3.4. Notwithstanding the requirements referring to the range of an interpolation family in paragraphs 1.2.3.1. and 1.2.3.2. of Sub-Annex 6, the difference in cycle energy demand between H R R R If more than one transmission is included in the road load family, a transmission with the highest power losses shall be used for road load determination. 4.2.1.3.5. Road loads H R R The road load of vehicles H (and L) of an interpolation family within the road load family shall be calculated according to paragraphs 3.2.3.2.2. to 3.2.3.2.2.4. inclusive of Sub-Annex 7, by: The road load interpolation shall only be applied on those road load relevant characteristics that were identified to be different between test vehicle L R R R (a) using H R R (b) using the road load parameters (i.e. test mass, Δ(C D f R (c) repeating this calculation for each H and L vehicle of every interpolation family within the road load family.
4.2.1.4. Application of the road load matrix family
A vehicle that fulfils the criteria of paragraph 5.8. of this Annex that is:
(a) representative of the intended series of complete vehicles to be covered by the road load matrix family in terms of estimated worst C D (b) representative of the intended series of vehicles to be covered by the road load matrix family in terms of estimated average of the mass of optional equipment, shall be used to determine the road load.
In the case that no representative body shape for a complete vehicle can be determined, the test vehicle shall be equipped with a square box with rounded corners with radii of maximum of 25 mm and a width equal to the maximum width of the vehicles covered by the road load matrix family, and a total height of the test vehicle of 3,0 m ± 0,1 m, including the box.
The manufacturer and the approval authority shall agree which vehicle test model is representative.
The vehicle parameters test mass, tyre rolling resistance and frontal area of both a vehicle H M and L M shall be determined in such a way that vehicle H M produces the highest cycle energy demand and vehicle L M the lowest cycle energy from the road load matrix family. The manufacturer and the approval authority shall agree on the vehicle parameters for vehicle H M and L M .
The road load of all individual vehicles of the road load matrix family, including H M and L M , shall be calculated according to paragraph 5.1. of this Sub-Annex.
4.2.1.5. Movable aerodynamic body parts
Movable aerodynamic body parts on the test vehicles shall operate during road load determination as intended under WLTP Type 1 test conditions (test temperature, vehicle speed and acceleration range, engine load, etc.).
Every vehicle system that dynamically modifies the vehicle's aerodynamic drag (e.g. vehicle height control) shall be considered to be a movable aerodynamic body part. Appropriate requirements shall be added if future vehicles are equipped with movable aerodynamic items of optional equipment whose influence on aerodynamic drag justifies the need for further requirements.
4.2.1.6. Weighing
Before and after the road load determination procedure, the selected vehicle shall be weighed, including the test driver and equipment, to determine the arithmetic average mass, m av . The mass of the vehicle shall be greater than or equal to the test mass of vehicle H or of vehicle L at the start of the road load determination procedure.
4.2.1.7. Test vehicle configuration
The test vehicle configuration shall be included in all relevant test reports and shall be used for any subsequent coastdown testing.
4.2.1.8. Test vehicle condition
4.2.1.8.1. Run-in
The test vehicle shall be suitably run-in for the purpose of the subsequent test for at least 10 000 but no more than 80 000 km.
4.2.1.8.1.1. At the request of the manufacturer, a vehicle with a minimum of 3 000 km may be used.
```

### Retrieved: L_2017175EN.01000101 / chunk_169

Resolution: document_chunk_sqlite

```text
The coastdown test on the chassis dynamometer shall be performed with the procedure given in paragraph 8.1.3.4.1. or in paragraph 8.1.3.4.2. of this Sub-Annex and shall start no later than 120 seconds after completion of the warm-up procedure. Consecutive coastdown runs shall be started immediately. At the request of the manufacturer and with approval of the approval authority, the time between the warm-up procedure and coastdowns using the iterative method may be extended to ensure a proper vehicle setting for the coastdown. The manufacturer shall provide the approval authority with evidence for requiring additional time and evidence that the chassis dynamometer load setting parameters (e.g. coolant and/or oil temperature, force on a dynamometer) are not affected.
8.1.3. Verification
8.1.3.1. The target road load value shall be calculated using the target road load coefficient, A t , B t and C t , for each reference speed, v j :
where:
A t t t are the target road load parameters f 0 1 2 F tj is the target road load at reference speed v j v j is the j th
8.1.3.2. The measured road load shall be calculated using the following equation:
where:
F mj is the measured road load for each reference speed v j TM is the test mass of the vehicle, kg; m r is the equivalent effective mass of rotating components according to paragraph 2.5.1. of this Sub-Annex, kg; Δt j is the coastdown time corresponding to speed v j
8.1.3.3. The simulated road load on the chassis dynamometer shall be calculated according to the method as specified in paragraph 4.3.1.4. of this Sub-Annex, with the exception of measuring in opposite directions, and with applicable corrections according to paragraph 4.5. of this Sub-Annex, resulting in a simulated road load curve:
The simulated road load for each reference speed v j shall be determined using the following equation, using the calculated A s , B s and C s :
8.1.3.4. For dynamometer load setting, two different methods may be used. If the vehicle is accelerated by the dynamometer, the methods described in paragraph 8.1.3.4.1. of this Sub-Annex shall be used. If the vehicle is accelerated under its own power, the methods in paragraphs 8.1.3.4.1. or 8.1.3.4.2. of this Sub-Annex shall be used. The minimum acceleration multiplied by speed shall be 6 m 2 /sec 3 . Vehicles which are unable to achieve 6 m 2 /s 3 shall be driven with the acceleration control fully applied.
8.1.3.4.1. Fixed run method
8.1.3.4.1.1. The dynamometer software shall perform four coastdowns in total: From the first coastdown, the dynamometer setting coefficients for the second run according to paragraph 8.1.4. of this Sub-Annex shall be calculated. Following the first coastdown, the software shall perform three additional coastdowns with either the fixed dynamometer setting coefficients determined after the first coastdown or the adjusted dynamometer setting coefficients according to paragraph 8.1.4. of this Sub-Annex. 8.1.3.4.1.2. The final dynamometer setting coefficients A, B and C shall be calculated using the following equations: where: A t t t are the target road load parameters f 0 1 2 A sn sn sn are the simulated road load coefficients of the n th A dn dn dn are the dynamometer setting coefficients of the n th n is the index number of coastdowns including the first stabilisation run.
8.1.3.4.2. Iterative method
The calculated forces in the specified speed ranges shall either be within a tolerance of ± 10 N after a least squares regression of the forces for two consecutive coastdowns, or additional coastdowns shall be performed after adjusting the chassis dynamometer load setting according to paragraph 8.1.4. of this Sub-Annex until the tolerance is satisfied.
8.1.4. Adjustment
The chassis dynamometer setting load shall be adjusted according to the following equations:
Therefore:
where:
F dj is the initial chassis dynamometer setting load, N; F * dj is the adjusted chassis dynamometer setting load, N; F j is the adjustment road load equal to (F sj tj F sj is the simulated road load at reference speed v j F tj is the target road load at reference speed v j A * d * d * d are the new chassis dynamometer setting coefficients.
```

### Retrieved: L_2018301EN.01000101 / chunk_83

Resolution: document_chunk_sqlite

```text
f 0 1 2 0 1 2 2 Unless otherwise stated, the road load coefficients shall be calculated with a least square regression analysis over the range of the reference speed points.'; f 0 is the constant road load coefficient and shall be rounded to one place of decimal, N; f 1 is the first order road load coefficient and shall be rounded to three places of decimal, N/(km/h); f 2 is the second order road load coefficient and shall be rounded to five places of decimal, N/(km/h) 2 (b) in point 2.5.3., the first paragraph below the title is replaced by the following: 'If the vehicle is tested on a dynamometer in 4WD operation, the equivalent inertia mass of the chassis dynamometer shall be set to the applicable test mass.'; (c) the following point 2.6. is inserted: '2.6. Additional masses for setting the test mass shall be applied such that the weight distribution of that vehicle is approximately the same as that of the vehicle with its mass in running order. In the case of category N vehicles or passenger vehicles derived from category N vehicles, the additional masses shall be located in a representative manner and shall be justified to the approval authority upon their request. The weight distribution of the vehicle shall be included in all relevant test reports and shall be used for any subsequent road load determination testing.'; (d) points 3. and 3.1. are replaced by the following: '3. General requirements The manufacturer shall be responsible for the accuracy of the road load coefficients and shall ensure this for each production vehicle within the road load family. Tolerances within the road load determination, simulation and calculation methods shall not be used to underestimate the road load of production vehicles. At the request of the approval authority, the accuracy of the road load coefficients of an individual vehicle shall be demonstrated. 3.1. Overall measurement accuracy, precision, resolution and frequency The required overall measurement accuracy shall be as follows: (a) Vehicle speed accuracy: ± 0,2 km/h with a measurement frequency of at least 10 Hz; (b) Time: min. accuracy: ± 10 ms; min. precision and resolution:10 ms; (c) Wheel torque accuracy: ± 6 Nm or ± 0,5 per cent of the maximum measured total torque, whichever is greater, for the whole vehicle, with a measurement frequency of at least 10 Hz; (d) Wind speed accuracy: ± 0,3 m/s, with a measurement frequency of at least 1 Hz; (e) Wind direction accuracy: ± 3°, with a measurement frequency of at least 1 Hz; (f) Atmospheric temperature accuracy: ± 1 °C, with a measurement frequency of at least 0,1 Hz; (g) Atmospheric pressure accuracy: ± 0,3 kPa, with a measurement frequency of at least 0,1 Hz; (h) Vehicle mass measured on the same weighing scale before and after the test: ± 10 kg (± 20 kg for vehicles > 4 000 kg); (i) Tyre pressure accuracy: ± 5 kPa; (j) Wheel rotational speed accuracy: ± 0,05 s - 1 (e) points 3.2.5., 3.2.6. and 3.2.7. are replaced by the following: '3.2.5. Rotating wheels To properly determine the aerodynamic influence of the wheels, the wheels of the test vehicle shall rotate at such a speed that the resulting vehicle velocity is within ± 3 km/h of the wind velocity. 3.2.6. Moving belt To simulate the fluid flow at the underbody of the test vehicle, the wind tunnel shall have a moving belt extending from the front to the rear of the vehicle. The speed of the moving belt shall be within ± 3 km/h of the wind velocity. 3.2.7. Fluid flow angle At nine equally distributed points over the nozzle area, the root mean square deviation of both the pitch angle α and the yaw angle β (Y-, Z-plane) at the nozzle outlet shall not exceed 1°.'; (f) point 3.2.12. is replaced by the following: '3.2.12. Measurement precision The precision of the measured force shall be within ± 3 N.'; (g) points 4.1.1.1., 4.1.1.1.1. and 4.1.1.1.2. are replaced by the following: '4.1.1.1. Permissible wind conditions The maximum permissible wind conditions for road load determination are described in paragraphs 4.1.1.1.1. and 4.1.1.1.2.
```

### Retrieved: L_2018301EN.01000101 / chunk_85

Resolution: document_chunk_sqlite

```text
Requirements for families;' (k) the following points 4.2.1.2.1. to 4.2.1.2.3.4. are inserted: '4.2.1.2.1. Requirements for applying the interpolation family without using the interpolation method For the criteria defining an interpolation family, see paragraph 5.6. of this Annex. 4.2.1.2.2. Requirements for applying the interpolation family using the interpolation method are: 4.2.1.2.3. Requirements for applying the road load family 4.2.1.2.3.1. At the request of the manufacturer and upon fulfilling the criteria of paragraph 5.7. of this Annex, the road load values for vehicles H and L of an interpolation family shall be calculated. 4.2.1.2.3.2. Test vehicles H and L as defined in paragraph 4.2.1.1.2. shall be referred to as H R R 4.2.1.2.3.3. In addition to the requirements of an interpolation family in paragraphs 2.3.1. and 2.3.2. of Sub-Annex 6, the difference in cycle energy demand between H R R R If more than one transmission is included in the road load family, a transmission with the highest power losses shall be used for road load determination. 4.2.1.2.3.4. If the road load delta of the vehicle option causing the friction difference is determined in accordance with paragraph 6.8., a new road load family shall be calculated which includes the road load delta in both vehicle L and vehicle H of that new road load family. f 0,N 0,R 0,Delta f 1,N 1,R 1,Delta f 2,N 2,R 2,Delta where: (a) Fulfilling the interpolation family criteria listed in paragraph 5.6. of this Annex; (b) Fulfilling the requirements in paragraphs 2.3.1. and 2.3.2. of Sub-Annex 6; (c) Performing the calculations in paragraph 3.2.3.2. of Sub-Annex 7. N refers to the road load coefficients of the new road load family; R refers to the road load coefficients of the reference road load family; Delta refers to the delta road load coefficients determined in paragraph 6.8.1.'; (m) points 4.2.1.3.2, 4.2.1.3.3., 4.2.1.3.4. and 4.2.1.3.5. are deleted; (n) in point 4.2.1.8.1., the following paragraph is added: 'At the request of the manufacturer, a vehicle with a minimum of 3 000 km may be used.'; (o) point 4.2.1.8.1.1. is deleted; (p) point 4.2.1.8.5. is replaced by the following: '4.2.1.8.5. Vehicle coastdown mode If the determination of dynamometer settings cannot meet the criteria described in paragraphs 8.1.3. or 8.2.3. due to non-reproducible forces, the vehicle shall be equipped with a vehicle coastdown mode. The vehicle coastdown mode shall be approved by the approval authority and its use shall be included in all relevant test reports. If a vehicle is equipped with a vehicle coastdown mode, it shall be engaged both during road load determination and on the chassis dynamometer.'; (q) point 4.2.1.8.5.1. is deleted; (s) in point 4.2.2.2., the following paragraph is added: 'After measurement of tread depth, the driving distance shall be limited to 500 km. If 500 km are exceeded, the tread depth shall be measured again.'; (t) point 4.2.2.2.1. is deleted; (u) point 4.2.4.1.2., is amended ad follows: (i) the first paragraph below the title is replaced by the following: 'All vehicles shall be driven at 90 per cent of the maximum speed of the applicable WLTC. The vehicle shall be warmed up for at least 20 minutes until stable conditions are reached.'; (ii) Table A4/2 is replaced by the following; ' Table A4/3 Reserved'; (v) points 4.3.1.1. and 4.3.1.2. are replaced by the following: '4.3.1.1.
```

### Retrieved: L_2017175EN.01000101 / chunk_150

Resolution: document_chunk_sqlite

```text
2.4. f 0 , f 1 , f 2 are the road load coefficients of the road load equation F = f 0 + f 1 × v + f 2 × v 2 , determined according to this Sub-Annex.
f 0 is the constant road load coefficient, N; f 1 is the first order road load coefficient,, N/(km/h); f 2 is the second order road load coefficient, N/(km/h) 2
Unless otherwise stated, the road load coefficients shall be calculated with a least square regression analysis over the range of the reference speed points.
2.5. Rotational mass
2.5.1. Determination of m r
m r is the equivalent effective mass of all the wheels and vehicle components rotating with the wheels on the road while the gearbox is placed in neutral, in kilograms (kg). m r shall be measured or calculated using an appropriate technique agreed upon by the approval authority. Alternatively, m r may be estimated to be 3 per cent of the sum of the mass in running order and 25 kg.
2.5.2. Application of rotational mass to the road load
Coastdown times shall be transferred to forces and vice versa by taking into account the applicable test mass plus m r . This shall apply to measurements on the road as well as on a chassis dynamometer.
2.5.3. Application of rotational mass for the inertia setting
If the vehicle is tested on a 4 wheel drive dynamometer and if both axles are rotating and influencing the dynamometer measurement results, the equivalent inertia mass of the chassis dynamometer shall be set to the applicable test mass.
Otherwise, the equivalent inertia mass of the chassis dynamometer shall be set to the test mass plus either the equivalent effective mass of the wheels not influencing the measurement results or 50 per cent of m r .
1. General requirements
The manufacturer shall be responsible for the accuracy of the road load coefficients and will ensure this for each production vehicle within the road load family. Tolerances within the road load determination, simulation and calculation methods shall not be used to underestimate the road load of production vehicles. At the request of the approval authority, the accuracy of the road load coefficients of an individual vehicle shall be demonstrated.
3.1. Overall measurement accuracy
The required overall measurement accuracy shall be as follows:
(a) Vehicle speed: ± 0,2 km/h with a measurement frequency of at least 10 Hz; (b) Time accuracy, precision and resolution: min. ± 10 ms; (c) Wheel torque: ± 6 Nm or ± 0,5 per cent of the maximum measured total torque, whichever is greater, for the whole vehicle, with a measurement frequency of at least 10 Hz; (d) Wind speed: ± 0,3 m/s, with a measurement frequency of at least 1 Hz; (e) Wind direction: ± 3°, with a measurement frequency of at least 1 Hz; (f) Atmospheric temperature: ± 1 °C, with a measurement frequency of at least 0,1 Hz; (g) Atmospheric pressure: ± 0,3 kPa, with a measurement frequency of at least 0,1 Hz; (h) Vehicle mass measured on the same weigh scale before and after the test: ± 10 kg (± 20 kg for vehicles > 4 000 kg); (i) Tyre pressure: ± 5 kPa; (j) Wheel rotational frequency: ± 0,05 s -1
3.2. Wind tunnel criteria
3.2.1. Wind velocity
The wind velocity during a measurement shall remain within ± 2 km/h at the centre of the test section. The possible wind velocity shall be at least 140 km/h.
3.2.2. Air temperature
The air temperature during a measurement shall remain within ± 3 °C at the centre of the test section. The air temperature distribution at the nozzle outlet shall remain within ± 3 °C.
3.2.3. Turbulence
For an equally-spaced 3 by 3 grid over the entire nozzle outlet, the turbulence intensity, Tu, shall not exceed 1 per cent. See Figure A4/1.
Figure A4/1
Turbulence intensity
where:
Tu is the turbulence intensity; u′ is the turbulent velocity fluctuation, m/s; U ∞ is the free flow velocity, m/s.
3.2.4. Solid blockage ratio
The vehicle blockage ratio ε sb expressed as the quotient of the vehicle frontal area and the area of the nozzle outlet as calculated using the following equation, shall not exceed 0,35.
where:
ε sb is the vehicle blockage ratio; A f is the frontal area of the vehicle, m 2 A nozzle is the nozzle outlet area, m 2
```

### Retrieved: L_2018301EN.01000101 / chunk_87

Resolution: document_chunk_sqlite

```text
the following amendments are made: (i) in the first paragraph after the title, the words 'Table A4/5' are replaced by the words 'Table A4/6'; (ii) in the title of the table, the words 'Table A4/5' are replaced by the words 'Table A4/6'; (ah) in point 4.4.3.2., the text: is replaced with the following: 'h is a coefficient as a function of n as given in Table A4/3 in paragraph 4.3.1.4.2. of this Sub-Annex.' 'h is a coefficient as a function of n as given in Table A4/4 in paragraph 4.3.1.4.2. of this Sub-Annex.'; (ai) in point 4.4.4., in the first paragraph below the title, the introductory part is replaced by the following: 'The arithmetic average speed and arithmetic average torque at each reference speed point shall be calculated using the following equations:'; (aj) point 4.5.3.1.1. is replaced by the following: '4.5.3.1.1. A wind correction for the absolute wind speed alongside the test road shall be made by subtracting the difference that cannot be cancelled out by alternate runs from the coefficient f 0 0 (ak) in point 4.5.4., the line for 'm av 'm av is the arithmetic average of the test vehicle masses at the beginning and end of road load determination, kg.'; (al) in point 4.5.5.1., the lines for 'f 1 2 'f 1 is the coefficient of the first order term, N/(km/h); f 2 is the coefficient of the second order term, N/(km/h) 2 (am) in point 4.5.5.2.1., the lines for 'c1' and 'c2' are replaced by the following: 'c 1 is the coefficient of the first order term as determined in paragraph 4.4.4., Nm/(km/h); c 2 is the coefficient of the second order term as determined in paragraph 4.4.4., Nm/(km/h) 2 (an) point 5.1.1.1. is replaced by the following: '5.1.1.1. The road load force for an individual vehicle shall be calculated using the following equation: F c 0 1 2 2 where: For the tyres fitted to an individual vehicle, the value of the rolling resistance RR shall be set to the class value of the applicable tyre energy efficiency class in accordance with Table A4/2. If the tyres on the front and rear axles belong to different energy efficiency classes, the weighted mean shall be used, calculated using the equation in paragraph 3.2.3.2.2.2. of Sub-Annex 7. If the same tyres were fitted to test vehicles L and H, the value of RR ind H F c is the calculated road load force as a function of vehicle velocity, N; f 0 is the constant road load coefficient, N, defined by the equation: f 0r is the constant road load coefficient of the representative vehicle of the road load matrix family, N; f 1 is the first order road load coefficient, N/(km/h), and shall be set to zero; f 2 is the second order road load coefficient, N/(km/h) 2 f 2 2r 2r f fr 2r 2r f fr f 2r is the second order road load coefficient of the representative vehicle of the road load matrix family, N/(km/h) 2 v is the vehicle speed, km/h; TM is the actual test mass of the individual vehicle of the road load matrix family, kg; TM r is the test mass of the representative vehicle of the road load matrix family, kg; A f is the frontal area of the individual vehicle of the road load matrix family, m 2 A fr is the frontal area of the representative vehicle of the road load matrix family, m 2 RR is the tyre rolling resistance of the individual vehicle of the road load matrix family, kg/tonne; RR r is the tyre rolling resistance of the representative vehicle of the road load matrix family, kg/tonne. (ao) point 5.1.2.1. is replaced by the following: '5.1.2.1.
```

### Retrieved: L_2017175EN.01000101 / chunk_159

Resolution: document_chunk_sqlite

```text
In the case that the convergence requirement is not met, pairs shall be removed from the analysis, starting with the pair giving the highest change in calculated road load, until the convergence requirement is met, as long as a minimum of 5 valid pairs are used for the final road load determination.
4.4. Measurement and calculation of running resistance using the torque meter method
As an alternative to the coastdown methods, the torque meter method may also be used in which the running resistance is determined by measuring wheel torque on the driven wheels at the reference speed points for time periods of at least 5 seconds.
4.4.1. Installation of torque meter
Wheel torque meters shall be installed between the wheel hub and the rim of each driven wheel, measuring the required torque to keep the vehicle at a constant speed.
The torque meter shall be calibrated on a regular basis, at least once a year, traceable to national or international standards, in order to meet the required accuracy and precision.
4.4.2. Procedure and data sampling
4.4.2.1. Selection of reference speeds for running resistance curve determination
Reference speed points for running resistance determination shall be selected according to paragraph 2.2. of this Sub-Annex.
The reference speeds shall be measured in descending order. At the request of the manufacturer, there may be stabilization periods between measurements but the stabilization speed shall not exceed the speed of the next reference speed.
4.4.2.2. Data collection
Data sets consisting of actual speed v ji actual torque C ji and time over a period of at least 5 seconds shall be measured for every v j at a sampling frequency of at least 10 Hz. The data sets collected over one time period for a reference speed v j shall be referred to as one measurement.
4.4.2.3. Vehicle torque meter measurement procedure
Prior to the torque meter method test measurement, a vehicle warm-up shall be performed according to paragraph 4.2.4. of this Sub-Annex.
During test measurement, steering wheel movement shall be avoided as much as possible, and the vehicle brakes shall not be operated.
The test shall be repeated until the running resistance data satisfy the measurement precision requirements as specified in paragraph 4.4.3.2. of this Sub-Annex.
Although it is recommended that each test run be performed without interruption, split runs may be performed if data cannot be collected in a single run for all the reference speed points. For split runs, care shall be taken so that vehicle conditions remain as stable as possible at each split point
4.4.2.4. Velocity deviation
During a measurement at a single reference speed point, the velocity deviation from the arithmetic average velocity, v ji -v jm , calculated according to paragraph 4.4.3. of this Sub-Annex, shall be within the values in Table A4/5.
Additionally, the arithmetic average velocity v jm at every reference speed point shall not deviate from the reference speed v j by more than ± 1 km/h or 2 per cent of the reference speed v j , whichever is greater.
Table A4/5
Velocity deviation
4.4.2.5. Atmospheric temperature
Tests shall be performed under the same temperature conditions as defined in paragraph 4.1.1.2. of this Sub-Annex.
4.4.3. Calculation of arithmetic average velocity and arithmetic average torque
4.4.3.1. Calculation process
Arithmetic average velocity v jm , in km/h, and arithmetic average torque C jm , in Nm, of each measurement shall be calculated from the data sets collected in paragraph 4.4.2.2. of this Sub-Annex using the following equations:
and
where:
v ji is the actual vehicle speed of the i th k is the number of data sets in a single measurement; C ji is the actual torque of the i th C js is the compensation term for speed drift, Nm, given by the following equation:
shall be no greater than 0,05 and may be disregarded if α j is not greater than ± 0,005 m/s 2 ;
m st is the test vehicle mass at the start of the measurements and shall be measured immediately before the warm-up procedure and no earlier, kg; mr is the equivalent effective mass of rotating components according to paragraph 2.5.1. of this Sub-Annex, kg; r j is the dynamic radius of the tyre determined at a reference point of 80 km/h or at the highest reference speed point of the vehicle if this speed is lower than 80 km/h, calculated according to the following equation:
where:
n is the rotational frequency of the driven tyre, s -1 α j is the arithmetic average acceleration, m/s 2 where: t i is the time at which the i th
4.4.3.2. Measurement precision
```

### Retrieved: L_2017175EN.01000101 / chunk_163

Resolution: document_chunk_sqlite

```text
5.2.1. As an alternative for determining road load with the coastdown or torque meter method, a calculation method for default road load may be used. For the calculation of a default road load based on vehicle parameters, several parameters such as test mass, width and height of the vehicle shall be used. The default road load F c 5.2.2. The default road load force shall be calculated using the following equation: where: F c is the calculated default road load force as a function of vehicle velocity, N; f 0 is the constant road load coefficient, N, defined by the following equation: f 1 is the first order road load coefficient and shall be set to zero; f 2 is the second order road load coefficient, N·(h/km) 2 v is vehicle velocity, km/h; TM test mass, kg; width vehicle width as defined in 6.2. of Standard ISO 612:1978, m; height vehicle height as defined in 6.3. of Standard ISO 612:1978, m.
1. Wind tunnel method
The wind tunnel method is a road load measurement method using a combination of a wind tunnel and a chassis dynamometer or of a wind tunnel and a flat belt dynamometer. The test benches may be separate facilities or integrated with one another.
6.1. Measurement method
6.1.1. The road load shall be determined by: (a) adding the road load forces measured in a wind tunnel and those measured using a flat belt dynamometer; or (b) adding the road load forces measured in a wind tunnel and those measured on a chassis dynamometer. 6.1.2. Aerodynamic drag shall be measured in the wind tunnel. 6.1.3. Rolling resistance and drivetrain losses shall be measured using a flat belt or a chassis dynamometer, measuring the front and rear axles simultaneously.
6.2. Approval of the facilities by the approval authority
The results of the wind tunnel method shall be compared to those obtained using the coastdown method to demonstrate qualification of the facilities and included in all relevant test reports.
6.2.1. Three vehicles shall be selected by the approval authority. The vehicles shall cover the range of vehicles (e.g. size, weight) planned to be measured with the facilities concerned.
6.2.2. Two separate coastdown tests shall be performed with each of the three vehicles according to paragraph 4.3. of this Sub-Annex, and the resulting road load coefficients, f 0 , f 1 and f 2 , shall be determined according to that paragraph and corrected according to paragraph 4.5.5. of this Sub-Annex. The coastdown test result of a test vehicle shall be the arithmetic average of the road load coefficients of its two separate coastdown tests. If more than two coastdown tests are necessary to fulfil the approval of facilities' criteria, all valid tests shall be averaged.
6.2.3. Measurement with the wind tunnel method according to paragraphs 6.3. to 6.7. inclusive of this Sub-Annex shall be performed on the same three vehicles as selected in paragraph 6.2.1. of this Sub-Annex and in the same conditions, and the resulting road load coefficients, f 0 , f 1 and f 2 , shall be determined.
If the manufacturer chooses to use one or more of the available alternative procedures within the wind tunnel method (i.e. paragraph 6.5.2.1. on preconditioning, paragraphs 6.5.2.2. and 6.5.2.3. on the procedure, and paragraph 6.5.2.3.3. on dynamometer setting), these procedures shall also be used also for the approval of the facilities.
6.2.4. Approval criteria
The facility or combination of facilities used shall be approved if both of the following two criteria are fulfilled:
(a) The difference in cycle energy, expressed as ε k where: ε k is the difference in cycle energy over a complete Class 3 WLTC for vehicle k between the wind tunnel method and the coastdown method, per cent; E k, WTM is the cycle energy over a complete Class 3 WLTC for vehicle k, calculated with the road load derived from the wind tunnel method (WTM) calculated according to paragraph 5 of Sub-Annex 7, J; E k, coastdown is the cycle energy over a complete Class 3 WLTC for vehicle k, calculated with the road load derived from the coastdown method calculated according to paragraph 5. of Sub-Annex 7, J.; and (b) The arithmetic average The facility may be used for road load determination for a maximum of two years after the approval has been granted.
```

### Retrieved table: L_2017175EN.01000101 / table_121

```json
{
  "document_id": "L_2017175EN.01000101",
  "table_id": "table_121",
  "row_ids": [
    2
  ],
  "headers": null,
  "rows": [
    [
      "SUBJECT",
      "Determination of a vehicle road load",
      "Determination of a vehicle road load",
      "Determination of a vehicle road load"
    ]
  ]
}
```

### Retrieved table: L_2017175EN.01000101 / table_49

```json
{
  "document_id": "L_2017175EN.01000101",
  "table_id": "table_49",
  "row_ids": [
    2
  ],
  "headers": null,
  "rows": [
    [
      "SUBJECT",
      "Determination of a vehicle road load",
      "Determination of a vehicle road load",
      "Determination of a vehicle road load"
    ]
  ]
}
```

### Retrieved table: L_2023066EN.01000101 / table_120

```json
{
  "document_id": "L_2023066EN.01000101",
  "table_id": "table_120",
  "row_ids": [
    2
  ],
  "headers": null,
  "rows": [
    [
      "SUBJECT",
      "Determination of a vehicle road load /…",
      "Determination of a vehicle road load /…",
      "Determination of a vehicle road load /…"
    ]
  ]
}
```

### Retrieved table: L_2018301EN.01000101 / table_153

```json
{
  "document_id": "L_2018301EN.01000101",
  "table_id": "table_153",
  "row_ids": [
    2
  ],
  "headers": null,
  "rows": [
    [
      "SUBJECT",
      "Determination of a vehicle road load /…",
      "Determination of a vehicle road load /…",
      "Determination of a vehicle road load /…"
    ]
  ]
}
```

### Retrieved table: L_2019058EN.01000101 / table_38

```json
{
  "document_id": "L_2019058EN.01000101",
  "table_id": "table_38",
  "row_ids": [
    0
  ],
  "headers": [
    "Measurement system",
    "Accuracy",
    "Rise time ( 1 )"
  ],
  "rows": [
    [
      "Balance for vehicle weight",
      "50 kg or < 0,5 % of max. calibration whichever is smaller",
      "—"
    ]
  ]
}
```

## global_natural_018

For the 2021–2025 allocation table, what annual and total allocation quantities are recorded for Audi Brussels?

Draft reference: The supplied Audi Brussels row records 3,076 for each year 2021–2025, totalling 15,380. A later revision for the same period may differ: identify document/version, not just years.

Retrieval execution status: success (NOT relevance)

### Retrieved: L_2021231EN.01000101 / chunk_9

Resolution: document_chunk_sqlite

```text
Where the update of an integrated national energy and climate plan pursuant to Article 14 of Regulation (EU) 2018/1999 necessitates a revision of a territorial just transition plan, that revision shall be carried out as part of the mid-term review in accordance with Article 18 of Regulation (EU) 2021/1060.
1. Where Member States intend to make use of the possibility to receive support under the other pillars of the Just Transition Mechanism, their territorial just transition plans shall set out the sectors and thematic areas envisaged to be supported under those pillars.
Article 12
Indicators
1. Common output and result indicators, as set out in Annex III and, where duly justified in the territorial just transition plan, programme-specific output and result indicators shall be used in accordance with point (a) of the second subparagraph of Article 16(1), point (d)(ii) of Article 22(3) and point (b) of Article 42(2) of Regulation (EU) 2021/1060.
2. For output indicators, baselines shall be set at zero. The milestones set for 2024 and targets set for 2029 shall be cumulative. Targets shall not be revised after the request for programme amendment, submitted pursuant to Article 18(3) of Regulation (EU) 2021/1060, has been approved by the Commission.
3. Where a JTF priority supports the activities referred to in points (k), (l) or (m) of Article 8(2), data on the indicators for participants shall only be transmitted where all the data relating to that participant, required in accordance with Annex III, are available.
Article 13
Financial corrections
Based on the examination of the final performance report of the programme, the Commission may make financial corrections in accordance with Article 104 of Regulation (EU) 2021/1060 where less than 65 % of the target set out for one or more output indicators is achieved.
Financial corrections shall be in proportion to the achievements and shall not be applied where the failure to achieve targets is due to the impact of socio-economic or environmental factors, significant changes in the economic or environmental conditions in the Member State concerned or because of reasons of force majeure seriously affecting implementation of the priorities concerned.
Article 14
Review
By 30 June 2025, the Commission shall review the implementation of the JTF with regard to the specific objective set out in Article 2, taking into account possible changes in Regulation (EU) 2020/852 and the Union's climate objectives set out in a Regulation of the European Parliament and of the Council establishing the framework for achieving climate neutrality and amending Regulations (EC) No 401/2009 and (EU) 2018/1999 ('European Climate Law'), and the evolution in the implementation of the Sustainable Europe Investment Plan. On that basis, the Commission shall submit a report to the European Parliament and to the Council, which may be accompanied by legislative proposals.
Article 15
Entry into force
This Regulation shall enter into force on the day following that of its publication in the Official Journal of the European Union .
This Regulation shall be binding in its entirety and directly applicable in all Member States.
Done at Brussels, 24 June 2021.
For the European Parliament
The President
D. M. SASSOLI
For the Council
The President
A. P. ZACARIAS
[( 1 )](#ntc1-L_2021231EN.01000101-E0001)
[OJ C 290, 1.9.2020, p. 1](http://publications.europa.eu/resource/oj/JOC_2020_290_R_TOC)
.
[( 2 )](#ntc2-L_2021231EN.01000101-E0002)
[OJ C 311, 18.9.2020, p. 55](http://publications.europa.eu/resource/oj/JOC_2020_311_R_TOC)
and
[OJ C 429, 11.12.2020, p. 240](http://publications.europa.eu/resource/oj/JOC_2020_429_R_TOC)
.
```

### Retrieved: LI2020433EN.01002301 / chunk_4

Resolution: document_chunk_sqlite

```text
1. For the purpose of Article 21(5) of the Financial Regulation, EUR 384 400 million in 2018 prices, of the amount referred to in Article 2(1) of this Regulation, shall constitute external assigned revenue to the Union programmes referred to in point (a) of Article 2(2) of this Regulation and EUR 5 600 million in 2018 prices of that amount shall constitute external assigned revenue to the Union programmes referred to in point (c) of Article 2(2) of this Regulation.
2. EUR 360 000 million in 2018 prices, of the amount referred to in Article 2(1), shall be used for loans to Member States under the Union programmes referred to in point (b) of Article 2(2).
3. Commitment appropriations covering support to the Union programmes referred to in points (a) and (c) of Article 2(2) shall be made available automatically up to the respective amounts referred to in those points as of the date of entry into force of the Own Resources Decision which provides for the empowerment referred to in Article 2(1) of this Regulation.
4. Legal commitments giving rise to expenditure for support as referred to in point (a) of Article 2(2), and, where appropriate, in point (c) of Article 2(2), shall be entered into by the Commission or by its executive agencies by 31 December 2023. Legal commitments of at least 60 % of the amount referred to in point (a) of Article 2(2) shall be entered into by 31 December 2022.
5. Decisions on the granting of the loans referred to in point (b) of Article 2(2) shall be adopted by 31 December 2023.
6. The Union's budgetary guarantees up to an amount which, in accordance with the relevant provisioning rate set out in the respective basic acts, corresponds to the provisioning for budgetary guarantees referred to in point (c) of Article 2(2), depending on the risk profiles of the supported financing and investment operations, shall be granted only for supporting operations which have been approved by the counterparts by 31 December 2023. The respective budgetary guarantee agreements shall contain provisions requiring that financial operations corresponding to at least 60 % of the amount of those budgetary guarantees are approved by the counterparts by 31 December 2022. Where provisioning for budgetary guarantees is used for non-repayable support related to the financing and investment operations referred to in point (c) of Article 2(2), the related legal commitments shall be entered into by the Commission by 31 December 2023.
7. Paragraphs 4 to 6 of this Article shall not apply to technical and administrative assistance referred to in Article 1(3).
8. Costs from technical and administrative assistance for the implementation of the Instrument, such as preparatory, monitoring, control, audit and evaluation activities including corporate information technology systems for the purposes of this Regulation, shall be financed from the Union budget.
9. Payments related to the legal commitments entered into, decisions adopted and the provisions regarding financial operations approved in accordance with paragraphs 4 to 6 of this Article shall be made by 31 December 2026, with the exception of technical and administrative assistance referred to in Article 1(3) and of cases where, exceptionally, although the legal commitment has been entered into, the decision has been adopted or the operation has been approved, on terms compliant with the deadline applicable under this paragraph, payments after 2026 are necessary for the Union to be able to honour its obligations towards third parties, including as a result of a definitive judgment against the Union.
Article 4
Reporting
By 31 October 2022, the Commission shall submit to the Council a report on the progress achieved in the implementation of the Instrument and the use of the funds allocated in accordance with Article 2(2).
Article 5
Applicability
1. This Regulation shall not be applicable to or in the United Kingdom.
2. References to 'Member States' in this Regulation shall not be understood to include the United Kingdom.
Article 6
Entry into force
This Regulation shall enter into force on the day following that of its publication in the Official Journal of the European Union .
This Regulation shall be binding in its entirety and directly applicable in all Member States.
Done at Brussels, 14 December 2020.
For the Council
The President
M. ROTH
```

### Retrieved: 31990Y1231_02_en / chunk_8

Resolution: document_chunk_sqlite

```text
The situation is still more striking as regards payment appropriations: between 1984 and 1989 annual payments made amounted on average to 5 % of the total allocation each year while in the first half of 1990 alone 15 % of the total payment appropriations were used. Programme (b) is a special case: in view of the difficulties experienced in implementing the psychiatric reform (see 5.15 5.19 below), the Commission stopped approving new projects in 1989 so the new commitment appropriations available were not used. Considerable delays were also detected in a number of projects approved by the Commission between 1984 and 1988. Those projects, on which work had still not begun by 1 December 1990, were cancelled and the corresponding commitment appropriations will be released. III. The programmes 3.1. The programmes have been improved considerably thanks to technical assistance from the Commission. The report of 29 March 1984 on 'Psychiatric reform in Greece
```
```

### Retrieved: C_202406955EN / chunk_4

Resolution: document_chunk_sqlite

```text
[( 3 )](#ntc3-C_202406955EN.000101-E0003)
Commission Implementing Regulation (EU) 2019/1842 of 31 October 2019 laying down rules for the application of Directive 2003/87/EC of the European Parliament and of the Council as regards further arrangements for the adjustments to free allocation of emission allowances due to activity level changes (
[OJ L 282, 4.11.2019, p. 20](http://publications.europa.eu/resource/oj/JOL_2019_282_R_TOC)
, ELI:
[http://data.europa.eu/eli/reg](http://data.europa.eu/eli/reg_impl/2019/1842/oj)
[_](http://data.europa.eu/eli/reg_impl/2019/1842/oj)
[impl/2019/1842/oj](http://data.europa.eu/eli/reg_impl/2019/1842/oj)
).
[( 4 )](#ntc4-C_202406955EN.000101-E0004)
Commission Decision of 29 June 2021 instructing the Central Administrator of the European Union Transaction Log to enter the national allocation tables of Belgium, Bulgaria, Czechia, Denmark, Germany, Estonia, Ireland, Greece, Spain, France, Croatia, Italy, Cyprus, Latvia, Lithuania, Luxembourg, Hungary, Netherlands, Austria, Poland, Portugal, Romania, Slovenia, Slovakia, Finland and Sweden into the European Union Transaction Log (
[OJ C 302, 28.7.2021, p. 1](http://publications.europa.eu/resource/oj/JOC_2021_302_R_TOC)
).
ANNEX I
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: Belgium
ANNEX II
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: Czechia
ANNEX III
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: Denmark
ANNEX IV
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: Germany
ANNEX V
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: Estonia
ANNEX VI
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: Ireland
ANNEX VII
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: Greece
ANNEX VIII
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: Spain
ANNEX IX
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: France
ANNEX X
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: Croatia
ANNEX XI
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: Cyprus
ANNEX XII
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: Latvia
ANNEX XIII
```

### Retrieved: C_202505531EN / chunk_4

Resolution: document_chunk_sqlite

```text
[( 3 )](#ntc3-C_202505531EN.000101-E0003)
Commission Implementing Regulation (EU) 2019/1842 of 31 October 2019 laying down rules for the application of Directive 2003/87/EC of the European Parliament and of the Council as regards further arrangements for the adjustments to free allocation of emission allowances due to activity level changes (
[OJ L 282, 4.11.2019, p. 20](http://publications.europa.eu/resource/oj/JOL_2019_282_R_TOC)
, ELI:
[http://data.europa.eu/eli/reg](http://data.europa.eu/eli/reg_impl/2019/1842/oj)
[_](http://data.europa.eu/eli/reg_impl/2019/1842/oj)
[impl/2019/1842/oj](http://data.europa.eu/eli/reg_impl/2019/1842/oj)
).
[( 4 )](#ntc4-C_202505531EN.000101-E0004)
Commission Decision 2021/C 302/01 of 29 June 2021 instructing the Central Administrator of the European Union Transaction Log to enter the national allocation tables of Belgium, Bulgaria, Czechia, Denmark, Germany, Estonia, Ireland, Greece, Spain, France, Croatia, Italy, Cyprus, Latvia, Lithuania, Luxembourg, Hungary, Netherlands, Austria, Poland, Portugal, Romania, Slovenia, Slovakia, Finland and Sweden into the European Union Transaction Log (
[OJ C 302, 28.7.2021, p. 1](http://publications.europa.eu/resource/oj/JOC_2021_302_R_TOC)
).
ANNEX I
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: Belgium
ANNEX II
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: Bulgaria
ANNEX III
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: Czechia
ANNEX IV
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: Denmark
ANNEX V
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: Germany
ANNEX VI
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: Estonia
ANNEX VII
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: Spain
ANNEX VIII
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: France
ANNEX IX
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: Croatia
ANNEX X
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: Italy
ANNEX XI
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: Lithuania
ANNEX XII
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: Luxembourg
ANNEX XIII
```

### Retrieved: C_2023340EN.01000701 / chunk_3

Resolution: document_chunk_sqlite

```text
[( 3 )](#ntc3-C_2023340EN.01000701-E0003)
Commission Decision (EU) 2021/355 of 25 February 2021 concerning national implementation measures for the transitional free allocation of greenhouse gas emission allowances in accordance with Article 11(3) of Directive 2003/87/EC of the European Parliament and of the Council (
[OJ L 68, 26.2.2021, p. 221](http://publications.europa.eu/resource/oj/JOL_2021_068_R_TOC)
).
[( 4 )](#ntc4-C_2023340EN.01000701-E0004)
Commission Implementing Regulation (EU) 2021/447 of 12 March 2021 determining revised benchmark values for free allocation of emission allowances for the period from 2021 to 2025 pursuant to Article 10a(2) of Directive 2003/87/EC of the European Parliament and of the Council (
[OJ L 87, 15.3.2021, p. 29](http://publications.europa.eu/resource/oj/JOL_2021_087_R_TOC)
).
[( 5 )](#ntc5-C_2023340EN.01000701-E0005)
Commission Delegated Regulation (EU) 2019/331 of 19 December 2018 determining transitional Union-wide rules for harmonised free allocation of emission allowances pursuant to Article 10a of Directive 2003/87/EC of the European Parliament and of the Council (
[OJ L 59, 27.2.2019, p. 8](http://publications.europa.eu/resource/oj/JOL_2019_059_R_TOC)
).
[( 6 )](#ntc6-C_2023340EN.01000701-E0006)
Commission Implementing Decision (EU) 2021/927 of 31 May 2021 determining the uniform cross-sectoral correction factor for the adjustment of free allocations of emission allowances for the period 2021 to 2025 (
[OJ L 203, 9.6.2021, p. 14](http://publications.europa.eu/resource/oj/JOL_2021_203_R_TOC)
).
ANNEX I
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: Belgium
ANNEX II
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: Czechia
ANNEX III
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: Denmark
ANNEX IV
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: Germany
ANNEX V
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: Spain
ANNEX VI
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: France
ANNEX VII
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: Croatia
ANNEX VIII
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: Italy
ANNEX IX
```

### Retrieved: C_202506247EN / chunk_4

Resolution: document_chunk_sqlite

```text
[( 3 )](#ntc3-C_202506247EN.000101-E0003)
Commission Implementing Regulation (EU) 2019/1842 of 31 October 2019 laying down rules for the application of Directive 2003/87/EC of the European Parliament and of the Council as regards further arrangements for the adjustments to free allocation of emission allowances due to activity level changes (
[OJ L 282, 4.11.2019, p. 20](http://publications.europa.eu/resource/oj/JOL_2019_282_R_TOC)
, ELI:
[http://data.europa.eu/eli/reg](http://data.europa.eu/eli/reg_impl/2019/1842/oj)
[_](http://data.europa.eu/eli/reg_impl/2019/1842/oj)
[impl/2019/1842/oj](http://data.europa.eu/eli/reg_impl/2019/1842/oj)
).
[( 4 )](#ntc4-C_202506247EN.000101-E0004)
Commission Decision 2021/C 302/01 of 29 June 2021 instructing the Central Administrator of the European Union Transaction Log to enter the national allocation tables of Belgium, Bulgaria, Czechia, Denmark, Germany, Estonia, Ireland, Greece, Spain, France, Croatia, Italy, Cyprus, Latvia, Lithuania, Luxembourg, Hungary, Netherlands, Austria, Poland, Portugal, Romania, Slovenia, Slovakia, Finland and Sweden into the European Union Transaction Log (
[OJ C 302, 28.7.2021, p. 1](http://publications.europa.eu/resource/oj/JOC_2021_302_R_TOC)
).
ANNEX I
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: Belgium
ANNEX II
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: Bulgaria
ANNEX III
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: Czechia
ANNEX IV
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: Denmark
ANNEX V
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: Germany
ANNEX VI
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: Ireland
ANNEX VII
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: Greece
ANNEX VIII
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: Spain
ANNEX IX
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: France
ANNEX X
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: Italy
ANNEX XI
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: Latvia
ANNEX XII
National allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC
Member State: Hungary
ANNEX XIII
```

### Retrieved: L_2012112EN.01000601 / chunk_74

Resolution: document_chunk_sqlite

```text
In the rural development legislative framework for the 2014-2020 programming period, as regards Croatia, special support to facilitate the setting up and administrative operation of producer groups shall be granted, pursuant to the principles laid down in Article 35 of Council Regulation (EC) No 1698/2005, to producer groups which are officially recognised by Croatia's competent authority by 31 December 2017, provided that no similar general measures and/or support is foreseen in the new rural development regulation for the 2014-2020 programming period.
C. Leader
In the rural development legislative framework for the 2014-2020 programming period, as regards Croatia, the minimum EAFRD contribution to the rural development programme for Leader shall be set on average at a level which is at least half of the percentage of the budget that shall be applicable to the other Member States, if such a requirement is set.
D. Complements to direct payments
1. Support may be granted to farmers eligible for complementary national direct payments or aid under Article 132 of Council Regulation (EC) No 73/2009. 2. The support granted to a farmer in respect of the years 2014, 2015 and 2016 shall not exceed the difference between: (a) the level of direct payments applicable in Croatia for the year concerned in accordance with Article 121 of Council Regulation (EC) No 73/2009; and (b) 45 % of the level of direct payments applicable in the Union as constituted on 30 April 2004 in the relevant year. 3. The Union contribution to support granted under this subsection D in Croatia in respect of the years 2014, 2015 and 2016 shall not exceed 20 % of its respective total annual EAFRD allocation. 4. The Union contribution rate for the complements to direct payments shall not exceed 80 %.
E. Instrument for pre-accession assistance - Rural development
1. Croatia may continue to contract or enter into commitments under the IPARD programme under Commission Regulation (EC) No 718/2007 of 12 June 2007 implementing Council Regulation (EC) No 1085/2006 establishing an instrument for pre-accession assistance (IPA) ( 1 2. The Commission shall adopt the necessary measures to this end in accordance with the procedure referred to in Article 5 of European Parliament and Council Regulation (EU) No 182/2011. To that effect, the Commission shall be assisted by the IPA Committee referred to in Article 14(1) of Council Regulation (EC) No 1085/2006.
F. IPARD ex post evaluation
In the rural development legislative framework for the 2014-2020 programming period, as regards the implementation of the IPARD programme for Croatia, expenditure relating to the ex post evaluation of the IPARD programme provided for in Article 191 of Commission Regulation (EC) No 718/2007 may be eligible under technical assistance.
G. Modernisation of agricultural holdings
In the rural development legislative framework for the 2014-2020 programming period, as regards Croatia, the maximum intensity of an aid for the modernisation of agricultural holdings shall be 75 % of the amount of eligible investment for the implementation of Council Directive 91/676/EEC of 12 December 1991 concerning the protection of waters against pollution caused by nitrates from agricultural sources
[( 2 )](#ntr2-L_2012112EN.01008701-E0002)
, within a maximum period of four years from the date of accession pursuant to Articles 3(2) and 5(1) of that Directive.
H. Respect of standards
In the rural development legislative framework for the 2014-2020 programming period, as regards Croatia, the statutory management requirements referred to in Annex II to Council Regulation (EC) No 73/2009 applicable in that programming period shall be respected in accordance with the following timetable: requirements referred to in Point A of Annex II shall apply from 1 January 2014; requirements referred to in Point B of Annex II shall apply from 1 January 2016; and requirements referred to in Point C of Annex II shall apply from 1 January 2018.
```

### Expected table: C_2022160EN.01002701 / table_1

```json
{
  "document_id": "C_2022160EN.01002701",
  "table_id": "table_1",
  "row_ids": [
    0
  ],
  "headers": [
    "Installation ID",
    "Installation ID (Union registry)",
    "Installation name",
    "Operator name",
    "Quantity to be allocated | 2021",
    "Quantity to be allocated | 2022",
    "Quantity to be allocated | 2023",
    "Quantity to be allocated | 2024",
    "Quantity to be allocated | 2025",
    "Quantity to be allocated by installation"
  ],
  "rows": [
    [
      "BE000000000000158",
      "158",
      "Audi Brussels NV",
      "Audi Brussels",
      "3 076",
      "3 076",
      "3 076",
      "3 076",
      "3 076",
      "15 380"
    ]
  ]
}
```

### Retrieved table: L_2013259EN.01000101 / table_1

```json
{
  "document_id": "L_2013259EN.01000101",
  "table_id": "table_1",
  "row_ids": [
    0
  ],
  "headers": [
    "",
    "2013",
    "2014",
    "2015",
    "2016",
    "2017",
    "2018"
  ],
  "rows": [
    [
      "Allocation coefficient per year:",
      "0,0000 %",
      "10,7875 %",
      "25,8831 %",
      "76,6830 %",
      "100,0000 %",
      "100,0000 %"
    ]
  ]
}
```

### Retrieved table: L_2012232EN.01000301 / table_1

```json
{
  "document_id": "L_2012232EN.01000301",
  "table_id": "table_1",
  "row_ids": [
    0
  ],
  "headers": [
    "",
    "2012",
    "2013",
    "2014",
    "2015",
    "2016",
    "2017"
  ],
  "rows": [
    [
      "Allocation coefficient per year:",
      "87,52 %",
      "45,01 %",
      "100 %",
      "100 %",
      "100 %",
      "100 %"
    ]
  ]
}
```

### Retrieved table: L_2013259EN.01000101 / table_1

```json
{
  "document_id": "L_2013259EN.01000101",
  "table_id": "table_1",
  "row_ids": [
    1
  ],
  "headers": [
    "",
    "2013",
    "2014",
    "2015",
    "2016",
    "2017",
    "2018"
  ],
  "rows": [
    [
      "Total amount allocated per Member State (in EUR):",
      "",
      "",
      "",
      "",
      "",
      ""
    ]
  ]
}
```

### Retrieved table: L_2013280EN.01000301 / table_1

```json
{
  "document_id": "L_2013280EN.01000301",
  "table_id": "table_1",
  "row_ids": [
    0
  ],
  "headers": [
    "",
    "2013",
    "2014",
    "2015",
    "2016",
    "2017",
    "From 2018"
  ],
  "rows": [
    [
      "Total units per year (global quota per year, caps per subheading)",
      "2 250 000",
      "10 157 500",
      "11 315 000",
      "12 472 500",
      "13 630 000",
      "14 787 500"
    ]
  ]
}
```

### Retrieved table: L_2013259EN.01000101 / table_1

```json
{
  "document_id": "L_2013259EN.01000101",
  "table_id": "table_1",
  "row_ids": [
    6
  ],
  "headers": [
    "",
    "2013",
    "2014",
    "2015",
    "2016",
    "2017",
    "2018"
  ],
  "rows": [
    [
      "Total amount allocated to the Member States referred to in points (a) to (d) (in EUR)",
      "0",
      "1 342 478",
      "3 858 439",
      "6 559 570",
      "8 359 247",
      "3 904 420"
    ]
  ]
}
```

## global_natural_019

For the 2021–2025 allocation table, what amounts are recorded for the Lakeland Dairies Killeshandra Site?

Draft reference: The supplied Lakeland Killeshandra row records 4,334 for each year 2021–2025, totalling 21,670. Confirm document/version and any later allocation revisions.

Retrieval execution status: success (NOT relevance)

### Retrieved: LI2020433EN.01002301 / chunk_4

Resolution: document_chunk_sqlite

```text
1. For the purpose of Article 21(5) of the Financial Regulation, EUR 384 400 million in 2018 prices, of the amount referred to in Article 2(1) of this Regulation, shall constitute external assigned revenue to the Union programmes referred to in point (a) of Article 2(2) of this Regulation and EUR 5 600 million in 2018 prices of that amount shall constitute external assigned revenue to the Union programmes referred to in point (c) of Article 2(2) of this Regulation.
2. EUR 360 000 million in 2018 prices, of the amount referred to in Article 2(1), shall be used for loans to Member States under the Union programmes referred to in point (b) of Article 2(2).
3. Commitment appropriations covering support to the Union programmes referred to in points (a) and (c) of Article 2(2) shall be made available automatically up to the respective amounts referred to in those points as of the date of entry into force of the Own Resources Decision which provides for the empowerment referred to in Article 2(1) of this Regulation.
4. Legal commitments giving rise to expenditure for support as referred to in point (a) of Article 2(2), and, where appropriate, in point (c) of Article 2(2), shall be entered into by the Commission or by its executive agencies by 31 December 2023. Legal commitments of at least 60 % of the amount referred to in point (a) of Article 2(2) shall be entered into by 31 December 2022.
5. Decisions on the granting of the loans referred to in point (b) of Article 2(2) shall be adopted by 31 December 2023.
6. The Union's budgetary guarantees up to an amount which, in accordance with the relevant provisioning rate set out in the respective basic acts, corresponds to the provisioning for budgetary guarantees referred to in point (c) of Article 2(2), depending on the risk profiles of the supported financing and investment operations, shall be granted only for supporting operations which have been approved by the counterparts by 31 December 2023. The respective budgetary guarantee agreements shall contain provisions requiring that financial operations corresponding to at least 60 % of the amount of those budgetary guarantees are approved by the counterparts by 31 December 2022. Where provisioning for budgetary guarantees is used for non-repayable support related to the financing and investment operations referred to in point (c) of Article 2(2), the related legal commitments shall be entered into by the Commission by 31 December 2023.
7. Paragraphs 4 to 6 of this Article shall not apply to technical and administrative assistance referred to in Article 1(3).
8. Costs from technical and administrative assistance for the implementation of the Instrument, such as preparatory, monitoring, control, audit and evaluation activities including corporate information technology systems for the purposes of this Regulation, shall be financed from the Union budget.
9. Payments related to the legal commitments entered into, decisions adopted and the provisions regarding financial operations approved in accordance with paragraphs 4 to 6 of this Article shall be made by 31 December 2026, with the exception of technical and administrative assistance referred to in Article 1(3) and of cases where, exceptionally, although the legal commitment has been entered into, the decision has been adopted or the operation has been approved, on terms compliant with the deadline applicable under this paragraph, payments after 2026 are necessary for the Union to be able to honour its obligations towards third parties, including as a result of a definitive judgment against the Union.
Article 4
Reporting
By 31 October 2022, the Commission shall submit to the Council a report on the progress achieved in the implementation of the Instrument and the use of the funds allocated in accordance with Article 2(2).
Article 5
Applicability
1. This Regulation shall not be applicable to or in the United Kingdom.
2. References to 'Member States' in this Regulation shall not be understood to include the United Kingdom.
Article 6
Entry into force
This Regulation shall enter into force on the day following that of its publication in the Official Journal of the European Union .
This Regulation shall be binding in its entirety and directly applicable in all Member States.
Done at Brussels, 14 December 2020.
For the Council
The President
M. ROTH
```

### Retrieved: L_2021231EN.01000101 / chunk_9

Resolution: document_chunk_sqlite

```text
Where the update of an integrated national energy and climate plan pursuant to Article 14 of Regulation (EU) 2018/1999 necessitates a revision of a territorial just transition plan, that revision shall be carried out as part of the mid-term review in accordance with Article 18 of Regulation (EU) 2021/1060.
1. Where Member States intend to make use of the possibility to receive support under the other pillars of the Just Transition Mechanism, their territorial just transition plans shall set out the sectors and thematic areas envisaged to be supported under those pillars.
Article 12
Indicators
1. Common output and result indicators, as set out in Annex III and, where duly justified in the territorial just transition plan, programme-specific output and result indicators shall be used in accordance with point (a) of the second subparagraph of Article 16(1), point (d)(ii) of Article 22(3) and point (b) of Article 42(2) of Regulation (EU) 2021/1060.
2. For output indicators, baselines shall be set at zero. The milestones set for 2024 and targets set for 2029 shall be cumulative. Targets shall not be revised after the request for programme amendment, submitted pursuant to Article 18(3) of Regulation (EU) 2021/1060, has been approved by the Commission.
3. Where a JTF priority supports the activities referred to in points (k), (l) or (m) of Article 8(2), data on the indicators for participants shall only be transmitted where all the data relating to that participant, required in accordance with Annex III, are available.
Article 13
Financial corrections
Based on the examination of the final performance report of the programme, the Commission may make financial corrections in accordance with Article 104 of Regulation (EU) 2021/1060 where less than 65 % of the target set out for one or more output indicators is achieved.
Financial corrections shall be in proportion to the achievements and shall not be applied where the failure to achieve targets is due to the impact of socio-economic or environmental factors, significant changes in the economic or environmental conditions in the Member State concerned or because of reasons of force majeure seriously affecting implementation of the priorities concerned.
Article 14
Review
By 30 June 2025, the Commission shall review the implementation of the JTF with regard to the specific objective set out in Article 2, taking into account possible changes in Regulation (EU) 2020/852 and the Union's climate objectives set out in a Regulation of the European Parliament and of the Council establishing the framework for achieving climate neutrality and amending Regulations (EC) No 401/2009 and (EU) 2018/1999 ('European Climate Law'), and the evolution in the implementation of the Sustainable Europe Investment Plan. On that basis, the Commission shall submit a report to the European Parliament and to the Council, which may be accompanied by legislative proposals.
Article 15
Entry into force
This Regulation shall enter into force on the day following that of its publication in the Official Journal of the European Union .
This Regulation shall be binding in its entirety and directly applicable in all Member States.
Done at Brussels, 24 June 2021.
For the European Parliament
The President
D. M. SASSOLI
For the Council
The President
A. P. ZACARIAS
[( 1 )](#ntc1-L_2021231EN.01000101-E0001)
[OJ C 290, 1.9.2020, p. 1](http://publications.europa.eu/resource/oj/JOC_2020_290_R_TOC)
.
[( 2 )](#ntc2-L_2021231EN.01000101-E0002)
[OJ C 311, 18.9.2020, p. 55](http://publications.europa.eu/resource/oj/JOC_2020_311_R_TOC)
and
[OJ C 429, 11.12.2020, p. 240](http://publications.europa.eu/resource/oj/JOC_2020_429_R_TOC)
.
```

### Retrieved: 31999D0485en / chunk_12

Resolution: document_chunk_sqlite

```text
Table 6 takes as its basis the amount of capacity offered and the volume of cargo carried by the EATA parties eastbound and westbound in 1989. In order to make a comparison with subsequent years each base figure has been converted into 100. Table 6 Increase in capacity measured against increase in demand 1989 to 1992 >TABLE> (95) Table 6 demonstates that over the four years 1989 to 1992 taken as a whole capacity eastbound increased at the same rate as demand and that capacity westbound has also grown as a similar rate to the growth of demand. Accordingly it may be deduced from Table 6 that the argument of the EATA parties that eastbound capacity had grown in excess of eastbound demand is not substantiated. (96) The Commission understands that demand on the eastbound leg was well in advance of expectations for the fourth quarter of 1993 and that as a result the capacity non-utilisation programme of the EATA was "temporarily" suspended (see recital 27), never to be reintroduced. The assertions of the EATA parties as to the structural nature of the alleged overcapacity on eastbound northern Europe to the Far East services (see recital 24) were accordingly unsubstantiated. In any event, the relevance of these assertions is considered further at recital 227. (97) Moreover, the assertion that the overcapacity at that time was structural in nature is contradicted by the arguments put forward by the parties in the application for individual exemption. To show that any such overcapacity is structural in nature, the parties would have to demonstrate that it could never in its lifetime be efficiently used. However, the EATA parties argued precisely the opposite: "Even allowing for the present degree of overcapacity ... capacity will have to grow substantially over a 10-year period." "Taking a 10 year view, the maritime transport industry will have to meet substantial demands for additional capacity, as well as a certain level of replacement, at high new-building prices(38)." (98) In the light of these comments, which the Commission has no reason to doubt, it is considered that the parties assertions that there existed a structural problem of overcapacity on the northern Europe/Far East trades have not been demonstrated to be well-founded. (99) Finally, according to Drewry, the supply/demand balance on the north Europe/Far East trades looked as follows in the period 1992 to 1997. Table 7 North Europe/Far East supply/demand balance 1992 to 1995 >TABLE> (100) The figures given for demand in Table 7 exclude military traffic and relay/transshipment cargo moved via main trade ports as well as empty containers. They therefore underestimate actual vessel utilisation. The figures given for capacity are calculated after deduction of EATA cap in 1993 and 20 % slot reduction due to deadweight limitations. (101) Table 7 demonstrates not only continuous eastbound and westbound growth in demand but also demonstrates, as further illustrated in Table 8, that during the period in which the EATA was in operation, the increase in supply easily outstripped demand. Accordingly, in so far as there were any problems of overcapacity, it may be deduced that these would have been caused by the introduction of new capacity and not the existence of overcapacity at the time of implementation of the EATA. Table 8 North Europe/Far East supply/demand balance Eastbound 1992 to 1997 (million TEUs) >PIC FILE= "L
_
```

### Retrieved: L_2007095EN.01004101 / chunk_5

Resolution: document_chunk_sqlite

```text
Records of bacteriology shall be kept on all samples processed in a format in accordance with or comparable to the example given in Table 3.
All strains isolated shall be stored at the NRLs of the two Member States as long as it ensures integrity of the strains for a minimum of five years.
All samples of meat juice for serology shall be stored frozen for two years.
Table 3
Example of records to be taken on all processed samples
1. Reporting from Bulgaria and Romania
The competent authority responsible for the preparation of the yearly national report on the monitoring of Salmonella in animals pursuant to Article 9 of Directive 2003/99/EC shall collect and evaluate the results and report to the Commission.
Those reports shall include at least the following information:
6.1. Overall description on the implementation of the survey programme
- description of the population under study stratified according to slaughterhouses capacity, - description of randomization procedure, including notification system, - sample size calculated, - details of authorities and laboratories involved in sampling/testing/typing, - overall results of the study (samples analyzed by bacteriology, number of positive, serovar, phage type and antibiotic resistance testing).
6.2. Complete data on each animal sampled and corresponding tests results
The Member States shall submit the results of the survey in the form of raw data using a data dictionary and data collection forms provided by the Commission.
That dictionary and forms shall be established by the Commission and include at least the following:
- reference of the slaughterhouse, - capacity of the slaughterhouse, - date and time of sampling, - reference of the samples (the number), - type of samples taken: lymph nodes, - date of dispatch to the laboratory.
The following information shall be collected in the Member States for each sample sent to the laboratory:
- ID of the laboratory (in case several laboratories are involved), - means of transport of samples, - date of reception by the laboratory, - when testing lymph nodes, weight of the specimen, - results for the individual samples tested: 'negative' or in case positive for Salmonella Salmonella - results for strains subject to antimicrobial susceptibility testing and/or phagetyping results.
[( 1 )](#ntc1-L_2007095EN.01004401-E0001)
This number must represent at least 80 % of slaughtered fattening pigs in a Member State.
[( 2 )](#ntc2-L_2007095EN.01004401-E0002)
The 5th carcass to be processed on the 19th day of that month should be sampled for the survey.
ANNEX II
Maximum Community financial contribution to Bulgaria and Romania
ANNEX III
Certified financial report on the implementation of a baseline survey on the prevalence of Salmonella spp. in herds of slaughter pigs
Reporting period: 1 April 2007 to 30 September 2007
Statement on costs incurred on the survey and eligible for Community financial contribution
Reference number of Commission Decision providing Community financial contribution: ...
...
Declaration by the beneficiary
We certify that
- the costs set out in the statement on costs are genuine and have been incurred in carrying out the tasks laid down in Commission Decision 2007/219/EC and were essential for the proper performance of those tasks; - all supporting documents for those costs are available for audit purposes.
Date: ...
Person financially responsible: ...
Signature: ...
```

### Retrieved: L_2006015EN.01000101 / chunk_6

Resolution: document_chunk_sqlite

```text
(54) In the absence of any new information or evidence submitted, the provisional findings concerning the imports into the Community from Norway (volume, market share and average prices) as set out in recitals 54 to 59 of the provisional Regulation are hereby confirmed.
4.7. Price undercutting
(55) For the purposes of calculating the level of price undercutting during the IP, the methodology used at provisional stage was also used at definitive stage. The weighted average sales prices of the five companies selected in the sample of Community producers were compared to the weighted average export prices of the sampled exporting producers from Norway on a type-by-type basis. This comparison was made for comparable types of farmed salmon and at the same level of trade, namely for sales to the first independent customer. The comparison was made after deduction of rebates and discounts and the prices of the imports were CIF Community frontier, adjusted for customs duties. (56) The prices of the sampled Community producers were taken at an ex-works level, i.e. excluding transport costs and at levels of trade comparable to those of the imports concerned. For those sampled Community producers which sold their fish at the farm gate with a deduction of a fee paid to a processing factory, an upward adjustment was made to reflect processing and packing costs in order to make their prices comparable to those of other producers in the sample and to the imports subject to investigation. This adjustment was made on the basis of the actual fee paid to the processing facility or on the basis of the costs incurred by other producers in the sample for these activities. (57) As a result, the price comparison exercise showed that prices of salmon originating in Norway were significantly undercutting the Community industry prices on the Community market during the IP. The average undercutting margin, when expressed as a percentage of the Community industry's prices, was established at around 12 %, i.e. there was, as at the provisional stage, substantial undercutting
4.8. Situation of the Community industry
(58) It is recalled that in recital 89 of the provisional Regulation, it was provisionally established that the Community industry had suffered material injury within the meaning of Article 3 of the basic Regulation. (59) Several interested parties questioned the interpretation of the figures relating to the situation of the Community industry as presented in recitals 63 to 89 of the provisional Regulation. They stated that the figures did not show any material injury because some injury indicators, such as production, production capacity, sales volume and stocks showed positive trends. At the same time, whilst they admitted that the business perspectives of the Community industry are not very positive, they considered that overall this should not lead to the conclusion that the Community industry has suffered material injury. (60) In view of these claims, the Commission continued its investigation of injury. It is recalled that as mentioned at recital 40 above, 15 complaining Community producers now constitute the Community industry and, as mentioned at recital 49, five complaining Community producers were selected for the sample. On this basis, the following findings are made.
4.8.1. Production, production capacity and capacity utilisation
(61) The production, the production capacity and the capacity utilisation of the Community industry as a whole developed as follows: Table 1 Production, production capacity and capacity utilisation (62) As shown in the table above, production of the Community industry overall increased by 5 % during the period considered. Production first increased by 8 % between 2001 and 2002 but it subsequently decreased by around 1 %, and further decreased again by 2 % in the IP, remaining below the level of 2002. The trends observed are in line with those found at the provisional stage. (63) During the period considered production capacity increased by 21 %. The main increase took place in 2002 (+ 14 %). It is recalled that farmed salmon production in the Community is effectively limited by government licences specifying the maximum amount of live fish, which may be held in the water at any place at any point in time. Thus, the above capacity figures reflect a theoretical capacity based on the total quantity licensed rather than the physical fish-holding capacity of the cages or other production material operated by the Community industry. It is therefore considered that these capacity figures are not decisive in the analysis, as the actual production capacity is lower. (64) Capacity utilisation first decreased by 5 % between 2001 and 2002 and further decreased in 2003 by around 7 % and during the IP by around 2 %.
4.8.2. Sales volume, market shares, average unit prices in the EC and growth
```

### Retrieved: L_202402746EN / chunk_25

Resolution: document_chunk_sqlite

```text
The quantities of quota (owned quota, rented-in quota and rented-out quota) are compulsory items. Only the quantity as of the end of the accounting year is recorded.
The values concerning quotas which can be traded separately from associated land are recorded in this table. The quotas which cannot be traded separately from associated land are only recorded in Table D 'Assets'. The quotas originally acquired freely must be entered as well and valuated at current market values if they can be traded separately from land.
Some data entries are simultaneously included, individually or as components of aggregates, at other groups or categories in Tables D 'Assets', H 'Inputs' and/or I 'Crops'.
The following categories must be used:
50 Organic manure 60 Entitlements for payments under the basic payment scheme and entitlements for payments under basic income support for sustainability.
The following groups of information must be used:
E.QQ. Quantity (to be recorded for columns N, I, O only)
The units to be used are:
- Category 50 (organic manure): number of animals converted with standard conversion factors for manure excretion, * Category 60 (basic payment scheme and basic income support for sustainability): number of entitlements
E.QP. Quota purchased (to be recorded for column N only)
The amount paid for purchase during the accounting year of quotas or other rights which can be traded separately from associated land should be recorded.
E.QS. Quota sold (to be recorded for column N only)
The amount received for sale during the accounting year of quotas or other rights which can be traded separately from associated land should be recorded.
E.OV. Opening valuation (to be recorded for column N only)
The value at opening valuation of the quantities at the holder's own disposal, whether originally acquired freely or purchased, should be recorded at current market values, if the quotas can be traded separately from associated land.
E.CV. Closing valuation (to be recorded for column N only)
The value at closing valuation of the quantities at the holder's own disposal, whether originally acquired freely or purchased, should be recorded at current market values if the quotas can be traded separately from associated land.
E.PQ. Payments for quota leased or rented in quota (to be recorded for column I only)
Amount paid for leasing or renting of quotas or other rights. Also included in rent paid under category 5070 (Rent paid) in Table H 'Inputs'.
E.RQ. Receipts from leasing or renting out quota (to be recorded for column O only)
Amount received for renting or leasing of quotas or other rights. Also included under category 90900 ('Other') in Table I 'Crops'.
E.TX. Taxes, additional levy (column T)
Amount paid.
COLUMNS IN TABLE E
Column N refers to owned quota, column I to rented-in quota, column O to rented-out quota, and column T to taxes.
Table F
Debts and credits
Structure of the table
Liabilities of the holding: the amounts indicated shall relate only to amounts still outstanding, i.e., loans contracted minus the repayments already made.
The following categories are to be used:
    1. Debt - commercial standard - refers to loans not supported by any public policy targeting loan-taking. - 1020. Debt - commercial special - refers to loans benefiting from a public policy support (interest subsidies, guarantees, etc.). - 1030. Debt - family/private loans - loans concluded with a physical person thanks to their family/private relationship with the debtor. - 2010. Payables - amounts owed to suppliers. - 3000. Other liabilities - liabilities other than loans or payables.
Two groups of information are to be registered: (OV) opening valuation and (CV) closing valuation.
There are two columns: (S) short-term liabilities and (L) long-term liabilities:
- Short-term liabilities - debt and other liabilities in respect of the holding due in less than one year. - Long-term liabilities - debt and other liabilities in respect of the holding for duration of one year and over.
Table G
Value added tax (VAT)
Structure of the table
Data in monetary terms in the farm return are expressed exclusive of VAT.
The following details on VAT should be provided as categories:
1. Main VAT system in the farm
2. Minority VAT system in the farm
Codes as defined for the main VAT system.
There is only one group of information (VA) VAT system in the farm. There are three columns: (C) code of the VAT system, (NI) balance non-investments transactions and (I) balance investment transactions.
```

### Retrieved: L_2010021EN.01000101 / chunk_21

Resolution: document_chunk_sqlite

```text
[( 48 )](#ntc48-L_2010021EN.01001901-E0048)
Provisional quota in accordance with Article 1(2).
[( 49 )](#ntc49-L_2010021EN.01001901-E0049)
The use of this quota is subject to the conditions set out in point 3 of the Appendix to this Annex.
[( 50 )](#ntc50-L_2010021EN.01001901-E0050)
By-catches of cod, haddock and saithe shall be counted against the quotas for these species.
[( 51 )](#ntc51-L_2010021EN.01001901-E0051)
Provisional quota in accordance with Article 1(2).
[( 52 )](#ntc52-L_2010021EN.01001901-E0052)
Within an overall TAC of 55 105 tonnes for the northern stock of hake.
[( 53 )](#ntc53-L_2010021EN.01001901-E0053)
Within an overall TAC of 55 105 tonnes for the northern stock of hake.
[( 54 )](#ntc54-L_2010021EN.01001901-E0054)
Transfers of this quota may be effected to EU waters of IIa and IV. However, such transfers must be notified in advance to the Commission.
[( 55 )](#ntc55-L_2010021EN.01001901-E0055)
Within an overall TAC of 55 105 tonnes for the northern stock of hake.
[( 56 )](#ntc56-L_2010021EN.01001901-E0056)
Transfers of this quota may be effected to IV and EU waters of IIa. However, such transfers must be notified in advance to the Commission.
[( 57 )](#ntc57-L_2010021EN.01001901-E0057)
Within an overall TAC of 55 105 tonnes for the northern stock of hake.
[( 58 )](#ntc58-L_2010021EN.01001901-E0058)
Provisional quota in accordance with Article 1(2).
[( 59 )](#ntc59-L_2010021EN.01001901-E0059)
Of which up to 68 % may be fished in Norwegian Exclusive Economic Zone or in the fishery zone around Jan Mayen (WHB/*NZJM1). This condition will only be applicable as from the date of conclusion of the bilateral fisheries arrangement with Norway for 2010.
[( 60 )](#ntc60-L_2010021EN.01001901-E0060)
Of which up to 27 % may be fished in Faroese waters (WHB/*05B-F). This condition will only be applicable as from the date of conclusion of the bilateral fisheries arrangement with the Faroe Islands for 2010.
[( 61 )](#ntc61-L_2010021EN.01001901-E0061)
Provisional quota in accordance with Article 1(2).
[( 62 )](#ntc62-L_2010021EN.01001901-E0062)
Provisional quota in accordance with Article 1(2).
[( 63 )](#ntc63-L_2010021EN.01001901-E0063)
Of which up to 68 % may be fished in Norwegian Exclusive Economic Zone or in the fishery zone around Jan Mayen (WHB/*NZJM2). This condition will only be applicable as from the date of conclusion of the bilateral fisheries arrangement with Norway for 2010.
```

### Retrieved: 31988Y0204_02_en / chunk_7

Resolution: document_chunk_sqlite

```text
Table 3 - Expenditure on each type of measure - Flood II 30 November 1985 Measure Description Expenditure budgeted for 1978-85 Expenditure incurred as at 30 November 1985 Cr Rs % % of Cr Rs actual total measures scheduled 1 Transport and processing capacity (
*) 150 31 151 46 101 2 Technical inputs for milk production (*
) 109 22 39 12 36 3 Milk marketing (
*) 54 11 26 8 48 4 Support for village cooperatives 65 13 15 5 23 5 Planning, information, training and research (*
```

### Expected table: C_2022236EN.01000501 / table_11

```json
{
  "document_id": "C_2022236EN.01000501",
  "table_id": "table_11",
  "row_ids": [
    1
  ],
  "headers": [
    "Installation ID",
    "Installation ID (Union registry)",
    "Installation name",
    "Operator name",
    "Quantity to be allocated | 2021",
    "Quantity to be allocated | 2022",
    "Quantity to be allocated | 2023",
    "Quantity to be allocated | 2024",
    "Quantity to be allocated | 2025",
    "Quantity to be allocated by installation"
  ],
  "rows": [
    [
      "IE000000000000027",
      "27",
      "Lakeland Dairies Killeshandra Site",
      "Lakeland Dairies Co-operative Society Ltd.",
      "4 334",
      "4 334",
      "4 334",
      "4 334",
      "4 334",
      "21 670"
    ]
  ]
}
```

### Retrieved table: C_2022236EN.01000501 / table_11

```json
{
  "document_id": "C_2022236EN.01000501",
  "table_id": "table_11",
  "row_ids": [
    1
  ],
  "headers": [
    "Installation ID",
    "Installation ID (Union registry)",
    "Installation name",
    "Operator name",
    "Quantity to be allocated | 2021",
    "Quantity to be allocated | 2022",
    "Quantity to be allocated | 2023",
    "Quantity to be allocated | 2024",
    "Quantity to be allocated | 2025",
    "Quantity to be allocated by installation"
  ],
  "rows": [
    [
      "IE000000000000027",
      "27",
      "Lakeland Dairies Killeshandra Site",
      "Lakeland Dairies Co-operative Society Ltd.",
      "4 334",
      "4 334",
      "4 334",
      "4 334",
      "4 334",
      "21 670"
    ]
  ]
}
```

### Retrieved table: L_202500325EN / table_5

```json
{
  "document_id": "L_202500325EN",
  "table_id": "table_5",
  "row_ids": [
    2
  ],
  "headers": [
    "",
    "2020",
    "2021",
    "2022",
    "RIP"
  ],
  "rows": [
    [
      "Production capacity (tonnes)",
      "480 578",
      "477 621",
      "477 379",
      "476 874"
    ]
  ]
}
```

### Retrieved table: L_202402163EN / table_6

```json
{
  "document_id": "L_202402163EN",
  "table_id": "table_6",
  "row_ids": [
    2
  ],
  "headers": [
    "",
    "2020",
    "2021",
    "2022",
    "IP"
  ],
  "rows": [
    [
      "Production capacity (tonnes)",
      "21 360 776",
      "21 406 110",
      "21 686 443",
      "21 574 276"
    ]
  ]
}
```

### Retrieved table: L_202500325EN / table_5

```json
{
  "document_id": "L_202500325EN",
  "table_id": "table_5",
  "row_ids": [
    4
  ],
  "headers": [
    "",
    "2020",
    "2021",
    "2022",
    "RIP"
  ],
  "rows": [
    [
      "Capacity utilisation (%)",
      "83,6",
      "83,0",
      "56,1",
      "36,9"
    ]
  ]
}
```

### Retrieved table: L_202500325EN / table_5

```json
{
  "document_id": "L_202500325EN",
  "table_id": "table_5",
  "row_ids": [
    0
  ],
  "headers": [
    "",
    "2020",
    "2021",
    "2022",
    "RIP"
  ],
  "rows": [
    [
      "Production volume (tonnes)",
      "401 780",
      "396 575",
      "268 034",
      "175 786"
    ]
  ]
}
```

## global_natural_020

How does the fisheries table distinguish a metier from a fleet segment across its listed geographic aggregation levels?

Draft reference: Rows 0–2 distinguish Metier*Fleet segment (Cell): A/A1/A2/A3; Metier: B/B1/B2/B3; Fleet segment: C/C1/C2/C3 across the displayed geographic levels. Do not invent the substantive meaning of the symbols.

Retrieval execution status: success (NOT relevance)

### Retrieved: L_2010041EN.01000801 / chunk_8

Resolution: document_chunk_sqlite

```text
1. Variables
2. Variables to be collected are listed in Appendix VIII. Data shall be provided according to the periodicity stated in that Appendix. 2. Some delays may occur between information provided on the fleet segmentation and on the fishing effort.
3. Disaggregation level
4. The disaggregation level is given in Appendix VIII in accordance with the criteria defined in Appendix V. 2. The degree of aggregation shall correspond to the most disaggregated level required. A grouping of cells within this scheme may be made provided that an appropriate statistical analysis demonstrates its suitability. Such mergers must be approved by the relevant Regional Coordination Meeting.
5. Sampling strategy
6. Wherever possible, transversal data shall be collected in an exhaustive way. Where this is not possible, Member States shall specify the sampling procedures within their national programmes.
7. Precision levels
8. Member States shall include in their annual report information on the quality (accuracy and precision) of the data.
D. RESEARCH SURVEYS AT SEA
1. All surveys listed in Appendix IX shall be covered. 2. Member States shall guarantee within their national programmes, continuity with previous survey designs. 3. Notwithstanding points 1 and 2, Member States may propose a modification in the survey effort or sampling design, provided that this does not negatively affect the quality of the results. Acceptance by the Commission of any modification shall be conditional to STECF approval.
CHAPTER IV
Module of evaluation of the economic situation of the aquaculture and the processing industry sectors
A. COLLECTION OF ECONOMIC DATA FOR THE AQUACULTURE SECTOR
1. Variables
2. All variables listed in Appendix X are to be collected on an annual basis per segment according to the segmentation set out in Appendix XI. 2. The statistical unit shall be the 'enterprise' defined as the lowest legal entity for accounting purposes. 3. The population shall refer to enterprises whose primary activity is defined according to the EUROSTAT definition under NACE Code 05.02: 'Fish Farming'. 4. National currencies shall be transformed into Euro using the average annual exchange rate available from the European Central Bank (ECB).
3. Disaggregation level
4. Data shall be segmented by species and technique for aquaculture, as mentioned in Appendix XI. Member States may further segment by size of enterprise or other relevant criteria, if necessary. 2. Collection of data for fresh water species is not mandatory. However, if this data is collected, Member States shall follow the segmentation set out in Appendix XI.
5. Sampling strategy
6. Member States shall describe their methodologies for estimating each economic variable, including quality aspects, in their national programmes. 2. Member States shall ensure consistency and comparability of all economic variables when derived from different sources (e.g. questionnaires, financial accounts).
7. Precision levels
8. Member States shall include in their annual report information on the quality (accuracy and precision) of estimates.
B. COLLECTION OF ECONOMIC DATA CONCERNING THE PROCESSING INDUSTRY
1. Variables
2. All variables listed in Appendix XII are to be collected on an annual basis for the population. 2. The population shall refer to enterprises whose main activity is defined according to the EUROSTAT definition under NACE Code 15.20: 'Processing and preserving of fish and fish products'. 3. As a guideline, the national codes applied by Member States under Regulations (EC) No 852/2004 ( 4 ( 5 ( 6 4. National currencies shall be transformed into Euro using the average annual exchange rate available from the European Central Bank (ECB).
3. Disaggregation level
4. The statistical unit for collection of data shall be the 'enterprise' as defined as the lowest legal entity for accounting purposes. 2. For enterprises that carry out fish processing but not as a main activity, it is mandatory to collect the following data, in the first year of each programming period: (a) number of enterprises; (b) the turnover attributed to fish processing.
5. Sampling strategy
6. Member States shall describe their methodologies for estimating each economic variable, including quality aspects, in their national programmes. 2. Member States shall ensure consistency and comparability of all economic variables when derived from different sources (e.g. questionnaires, financial accounts).
7. Precision levels
8. Member States shall include in their annual report information on the quality (accuracy and precision) of estimates.
CHAPTER V
Module of evaluation of the effects of the fisheries sector on the marine ecosystem
```

### Retrieved: 31998D0414en / chunk_17

Resolution: document_chunk_sqlite

```text
In cases where an international organisation referred to in Annex IX, Article 1, of the Convention has competence over all the matters governed by this Agreement, the following provisions shall apply to participation by such international organisation in this Agreement: (a) at the time of signature or accession, such international organisation shall make a declaration stating: (i) that it has competence over all the matters governed by this Agreement; (ii) that, for this reason, its Member States shall not become States Parties, except in respect of their territories for which the international organisation has no responsibility; (iii) that it accepts the rights and obligations of States under this Agreement; (b) participation of such an international organisation shall in no case confer any rights under this Agreement on Member States of the international organisation; (c) in the event of a conflict between the obligations of an international organisation under this Agreement and its obligations under the agreement establishing the international organisation or any acts relating to it, the obligations under this Agreement shall prevail. Article 48 Annexes 1. The Annexes form an integral part of this Agreement and, unless expressly provided otherwise, a reference to this Agreement or to one of its Parts includes a reference to the Annexes relating thereto. 2. The Annexes may be revised from time to time by States Parties. Such revisions shall be based on scientific and technical considerations. Notwithstanding the provisions of Article 45, if a revision to an Annex is adopted by consensus at a meeting of States Parties, it shall be incorporated in this Agreement and shall take effect from the date of its adoption or from such other date as may be specified in the revision. If a revision to an Annex is not adopted by consensus at such a meeting, the amendment procedures set out in Article 45 shall apply. Article 49 Depositary The Secretary-General of the United Nations shall be the depositary of this Agreement and any amendments or revisions thereto. Article 50 Authentic texts The Arabic, Chinese, English, French, Russian and Spanish texts of this Agreement are equally authentic. In witness whereof, the undersigned Plenipotentiaries, being duly authorised thereto, have signed this Agreement. Opened for signature at New York, this fourth day of December, one thousand nine hundred and ninety-five, in a single original, in the Arabic, Chinese, English, French, Russian and Spanish languages. Annex I STANDARD REQUIREMENTS FOR THE COLLECTION AND SHARING OF DATA Article 1 General principles 1. The timely collection, compilation and analysis of data are fundamental to the effective conservation and management of straddling fish stocks and highly migratory fish stocks. To this end, data from fisheries for these stocks on the high seas and those in areas under national jurisdiction are required and should be collected and compiled in such a way as to enable statistically meaningful analysis for the purposes of fishery resource conservation and management. These data include catch and fishing effort statistics and other fishery-related information, such as vessel-related and other data for standardising fishing effort. Data collected should also include information on non-target and associated or dependent species. All data should be verified to ensure accuracy. Confidentiality of non-aggregated data shall be maintained. The dissemination of such data shall be subject to the terms on which they have been provided. 2. Assistance, including training as well as financial and technical assistance, shall be provided to developing States in order to build capacity in the field of conservation and management of living marine resources. Assistance should focus on enhancing capacity to implement data collection and verification, observer programmes, data analysis and research projects supporting stock assessments. The fullest possible involvement of developing State scientists and managers in conservation and management of straddling fish stocks and highly migratory fish stocks should be promoted. Article 2 Principles of data collection, compilation and exchange The following general principles should be considered in defining the parameters for collection, compilation and exchange of data from fishing operations for straddling fish stocks and highly migratory fish stocks: (a) States should ensure that data are collected from vessels flying their flag on fishing activities according to the operational characteristics of each fishing method (e.g., each individual tow for trawl, each set for long-line and purse-seine, each school fished for pole-and-line and each day fished for troll) and in sufficient detail to facilitate effective stock assessment; (b) States should ensure that fishery data are verified through an appropriate system; (c) States should compile fishery-related and other supporting scientific data and provide them in an agreed format and in a timely manner to the relevant subregional or regional fisheries management organisation or arrangement where one exists.
```

### Retrieved: 31998D0414en / chunk_11

Resolution: document_chunk_sqlite

```text
Such procedures shall be consistent with this Article and the basic procedures set out in Article 22 and shall not discriminate against non-members of the organisation or non-participants in the arrangement. Boarding and inspection as well as any subsequent enforcement action shall be conducted in accordance with such procedures. States shall give due publicity to procedures established pursuant to this paragraph. 3. If, within two years of the adoption of this Agreement, any organisation or arrangement has not established such procedures, boarding and inspection pursuant to paragraph 1, as well as any subsequent enforcement action, shall, pending the establishment of such procedures, be conducted in accordance with this Article and the basic procedures set out in Article 22. 4. Prior to taking action under this Article, inspecting States shall, either directly or through the relevant subregional or regional fisheries management organisation or arrangement, inform all States whose vessels fish on the high seas in the subregion or region of the form of identification issued to their duly authorised inspectors. The vessels used for boarding and inspection shall be clearly marked and identifiable as being on government service. At the time of becoming a Party to this Agreement, a State shall designate an appropriate authority to receive notifications pursuant to this Article and shall give due publicity of such designation through the relevant subregional or regional fisheries management organisation or arrangement. 5. Where, following a boarding and inspection, there are clear grounds for believing that a vessel has engaged in any activity contrary to the conservation and management measures referred to in paragraph 1, the inspecting State shall, where appropriate, secure evidence and shall promptly notify the flag State of the alleged violation. 6. The flag State shall respond to the notification referred to in paragraph 5 within three working days of its receipt, or such other period as may be prescribed in procedures established in accordance with paragraph 2, and shall either: (a) fulfil, without delay, its obligations under Article 19 to investigate and, if evidence so warrants, take enforcement action with respect to the vessel, in which case it shall promptly inform the inspecting State of the results of the investigation and of any enforcement action taken; or (b) authorise the inspecting State to investigate. 7. Where the flag State authorises the inspecting State to investigate an alleged violation, the inspecting State shall, without delay, communicate the results of that investigation to the flag State. The flag State shall, if evidence so warrants, fulfil its obligations to take enforcement action with respect to the vessel. Alternatively, the flag State may authorise the inspecting State to take such enforcement action as the flag State may specify with respect to the vessel, consistent with the rights and obligations of the flag State under this Agreement. 8. Where, following boarding and inspection, there are clear grounds for believing that a vessel has committed a serious violation, and the flag State has either failed to respond or failed to take action as required under paragraphs 6 or 7, the inspectors may remain on board and secure evidence and may require the master to assist in further investigation including, where appropriate, by bringing the vessel without delay to the nearest appropriate port, or to such other port as may be specified in procedures established in accordance with paragraph 2. The inspecting State shall immediately inform the flag State of the name of the port to which the vessel is to proceed. The inspecting State and the flag State and, as appropriate, the port State shall take all necessary steps to ensure the well-being of the crew regardless of their nationality. 9. The inspecting State shall inform the flag State and the relevant organisation or the participants in the relevant arrangement of the results of any further investigation. 10. The inspecting State shall require its inspectors to observe generally accepted international regulations, procedures and practices relating to the safety of the vessel and the crew, minimise interference with fishing operations and, to the extent practicable, avoid action which would adversely affect the quality of the catch on board. The inspecting State shall ensure that boarding and inspection is not conducted in a manner that would constitute harassment of any fishing vessel. 11.
```

### Retrieved: 31993D0464en / chunk_6

Resolution: document_chunk_sqlite

```text
The framework already laid down for transport statistics will, of course, continue to be developed through the revision of directives on transport by road, rail and inland waterway and these will be extended to air and sea transport. The information system must be consolidated by a more intermodal approach which can link sectoral methodologies and simplify survey organization. 5. R & D statistics The competency for research and technological development vested in the Community by virtue of the Single Act, strenghtened by the Maastricht agreements and Community policy on promoting innovation, calls for up-to-date and precise statistics. Pursuant to the proposal for a Council Decision on R & D and innovation statistics, the aims of the 1993 to 1997 programme will be to consolidate the present situation and to extend data collection activities, i.e. new information on R & D workers, measuring the technological potential of the regions and pilot surveys on innovation. Cooperation with the OECD should be stepped up so as to obtain information on R & D financing and expenditure within shorter deadlines. 6. Energy statistics The outlook for energy statistics depends on developments in the economic situation in general and the energy market in particular. Efforts will be directed at improving balance sheets, as regards both product breakdowns and aggregates. The price and consumption surveys will need to be expanded so as to provide better coverage. The activities envisaged will improve, and render more comparable, statistics on the transparency of energy prices and flows, security of supply with targeted measures regarding the extension of the geographical distribution of resourced, the substitution of energy products, the rational use of energy, the exploitation of renewable energy sources, the impact on the environment of emissions resulting from the transformation of energy products (CO2, SO2 etc.) and assessment of their economic significance and on regional energy investment. A strategy of careful use of non-energy raw materials is an important counterpart to these activities. When the networks are opened up, statistical monitoring of their use may be necessary. 7. Tourism statistics A system of tourism statistics will need to be set up in the context of the European Economic Area, based mainly on tourist supply and demand. B. The sectoral programmes for management of the common agricultural policy (CAP) and fisheries statistics Purpose To contribute to the statistical information necessary to manage and monitor the arrangements made under the CAP and as part of fisheries policy. Statistical objectives To propose to the Member States the Community surveys to be carried out, the comparable processing of national surveys, the application of harmonized standards and the introduction of common infrastructure statistics in the following fields: 1. Agricultural statistics Agricultural statistics will undergo a significant change in the coming years as a result of the reform of the CAP and the implementation of the results of a 'screening' operation carried out under the previous programme. It seems inevitable that changes to the instruments for collecting information on production and forecasting production, prices, revenues and agricultural structures will be necessary. The goal is to attain better utilization of the resources devoted to agricultural statistics while limiting as far as possible the growing administrative burden on farmers. (a) Agricultural production Crop production: the introduction of stabilizers in various sectors of crop production, as well as certain likely elements in CAP reform, have emphasized the need to improve the quality, comparability and provision times of these statistics. Reform of the CAP will reinforce the direct impact of statistics on market management. It is therefore necessary not only to create a binding legal framework for crop statistics, but also to continue to seek the most appropriate means of guaranteeing their reliability and objectivity whilst containing financial and manpower costs as far as possible. It is with this aim in mind that research on sampling and forecasting techniques and remote sensing for agricultural statistics will be continued and, if possible, intensified. Animal production: Community statistics and legislation will have to adapt to changes in the markets and market management; they will therefore need to be reviewed carefully at regular intervals in order to ensure that the objectives can be attained at the lowest cost, taking account in particular of the different levels of importance of production in the various countries. Special attention will have to be paid to improving the overall information on slaughterings. Supply balances: these balances provide a synthesis of the statistics on the supply and uses of the various crop and animal products, and their main function is to permit monitoring of the degree of self-sufficiency and of consumption. Adaptations may be required as a consequense of the new system of intra-Community trade after 1992. It is necessary to improve their quality and better define the essential information required, taking account of the fact that the figures constitute reference data for international agreements, in particular for GATT. Fodder supply balances: statistics have been compiled for the last 20 years on the supply of animal feedingstuffs. Studies have been undertaken to determine the nutritional needs of animals in order to assess the demand for feedingstuffs well before data on supply are known.
```

### Retrieved: L_202302842EN / chunk_41

Resolution: document_chunk_sqlite

```text
Member States shall set up an electronic database for the purpose of validation of data recorded in accordance with this Regulation. The validation of the data recorded shall include the cross-checking, analysis and verification of the data. 2. Member States shall ensure that all data recorded in accordance with this Regulation are accurate, complete and submitted by operators, masters or other persons authorised under this Regulation within deadlines laid down in the rules of the common fisheries policy.' (b) the following paragraph is inserted: '2a. For the purposes of paragraphs 1 and 2: (c) paragraph 5 is replaced by the following: '5. If an inconsistency in the data has been identified, the Member State concerned shall undertake and document the necessary investigations, analyses and cross-checks. The results of the investigations and corresponding documentation shall be transmitted to the Commission on request. If there are reasons to suspect that an infringement has been committed, the Member State shall also carry out investigations and take the necessary immediate measures in accordance with Articles 85 and 91.' (d) paragraph 8 is replaced by the following: '8. Member States shall establish and keep up to date a national plan for the implementation of the validation system covering the data listed under paragraph 2a, points (a) and (b), and the follow-up of inconsistencies. The plan shall define the Member State priorities for the validation of data and subsequent follow-up on inconsistencies, following a risk-based approach. Member States shall submit that national plan to the Commission within two months from its adoption or update.' (86) Articles 110 and 111 are replaced by the following: 'Article 110 Access to, storage and processing of data 1. Member States shall ensure the remote access at all time and without prior notice, for the Commission or the body designated by it, of the following data in a non-aggregated form: 2. The Commission or the body designated by it may process the data referred to in paragraph 1, in order to fulfil their duties under the rules of the common fisheries policy, in particular for carrying out inspections, verifications, audits and enquiries, or under the rules of agreements with third countries or international organisations. In addition, the Commission may use data referred in paragraph 1 for the development, production and dissemination of European statistics, in particular by Eurostat in accordance with Regulation (EC) No 223/2009 of the European Parliament and of the Council ( *16 3. For the purpose of performing scientific research or provide scientific advice, data listed in paragraph 1, point (a)(i) to (iv), and data concerning catches, discards and landings listed in paragraph 1, point (b)(iii) and (v), may, where necessary, be provided to independent scientific bodies that are recognised at Union, national or international level. Before transferring such data, Member States shall consider whether the scientific research can be conducted on the basis of pseudonymised or anonymised data. In any advice or publication based on such data, those data shall be anonymised. 4. Member States shall establish, implement and host the relevant fisheries databases containing the data referred to in paragraph 1. 5. Member States shall upon a reasoned request by the Commission transmit data on infringements to the Commission or the body designated by it. The data shall include, in particular, the date of the infringement, the date of the definitive decision and the applied sanctions and measures, including assigned points. Article 111 Exchange of data 1. Each flag Member State shall ensure the direct electronic exchange of relevant information with other Member States concerned, in particular: 2. Each coastal Member State shall ensure the direct electronic exchange of relevant information with other Member States concerned and the Commission or the body designated by it, in particular by sending: 3. Each flag Member State shall ensure the direct electronic exchange of relevant information concerning vessels flying its flag to the Commission or the body designated by it, in particular: ( *16 OJ L 87, 31.3.2009, p. 164 (87) The following article is inserted: 'Article 111a Uniform conditions for the implementation of provisions on data For the purpose of implementing provisions of this Chapter, the Commission may, by means of implementing acts, lay down detailed rules on: Those implementing acts shall be adopted in accordance with the examination procedure referred to in Article 119(2).'. (88) Article 112 is replaced by the following: 'Article 112 Protection of personal data 1. Regulations (EU) 2016/679 ( *17 ( *18 ( *19 2. Personal data collected under this Regulation may only be processed for the following purposes, provided that those purposes cannot be fulfilled with data that do not permit identification of data subjects: 3.
```

### Retrieved: L_2013354EN.01008601 / chunk_3

Resolution: document_chunk_sqlite

```text
1. Until 31 December 2021, Article 5(3) and Articles 6, 8, 41, 56, 58 to 62, 66, 68 and 109 shall not apply to France in respect of fishing vessels which are less than 10 metres in overall length and which operate from Mayotte, an outermost region within the meaning of Article 349 of the Treaty on the Functioning of the European Union (hereinafter "Mayotte"), and the activities and catch of such fishing vessels.
2. By 30 September 2014, France shall establish a simplified and provisional scheme of control applicable to fishing vessels which are less than 10 metres in overall length and which operate from Mayotte. That scheme shall address the following issues:
(a) knowledge of fishing capacity; (b) access to Mayotte waters; (c) implementation of declaration obligations; (d) designation of the authorities responsible for the control activities; (e) measures ensuring that any enforcement on vessels longer than 10 metres length is carried out on a non-discriminatory basis.
By 30 September 2020, France shall present to the Commission an action plan setting out the measures to be taken in order to ensure the full implementation of Regulation (EC) No 1224/2009 from 1 January 2022 concerning fishing vessels which are less than 10 metres in overall length and which operate from Mayotte. That action plan shall be the subject of a dialogue between France and the Commission. France shall take all necessary measures to implement that action plan."
Article 6
Entry into force
This Regulation shall enter into force on 1 January 2014.
This Regulation shall be binding in its entirety and directly applicable in all Member States.
Done at Brussels, 17 December 2013.
For the Council
The President
L. LINKEVIČIUS
[( 1 )](#ntc1-L_2013354EN.01008601-E0001)
Opinion of 12 December 2013 (not yet published in the Official Journal).
[( 2 )](#ntc2-L_2013354EN.01008601-E0002)
[OJ C 341, 21.11.2013, p. 97](http://publications.europa.eu/resource/oj/JOC_2013_341_R_TOC)
.
[( 3 )](#ntc3-L_2013354EN.01008601-E0003)
European Council Decision 2012/419/EU of 11 July 2012 amending the status of Mayotte with regard to the European Union (
[OL L 204, 31.7.2012, p. 131](http://publications.europa.eu/resource/oj/JOL_2012_204_R_TOC)
).
[( 4 )](#ntc4-L_2013354EN.01008601-E0004)
Council Regulation (EC) No 850/98 of 30 March 1998 for the conservation of fishery resources through technical measures for the protection of juveniles of marine organism (
[OJ L 125, 27.4.1998, p. 1](http://publications.europa.eu/resource/oj/JOL_1998_125_R_TOC)
).
[( 5 )](#ntc5-L_2013354EN.01008601-E0005)
See page 1 of this Official Journal.
[( 6 )](#ntc6-L_2013354EN.01008601-E0006)
See page 22 of this Official Journal.
```

### Retrieved: L_2021253EN.01005101 / chunk_5

Resolution: document_chunk_sqlite

```text
Table 4 (previously Table 3)
Species for which data are to be collected for recreational fisheries
Table 5 (previously Table 2)
Fishing activity (metier)
Table 6 (previously Table 4)
Fishing activity variables
Table 7 (previously Table 5A)
Fleet economic variables
Table 8 (previously Table 5B)
Fleet segmentation
Table 9 (previously Table 6)
Social variables for the fishing and aquaculture sectors
Table 10 (previously Table 7)
Economic variables in the aquaculture sector
Table 11 (previously Table 9)
Segmentation to be applied for the collection of aquaculture data
[( 65 )](#ntr65-L_2021253EN.01005301-E0065)
[( 1 )](#ntc1-L_2021253EN.01005301-E0001)
Regulation (EU) 2017/1004 of the European Parliament and of the Council of 17 May 2017 on the establishment of a Union framework for the collection, management and use of data in the fisheries sector and support for scientific advice regarding the common fisheries policy and repealing Council Regulation (EC) No 199/2008 (
[OJ L 157, 20.6.2017, p. 1](http://publications.europa.eu/resource/oj/JOL_2017_157_R_TOC)
).
[( 2 )](#ntc2-L_2021253EN.01005301-E0002)
Council Regulation (EC) No 1224/2009 of 20 November 2009 establishing a Union control system for ensuring compliance with the rules of the common fisheries policy, amending Regulations (EC) No 847/96, (EC) No 2371/2002, (EC) No 811/2004, (EC) No 768/2005, (EC) No 2115/2005, (EC) No 2166/2005, (EC) No 388/2006, (EC) No 509/2007, (EC) No 676/2007, (EC) No 1098/2007, (EC) No 1300/2008, (EC) No 1342/2008 and repealing Regulations (EEC) No 2847/93, (EC) No 1627/94 and (EC) No 1966/2006 (
[OJ L 343, 22.12.2009, p. 1](http://publications.europa.eu/resource/oj/JOL_2009_343_R_TOC)
).
[( 3 )](#ntc3-L_2021253EN.01005301-E0003)
Commission Implementing Regulation (EU) No 404/2011 of 8 April 2011 laying down detailed rules for the implementation of Council Regulation (EC) No 1224/2009 establishing a Community control system for ensuring compliance with the rules of the Common Fisheries Policy (
[OJ L 112, 30.4.2011, p. 1](http://publications.europa.eu/resource/oj/JOL_2011_112_R_TOC)
).
```

### Retrieved: L_2010041EN.01000801 / chunk_4

Resolution: document_chunk_sqlite

```text
1. Variables
2. Sampling must be performed in order to evaluate the quarterly length distribution of species in the catches, and the quarterly volume of discards. Data shall be collected by metier referred to as level 6 of the matrix defined in Appendix IV (1 to 5) and for the stocks listed in Appendix VII. 2. Where relevant additional biological sampling programmes of the unsorted landings have to be carried out in order to estimate: (a) the share of the various stocks in these landings for Herring in the Skagerrak IIIA-N, Kattegat IIIa-S, and Eastern North Sea separately and salmon in the Baltic Sea; (b) the share of the various species for those groups of species that are internationally assessed, e.g. Megrims, Anglerfishes and elasmobranches.
3. Disaggregation level
4. In order to optimise the sampling programmes, the metiers defined in Appendix IV (1 to 5) may be merged. When metiers are merged (vertical merging), statistical evidence shall be brought regarding the homogeneity of the combined metiers. Merging of neighbouring cells corresponding to fleet segments of the vessels (horizontal merging) shall be supported by statistical evidence. Such horizontal merging shall be done primarily by clustering neighbouring vessel LOA classes, independently of the dominant fishing techniques, when appropriate to distinguish different exploitation patterns. Regional agreement on mergers shall be sought at the relevant Regional Coordination Meeting and endorsed by STECF. 2. At national level, one metier defined at level 6 of the matrix in Appendix IV (1 to 5) may be further disaggregated into several more precise strata, i.e. distinguishing different target species. Such further stratification shall be done respecting the two following principles: (a) the strata defined at national level do not overlap the metiers defined in Appendix IV (1 to 5); (b) the strata defined at national level must, in their entirety comprise of all the fishing trips of the metier defined at level 6. 3. The spatial units for metier sampling are defined by level 3 of Appendix I for all the regions with the following exceptions: (a) the Baltic Sea (ICES areas III b-d), Mediterranean Sea and the Black Sea where the resolution shall be level 4; (b) Regional Fisheries Management Organisations units, providing they are metier-based (in the absence of such definitions, Regional Fisheries Management Organisations shall proceed to appropriate mergers). 4. For the purpose of collection and aggregation of data, spatial sampling units may be clustered by regions as referred to in Article 1 of Commission Regulation (EC) 665/2008 ( 2 5. For parameters referred to in Chapter III section B/B1 1. (2), data shall be provided quarterly and be consistent with the fleet fishing activity matrix described in Appendix IV (1 to 5).
5. Sampling strategy
```

### Expected table: L_2010041EN.01000801 / table_10

```json
{
  "document_id": "L_2010041EN.01000801",
  "table_id": "table_10",
  "row_ids": [
    0,
    1,
    2
  ],
  "headers": [
    "",
    "",
    "Sub regions or fishing grounds | 1",
    "Regions | 2",
    "Supra regions | 3"
  ],
  "rows": [
    [
      "Metier*Fleet segment (Cell)",
      "A",
      "A1",
      "A2",
      "A3"
    ],
    [
      "Metier",
      "B",
      "B1",
      "B2",
      "B3"
    ],
    [
      "Fleet segment",
      "C",
      "C1",
      "C2",
      "C3"
    ]
  ]
}
```

### Retrieved table: L_2022008EN.01014201 / table_26

```json
{
  "document_id": "L_2022008EN.01014201",
  "table_id": "table_26",
  "row_ids": [
    0
  ],
  "headers": null,
  "rows": [
    [
      "General comment: This table is intended to indicate the size of fleet segments and clustering schemes. The population shall include all active and inactive vessels registered in the Union Fishing Fleet Register, as defined in Commission Regulation (EU) 2017/218 on 31 December of the reporting year, and vessels that do not appear on the Register at that date but have fished at least one day during the reporting year.",
      "General comment: This table is intended to indicate the size of fleet segments and clustering schemes. The population shall include all active and inactive vessels registered in the Union Fishing Fleet Register, as defined in Commission Regulation (EU) 2017/218 on 31 December of the reporting year, and vessels that do not appear on the Register at that date but have fished at least one day during the reporting year."
    ]
  ]
}
```

### Retrieved table: L_2010041EN.01000801 / table_10

```json
{
  "document_id": "L_2010041EN.01000801",
  "table_id": "table_10",
  "row_ids": [
    0
  ],
  "headers": [
    "",
    "",
    "Sub regions or fishing grounds | 1",
    "Regions | 2",
    "Supra regions | 3"
  ],
  "rows": [
    [
      "Metier*Fleet segment (Cell)",
      "A",
      "A1",
      "A2",
      "A3"
    ]
  ]
}
```

### Retrieved table: L_2010041EN.01000801 / table_10

```json
{
  "document_id": "L_2010041EN.01000801",
  "table_id": "table_10",
  "row_ids": [
    2
  ],
  "headers": [
    "",
    "",
    "Sub regions or fishing grounds | 1",
    "Regions | 2",
    "Supra regions | 3"
  ],
  "rows": [
    [
      "Fleet segment",
      "C",
      "C1",
      "C2",
      "C3"
    ]
  ]
}
```

### Retrieved table: L_2022008EN.01014201 / table_28

```json
{
  "document_id": "L_2022008EN.01014201",
  "table_id": "table_28",
  "row_ids": [
    1
  ],
  "headers": null,
  "rows": [
    [
      "1. Description of clustering In cases where a fleet segment has less than 10 vessels: Clustering should be described, and information should be given on the segments that are clustered. The Member State should distinguish between segments considered for clustering as follows: Importance of fleet segments should be assessed in terms of landings (value and volume) and/or effort. Similarity should be demonstrated using expert knowledge on fishing patterns or on available data on landings and/or effort. For each of the cases described, the Member State should apply the following approaches for clustering according to the different characteristics of fleet segments: 2. Description of activity indicator If the Member State is using an activity indicator to divide the fleet segment into different activity levels, use ‘L’ for the low activity vessels and ‘A’ for the normal economic activity vessels. Please provide a description of the activity methodology used. 3. Deviation from the RCG ECON (ex. PGECON) definitions Describe and justify any deviations from variable definitions as listed in the ‘EU MAP Guidance Document’ on the DCF website. In case the PIM is not used, explain and justify the application of alternative methods. (max. 900 words)"
    ]
  ]
}
```

### Retrieved table: L_2010041EN.01000801 / table_10

```json
{
  "document_id": "L_2010041EN.01000801",
  "table_id": "table_10",
  "row_ids": [
    1
  ],
  "headers": [
    "",
    "",
    "Sub regions or fishing grounds | 1",
    "Regions | 2",
    "Supra regions | 3"
  ],
  "rows": [
    [
      "Metier",
      "B",
      "B1",
      "B2",
      "B3"
    ]
  ]
}
```
