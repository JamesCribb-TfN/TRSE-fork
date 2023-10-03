The final scripts `compile_final_bus_walk_matrix(task1 output).py` and `compile_final_bus_walk_rail_matrix(task 2 output).py` do not need to be run if scripts:
    A - `create_a1_a2_jt_matrix`
    B - `PBA_TRSE_Task_1_faster`
    C -  `PBA_TRSE_Task_2_faster`

have used a single OTP response file to generate outputs. 

Due to long run times & crashes, the initial evidence was collected over 5 seperate OTP runs. Thus each of the five runs had to be 
    passed through scripts A, B, C seperatly. These were then combined using the mentioned final script. Clearly if you have a single
    OTP run then you will only need to process this once using scripts A, B, C.