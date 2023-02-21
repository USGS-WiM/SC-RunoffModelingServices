import math
import numpy as np
from SC_Synthetic_UH_Method import computeSCSyntheticUnitHydrograph


def calcponds():
        
    # Fixed Variables
    storm_duration = [1, 2, 3, 6, 12, 24] # hours, referred to as a D-hour storm
    burst_duration = 6
    max_depth = 10

    # Initialize output arrays
    pond_peak_inflow = []
    time_of_pond_peak_inflow = []
    pond_peak_outflow = []
    time_of_pond_peak_outflow = []
    pond_max_depth = []


    # TODO: These all need to be upper inputs
    unitHydrograph = computeSCSyntheticUnitHydrograph(33.3946, -80.3474, 10, "Merkel", 100.0, 78, "II", 240, 66.9, 4.94, 0.99)

    #pond 1
    length = 200
    w1 = 200
    w2 = 200
    side_slope_z = 3
    bottom_slope = .5

    #pond 2

    #both
    pond_bottom_elev = 100
    Orif1_Coeff=.6
    Orif1_Dia = 6
    Orif1_CtrEL = .5
    Orif1_NumOpenings = 1
    Orif2_Coeff=.6
    Orif2_Dia = 6
    Orif2_CtrEL = 2
    Orif2_NumOpenings = 1
    Rec_Weir_Coeff = 3.3
    Rec_Weir_Ex = 1.5
    Rec_Weir_Length = 2
    Rec_WeirCrest_EL = 4
    Rec_Num_Wiers = 1
    OS_BCWeir_Coeff = 3
    OS_Weir_Ex = 1.5
    OS_Length = 20
    OS_Crest_EL = 6
    Seepage_Bottom = 2
    Seepage_Side = 4

    # Initalize arrays used in 
    Q = [] # Pond_X hr, 2S_Dt, Y-Q (1) 
    S = [] # Pond_X, 2S_Dt+Q, Y-S (1)
    Total_L = [] # Y-S (1)
    Total_W1 = [] # Y-S (1)
    Total_W2 = [] # Y-S (1)
    A = [] # Y-S (1)
    change_S = [] # Pond_1 hr
    twoS_dtplusQ = [] # Y-S (1)

    # Caluclate values in Y-Q (1) sheet
    Orif1_A = 3.14159*((Orif1_Dia/12)**2)/4
    Orif2_A = 3.14159*((Orif2_Dia/12)**2)/4
    for Y in range(0, max_depth+1):
        h = pond_bottom_elev + Y
        # First Stage Orfice Total Flow
        Orif1_H = max(0,Y-Orif1_CtrEL)
        Orif1_Q = max(0,Orif1_Coeff*Orif1_A*math.sqrt(64.4*Orif1_H))   
        Orif1_total_flow = Orif1_NumOpenings*Orif1_Q
        # Second Stage Orfice Total Flow
        Orif2_H = max(0,Y-Orif2_CtrEL)
        Orif2_Q = max(0,Orif2_Coeff*Orif2_A*math.sqrt(64.4*Orif2_H)) 
        Orif2_total_flow = Orif2_NumOpenings*Orif2_Q
        # Upper Stage Rectangular Weir Total Flow
        Rec_Weir_H = max(0,Y-Rec_WeirCrest_EL)
        Rec_Single_Weir_Q = Rec_Weir_Coeff*Rec_Weir_Length*Rec_Weir_H**Rec_Weir_Ex
        Rec_Stage_total_flow = Rec_Single_Weir_Q*Rec_Num_Wiers
        # Overflow Spillway Q
        OS_H = max(0,Y-OS_Crest_EL)
        OS_Q = OS_BCWeir_Coeff*OS_Length*OS_H**OS_Weir_Ex
        # Seepage in cfs
        if Y == 0:
            Total_L.append(length+2*bottom_slope*(h-pond_bottom_elev))
            Total_W1.append(w1+2*side_slope_z*(h-pond_bottom_elev))
            Total_W2.append(w2+2*side_slope_z*(h-pond_bottom_elev))
            A1 = Total_L[Y]*(Total_W1[Y]+Total_W2[Y])/2
            A.append(A1)
        else:
            Total_L.append(Total_L[Y-1]+2*side_slope_z*(1)) # not sure if it will always be (1)
            Total_W1.append(Total_W1[Y-1]+2*side_slope_z*(1)) # not sure if it will always be (1)
            Total_W2.append(Total_W2[Y-1]+2*side_slope_z*(1)) # not sure if it will always be (1)
            A.append(Total_L[Y]*(Total_W1[Y]+Total_W2[Y])/2)
        if Y == 0:
            Seepage_Bottom_CFS = 0
            Seepage_Side_CFS = 0
        else:
            Seepage_Bottom_CFS = A1*Seepage_Bottom/(12*3600)
            Seepage_Side_CFS = (A[Y]-A1)*Seepage_Side/(12*3600)
        
        # Calculate Q in 2S_Dt+Q & Pond_X hr sheets
        Outflow_Q = Orif1_total_flow+Orif2_total_flow+Rec_Stage_total_flow+OS_Q+Seepage_Bottom_CFS+Seepage_Side_CFS
        Q.append(Outflow_Q) 
        # Calculate S in 2S_Dt+Q & Pond_X hr sheets; Calculate change in S from Y-S (1) sheet 
        if Y == 0:
            S.append(0)
            change_S.append(0)
        else:
            change_S.append(((A[Y-1]+A[Y])/2)*(1)) # not sure if it will always be (1)
            S.append(S[Y-1] + change_S[Y])
        # Calculate 2S/dt+Q in 2S_Dt+Q & Pond_X hr sheets
        twoS_dtplusQ.append((2*S[Y]/(60*burst_duration))+Q[Y])

        

    print(Q) 
    print(S)
    print(twoS_dtplusQ)
   

    # TODO Loop thorugh storm_duration
    # Initlaize arrays used in 
    time = unitHydrograph[3]['time'] # pond_x hr
    inflow = unitHydrograph[3]['flow_1_hour'] # pond_x hr TODO depends on storm_duration loop
    i1plusi2 = [] # pond_x hr (column E)
    twoS_dtplusQ2 = [] # pond_x hr (column F)
    twoS_dtminusQ1 = [] # pond_x hr (column E)
    Q2 = [] # pond_x hr (column H)
    Y2 = [] # pond_x hr (column G)
    outflows = [] # pond_x hr (as Q2) & D-hr Storm Pond Routing Results
    counter = 0



    for t in time:
        if counter == 0:
            i1plusi2.append(0)
            twoS_dtminusQ1.append(0)
            twoS_dtplusQ2.append(0)
            Y2.append(0)
            Q2.append(0)
        else:
            i1plusi2.append(inflow[counter-1] + inflow[counter])
            twoS_dtminusQ1.append(twoS_dtplusQ2[counter-1]-2*Q2[counter-1])
            twoS_dtplusQ2.append(i1plusi2[counter]+twoS_dtminusQ1[counter])
            # Q2
            if (twoS_dtplusQ2[counter]<twoS_dtplusQ[1]):
                Q2.append(Q[0]+((Q[1]-Q[0])/(twoS_dtplusQ[1]-twoS_dtplusQ[0]))*(twoS_dtplusQ2[counter]-twoS_dtplusQ2[0]))
            elif (twoS_dtplusQ2[counter]<twoS_dtplusQ[2]):  
                Q2.append(Q[1]+((Q[2]-Q[1])/(twoS_dtplusQ[2]-twoS_dtplusQ[1]))*(twoS_dtplusQ2[counter]-twoS_dtplusQ2[1]))
            elif (twoS_dtplusQ2[counter]<twoS_dtplusQ[3]):  
                Q2.append(Q[2]+((Q[3]-Q[2])/(twoS_dtplusQ[3]-twoS_dtplusQ[2]))*(twoS_dtplusQ2[counter]-twoS_dtplusQ2[2]))
            elif (twoS_dtplusQ2[counter]<twoS_dtplusQ[4]):                 
                Q2.append(Q[3]+((Q[4]-Q[3])/(twoS_dtplusQ[4]-twoS_dtplusQ[3]))*(twoS_dtplusQ2[counter]-twoS_dtplusQ2[3]))
            elif (twoS_dtplusQ2[counter]<twoS_dtplusQ[5]):  
                Q2.append(Q[4]+((Q[5]-Q[4])/(twoS_dtplusQ[5]-twoS_dtplusQ[4]))*(twoS_dtplusQ2[counter]-twoS_dtplusQ2[4]))
            elif (twoS_dtplusQ2[counter]<twoS_dtplusQ[6]):  
                Q2.append(Q[5]+((Q[6]-Q[5])/(twoS_dtplusQ[6]-twoS_dtplusQ[5]))*(twoS_dtplusQ2[counter]-twoS_dtplusQ2[5]))
            elif (twoS_dtplusQ2[counter]<twoS_dtplusQ[7]):  
                Q2.append(Q[6]+((Q[7]-Q[6])/(twoS_dtplusQ[7]-twoS_dtplusQ[6]))*(twoS_dtplusQ2[counter]-twoS_dtplusQ2[6]))
            elif (twoS_dtplusQ2[counter]<twoS_dtplusQ[8]): 
                Q2.append(Q[7]+((Q[8]-Q[7])/(twoS_dtplusQ[8]-twoS_dtplusQ[7]))*(twoS_dtplusQ2[counter]-twoS_dtplusQ2[7])) 
            elif (twoS_dtplusQ2[counter]<twoS_dtplusQ[9]):  
                Q2.append(Q[8]+((Q[9]-Q[8])/(twoS_dtplusQ[9]-twoS_dtplusQ[8]))*(twoS_dtplusQ2[counter]-twoS_dtplusQ2[8])) 
            elif (twoS_dtplusQ2[counter]<twoS_dtplusQ[10]): 
                Q2.append(Q[9]+((Q[10]-Q[9])/(twoS_dtplusQ[10]-twoS_dtplusQ[9]))*(twoS_dtplusQ2[counter]-twoS_dtplusQ2[9])) 
            else:
                Q2.append('error') 
            # Y2
        counter = counter + 1

    print('time:', time)
    print('inflow:', inflow)
    print('i1plusi2:', i1plusi2)
    print('twoS_dtminusQ1:', twoS_dtminusQ1)
    print('twoS_dtplusQ2:', twoS_dtplusQ2)
    print('Q2:', Q2)

    # Corresponds red arrow in the "D-hr Storm Pond Results" sheet
    #index_max_peak_outflow = np.argmax(pond_peak_outflow)
    #max_peak_outflow = storm_duration[index_max_peak_outflow]
    max_peak_outflow = 6

    runoff_and_ponding_results = {
        # "storm_duration": unitHydrograph[2]['storm_duration'],
        # "rainfall_depth": unitHydrograph[2]['rainfall_depth'],
        # "CN_adjusted_for_rainfall_duration": unitHydrograph[2]['CN_adjusted_for_rainfall_duration'],  # I think the spreadsheet is wrong here 
        # "runoff_volume_Q_CN": unitHydrograph[2]['runoff_volume_Q_CN'],
        # "pond_peak_inflow": pond_peak_inflow, # max of inflow (pond_x hr 19)
        # "time_of_pond_peak_inflow": time_of_pond_peak_inflow, # time of max inflow (pond_x hr k20)
        # "pond_peak_outflow": pond_peak_outflow, # max of outflow (pond_x hr k22)
        # "time_of_pond_peak_outflow": time_of_pond_peak_outflow, # time of max outflow (pond_x hr k23)
        # "max_peak_outflow_storm_duration": max_peak_outflow, # storm duration with max peak outflow
        # "max_depth": pond_max_depth # max_depth (pond_x hr k24)
    }

    pond_inflow_and_outflow_ordinates = {
        # "time": unitHydrograph[3]['time'],
        # "inflow_1_hour": unitHydrograph[3]['flow_1_hour'],
        # "outflow_1_hour": outflows[0],
        # "inflow_2_hour": unitHydrograph[3]['flow_2_hour'],
        # "outflow_2_hour": outflows[1],
        # "inflow_3_hour": unitHydrograph[3]['flow_3_hour'],
        # "outflow_3_hour": outflows[2],
        # "inflow_6_hour": unitHydrograph[3]['flow_6_hour'],
        # "outflow_6_hour": outflows[3],
        # "inflow_12_hour": unitHydrograph[3]['flow_12_hour'],
        # "outflow_12_hour": outflows[4],
        # "inflow_24_hour": unitHydrograph[3]['flow_24_hour'],
        # "outflow_24_hour": outflows[5]
    }

    return runoff_and_ponding_results, pond_inflow_and_outflow_ordinates
