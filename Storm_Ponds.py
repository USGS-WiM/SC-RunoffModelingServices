import math
import numpy as np
from SC_Synthetic_UH_Method import computeSCSyntheticUnitHydrograph


def calcStormPonds(lat, lon, AEP, CNModificationMethod, Area, Tc, RainfallDistributionCurve, PRF, CN, S, Ia,
              pondOption, pond_bottom_elev, Orif1_Coeff, Orif1_Dia, Orif1_CtrEL, Orif1_NumOpenings, Orif2_Coeff, Orif2_Dia, Orif2_CtrEL, Orif2_NumOpenings, Rec_Weir_Coeff, Rec_Weir_Ex, Rec_Weir_Length, Rec_WeirCrest_EL, Rec_Num_Weirs, OS_BCWeir_Coeff, OS_Weir_Ex, OS_Length , OS_Crest_EL , Seepage_Bottom, Seepage_Side,
              length = None, w1 = None, w2 = None, side_slope_z = None, bottom_slope = None,
              Elev_Area = None):
        
    # lat, lon, AEP, CNModificationMethod, Area, Tc, RainfallDistributionCurve, PRF, CN, S, Ia: see computeSCSyntheticUnitHydrograph
    # pondOption: 1 or 2 
    # pond_bottom_elev: Elevation of pond bottom in feet
    # Orif1_Coeff & Orif2_Coeff: coefficient of 1st and 2nd stage circular orifices
    # Orif1_Dia & Orif2_Dia: Diameter of 1st and 2nd stage circular orifices in inches
    # Orif1_CtrEL & Orif2_CtrEL: Centerline elevation above bottom of pond for 1st and 2nd stage circular orifices in feet
    # Orif1_NumOpenings & Orif2_NumOpenings: number of openings for 1st and 2nd stage circular orifices
    # Rec_Weir_Coeff: 3rd stage rectangular weir coefficient 
    # Rec_Weir_Ex: 3rd stage rectangular weir exponent 
    # Rec_Weir_Length: 3rd stage rectangular weir length in feet 
    # Rec_WeirCrest_EL: 3rd stage rectangular weir crest elevation above pond bottom in feet 
    # Rec_Num_Weirs: number of weirs for 3rd stage rectangular weir
    # OS_BCWeir_Coeff: broad-crested weird coefficient for overflow spillway 
    # OS_Weir_Ex: weir exponent for overflow spillway
    # OS_Length: overflow spillway length in feet
    # OS_Crest_EL: crest elevation above pond bottom for overflow spillway in feet
    # Seepage_Bottom: seepage through pond bottom in in/hr
    # Seepage_Side: seepage through pon bottom in in/hr
    # length: length of inverted quadrilateral frustum in feet, for pond option 1
    # w1: w1 of inverted quadrilateral frustum in feet, for pond option 1
    # w2: w2 of inverted quadrilateral frustum in feet, for pond option 1
    # side_slope_z: side slope z of inverted quadrilateral frustum in feet, for pond option 1
    # bottom_slope: bottom slope of inverted quadrilateral frustum in feet, for pond option 1
    # Elev_Area: list of values elevation (ft-MSL) vs surface area (sq ft), for pond option 2


    # Calculate Unit Hydrograph
    unitHydrograph = computeSCSyntheticUnitHydrograph(lat, lon, AEP, CNModificationMethod, Area, Tc, RainfallDistributionCurve, PRF, CN, S, Ia)

    # Fixed Variables
    storm_duration = unitHydrograph[2]['storm_duration']
    burst_duration = 6
    max_depth = 10

    # Initialize output arrays
    pond_peak_inflow = []
    time_of_pond_peak_inflow = []
    pond_peak_outflow = []
    time_of_pond_peak_outflow = []
    pond_max_depth = []
    outflows = []

    # Pond options
    if pondOption == 1:
        if [x for x in (length, w1, w2, side_slope_z, bottom_slope) if x is None]:            
            raise Exception("Not all inputs for pond option 1 are present.")
        # Calculate Q, twoS_dtplusQ, Y for pond option one
        Q, twoS_dtplusQ, Y = calcPondOne(length, w1, w2, side_slope_z, bottom_slope, pond_bottom_elev, 
                                        Orif1_Coeff, Orif1_Dia, Orif1_CtrEL, Orif1_NumOpenings, 
                                        Orif2_Coeff, Orif2_Dia, Orif2_CtrEL, Orif2_NumOpenings, 
                                        Rec_Weir_Coeff, Rec_Weir_Ex, Rec_Weir_Length, Rec_WeirCrest_EL, Rec_Num_Weirs,
                                        OS_BCWeir_Coeff, OS_Weir_Ex, OS_Length, OS_Crest_EL,
                                        Seepage_Bottom, Seepage_Side,
                                        max_depth, burst_duration)
    else:    
        if Elev_Area is None:            
            raise Exception("Not all inputs for pond option 2 are present.")
        # Calculate Q, twoS_dtplusQ, Y for pond option two
        Q, twoS_dtplusQ, Y = calcPondTwo(Elev_Area, pond_bottom_elev,
                                        Orif1_Coeff, Orif1_Dia, Orif1_CtrEL, Orif1_NumOpenings, 
                                        Orif2_Coeff, Orif2_Dia, Orif2_CtrEL, Orif2_NumOpenings, 
                                        Rec_Weir_Coeff, Rec_Weir_Ex, Rec_Weir_Length, Rec_WeirCrest_EL, Rec_Num_Weirs,
                                        OS_BCWeir_Coeff, OS_Weir_Ex, OS_Length, OS_Crest_EL,
                                        Seepage_Bottom, Seepage_Side,
                                        max_depth, burst_duration)

    # Calculate outflow (Q2) for each storm duration
    for D in storm_duration:     # Loop through storm_duration
        # Initialize arrays used in 
        time = unitHydrograph[3]['time'] # pond_x hr(column B)
        inflow = unitHydrograph[3]['flow_' + str(D) + '_hour'] # pond_x hr (column C)
        i1plusi2 = [] # pond_x hr (column D)
        twoS_dtplusQ2 = [] # pond_x hr (column F)
        twoS_dtminusQ1 = [] # pond_x hr (column E)
        Q2 = [] # pond_x hr (column H) & D-hr Storm Pond Routing Results
        Y2 = [] # pond_x hr (column G)
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
                # Q2 & Y2
                if (twoS_dtplusQ2[counter]<twoS_dtplusQ[1]):
                    Q2.append(Q[0]+((Q[1]-Q[0])/(twoS_dtplusQ[1]-twoS_dtplusQ[0]))*(twoS_dtplusQ2[counter]-twoS_dtplusQ[0]))
                    Y2.append(Y[0]+((Y[1]-Y[0])/(twoS_dtplusQ[1]-twoS_dtplusQ[0]))*(twoS_dtplusQ2[counter]-twoS_dtplusQ[0]))
                elif (twoS_dtplusQ2[counter]<twoS_dtplusQ[2]):  
                    Q2.append(Q[1]+((Q[2]-Q[1])/(twoS_dtplusQ[2]-twoS_dtplusQ[1]))*(twoS_dtplusQ2[counter]-twoS_dtplusQ[1]))
                    Y2.append(Y[1]+((Y[2]-Y[1])/(twoS_dtplusQ[2]-twoS_dtplusQ[1]))*(twoS_dtplusQ2[counter]-twoS_dtplusQ[1]))
                elif (twoS_dtplusQ2[counter]<twoS_dtplusQ[3]):  
                    Q2.append(Q[2]+((Q[3]-Q[2])/(twoS_dtplusQ[3]-twoS_dtplusQ[2]))*(twoS_dtplusQ2[counter]-twoS_dtplusQ[2]))
                    Y2.append(Y[2]+((Y[3]-Y[2])/(twoS_dtplusQ[3]-twoS_dtplusQ[2]))*(twoS_dtplusQ2[counter]-twoS_dtplusQ[2]))
                elif (twoS_dtplusQ2[counter]<twoS_dtplusQ[4]): 
                    Q2.append(Q[3]+((Q[4]-Q[3])/(twoS_dtplusQ[4]-twoS_dtplusQ[3]))*(twoS_dtplusQ2[counter]-twoS_dtplusQ[3]))
                    Y2.append(Y[3]+((Y[4]-Y[3])/(twoS_dtplusQ[4]-twoS_dtplusQ[3]))*(twoS_dtplusQ2[counter]-twoS_dtplusQ[3]))
                elif (twoS_dtplusQ2[counter]<twoS_dtplusQ[5]):  
                    Q2.append(Q[4]+((Q[5]-Q[4])/(twoS_dtplusQ[5]-twoS_dtplusQ[4]))*(twoS_dtplusQ2[counter]-twoS_dtplusQ[4]))
                    Y2.append(Y[4]+((Y[5]-Y[4])/(twoS_dtplusQ[5]-twoS_dtplusQ[4]))*(twoS_dtplusQ2[counter]-twoS_dtplusQ[4]))
                elif (twoS_dtplusQ2[counter]<twoS_dtplusQ[6]):  
                    Q2.append(Q[5]+((Q[6]-Q[5])/(twoS_dtplusQ[6]-twoS_dtplusQ[5]))*(twoS_dtplusQ2[counter]-twoS_dtplusQ[5]))
                    Y2.append(Y[5]+((Y[6]-Y[5])/(twoS_dtplusQ[6]-twoS_dtplusQ[5]))*(twoS_dtplusQ2[counter]-twoS_dtplusQ[5]))
                elif (twoS_dtplusQ2[counter]<twoS_dtplusQ[7]):  
                    Q2.append(Q[6]+((Q[7]-Q[6])/(twoS_dtplusQ[7]-twoS_dtplusQ[6]))*(twoS_dtplusQ2[counter]-twoS_dtplusQ[6]))
                    Y2.append(Y[6]+((Y[7]-Y[6])/(twoS_dtplusQ[7]-twoS_dtplusQ[6]))*(twoS_dtplusQ2[counter]-twoS_dtplusQ[6]))
                elif (twoS_dtplusQ2[counter]<twoS_dtplusQ[8]): 
                    Q2.append(Q[7]+((Q[8]-Q[7])/(twoS_dtplusQ[8]-twoS_dtplusQ[7]))*(twoS_dtplusQ2[counter]-twoS_dtplusQ[7])) 
                    Y2.append(Y[7]+((Y[8]-Y[7])/(twoS_dtplusQ[8]-twoS_dtplusQ[7]))*(twoS_dtplusQ2[counter]-twoS_dtplusQ[7])) 
                elif (twoS_dtplusQ2[counter]<twoS_dtplusQ[9]):  
                    Q2.append(Q[8]+((Q[9]-Q[8])/(twoS_dtplusQ[9]-twoS_dtplusQ[8]))*(twoS_dtplusQ2[counter]-twoS_dtplusQ[8]))
                    Y2.append(Y[8]+((Y[9]-Y[8])/(twoS_dtplusQ[9]-twoS_dtplusQ[8]))*(twoS_dtplusQ2[counter]-twoS_dtplusQ[8]))  
                elif (twoS_dtplusQ2[counter]<twoS_dtplusQ[10]): 
                    Q2.append(Q[9]+((Q[10]-Q[9])/(twoS_dtplusQ[10]-twoS_dtplusQ[9]))*(twoS_dtplusQ2[counter]-twoS_dtplusQ[9])) 
                    Y2.append(Y[9]+((Y[10]-Y[9])/(twoS_dtplusQ[10]-twoS_dtplusQ[9]))*(twoS_dtplusQ2[counter]-twoS_dtplusQ[9])) 
                else:
                    Q2.append('error') 
                    Y2.append('error')
            counter = counter + 1
        outflows.append(Q2)
        
        index_pond_peak_inflow = np.argmax(inflow)
        pond_peak_inflow.append((inflow[index_pond_peak_inflow]))
        time_of_pond_peak_inflow.append(time[index_pond_peak_inflow])
        index_pond_peak_outflow = np.argmax(Q2)
        pond_peak_outflow.append(Q2[index_pond_peak_outflow])
        time_of_pond_peak_outflow.append(time[index_pond_peak_outflow])
        pond_max_depth.append(max(Y2))
        # print('time:', time)
        # print('inflow:', inflow)
        # print('i1plusi2:', i1plusi2)
        # print('twoS_dtminusQ1:', twoS_dtminusQ1)
        # print('twoS_dtplusQ2:', twoS_dtplusQ2)
        # print('Q2:', Q2)
        # print('Y2:', Y2)
    
    # Corresponds red arrow in the "D-hr Storm Pond Results" sheet
    index_max_peak_outflow = np.argmax(pond_peak_outflow)
    max_peak_outflow = storm_duration[index_max_peak_outflow]

    runoff_and_ponding_results = {
        "storm_duration": unitHydrograph[2]['storm_duration'],
        "rainfall_depth": unitHydrograph[2]['rainfall_depth'],
        "CN_adjusted_for_rainfall_duration": unitHydrograph[2]['CN_adjusted_for_rainfall_duration'],  
        "runoff_volume_Q_CN": unitHydrograph[2]['runoff_volume_Q_CN'],
        "pond_peak_inflow": pond_peak_inflow, # max of inflow (pond_x hr 19)
        "time_of_pond_peak_inflow": time_of_pond_peak_inflow, # time of max inflow (pond_x hr k20)
        "pond_peak_outflow": pond_peak_outflow, # max of outflow (pond_x hr k22)
        "time_of_pond_peak_outflow": time_of_pond_peak_outflow, # time of max outflow (pond_x hr k23)
        "max_peak_outflow_storm_duration": max_peak_outflow, # storm duration with max peak outflow
        "max_depth": pond_max_depth # max_depth (pond_x hr k24)
    }

    pond_inflow_and_outflow_ordinates = {
        "time": unitHydrograph[3]['time'],
        "inflow_1_hour": unitHydrograph[3]['flow_1_hour'],
        "outflow_1_hour": outflows[0],
        "inflow_2_hour": unitHydrograph[3]['flow_2_hour'],
        "outflow_2_hour": outflows[1],
        "inflow_3_hour": unitHydrograph[3]['flow_3_hour'],
        "outflow_3_hour": outflows[2],
        "inflow_6_hour": unitHydrograph[3]['flow_6_hour'],
        "outflow_6_hour": outflows[3],
        "inflow_12_hour": unitHydrograph[3]['flow_12_hour'],
        "outflow_12_hour": outflows[4],
        "inflow_24_hour": unitHydrograph[3]['flow_24_hour'],
        "outflow_24_hour": outflows[5]
    }

    # print(runoff_and_ponding_results)
    # print(pond_inflow_and_outflow_ordinates)

    return runoff_and_ponding_results, pond_inflow_and_outflow_ordinates


# Pond option two calculations
def calcPondTwo(Elev_Area, pond_bottom_elev,
                Orif1_Coeff, Orif1_Dia, Orif1_CtrEL, Orif1_NumOpenings, 
                Orif2_Coeff, Orif2_Dia, Orif2_CtrEL, Orif2_NumOpenings, 
                Rec_Weir_Coeff, Rec_Weir_Ex, Rec_Weir_Length, Rec_WeirCrest_EL, Rec_Num_Weirs,
                OS_BCWeir_Coeff, OS_Weir_Ex, OS_Length, OS_Crest_EL,
                Seepage_Bottom, Seepage_Side,
                max_depth, burst_duration):
    
    if pond_bottom_elev != Elev_Area[0][0]:
        raise Exception("Bottom pond elevation must be the same as the first elevation input.")
        
    # Initialize arrays used in 
    Q = [] # Pond_X hr, 2S_Dt, Y-Q (2) 
    S = [] # Pond_X, 2S_Dt+Q, Y-S (2)
    A = [] # Y-S (2)
    change_S = [] # Pond_X hr
    twoS_dtplusQ = [] # Y-S (2)
    Y = [] # Pond_X hr, 2S_Dt, Y-Q (2)
    h = [] # 2S_Dt+Q, Y-Q (2), Y-S (2)
    # Calculate values in Y-Q (2) sheet
    Orif1_A = 3.14159*((Orif1_Dia/12)**2)/4
    Orif2_A = 3.14159*((Orif2_Dia/12)**2)/4
    for y in range(0, max_depth):
        h.append(Elev_Area[y][0])
        Y.append(h[y]-pond_bottom_elev)

        # First Stage Orifice Total Flow
        Orif1_H = max(0,Y[y]-Orif1_CtrEL)
        Orif1_Q = max(0,Orif1_Coeff*Orif1_A*math.sqrt(64.4*Orif1_H))   
        Orif1_total_flow = Orif1_NumOpenings*Orif1_Q
        # Second Stage Orifice Total Flow
        Orif2_H = max(0,Y[y]-Orif2_CtrEL)
        Orif2_Q = max(0,Orif2_Coeff*Orif2_A*math.sqrt(64.4*Orif2_H)) 
        Orif2_total_flow = Orif2_NumOpenings*Orif2_Q
        # Upper Stage Rectangular Weir Total Flow
        Rec_Weir_H = max(0,Y[y]-Rec_WeirCrest_EL)
        Rec_Single_Weir_Q = Rec_Weir_Coeff*Rec_Weir_Length*Rec_Weir_H**Rec_Weir_Ex
        Rec_Stage_total_flow = Rec_Single_Weir_Q*Rec_Num_Weirs
        # Overflow Spillway Q
        OS_H = max(0,Y[y]-OS_Crest_EL)
        OS_Q = OS_BCWeir_Coeff*OS_Length*OS_H**OS_Weir_Ex
        # Seepage in cfs
        if y == 0:
            A1 = Elev_Area[0][1]
            A.append(A1)
        else:
            A.append(Elev_Area[y][1])
        if y == 0:
            Seepage_Bottom_CFS = 0
            Seepage_Side_CFS = 0
        else:
            Seepage_Bottom_CFS = A1*Seepage_Bottom/(12*3600)
            Seepage_Side_CFS = (A[y]-A1)*Seepage_Side/(12*3600)
        
        # Calculate Q in 2S_Dt+Q & Pond_X hr sheets
        Outflow_Q = Orif1_total_flow+Orif2_total_flow+Rec_Stage_total_flow+OS_Q+Seepage_Bottom_CFS+Seepage_Side_CFS
        Q.append(Outflow_Q) 
        # Calculate S in 2S_Dt+Q & Pond_X hr sheets; Calculate change in S from Y-S (2) sheet 
        if y == 0:
            S.append(0)
            change_S.append(0)
        else:
            change_S.append(((A[y-1]+A[y])/2)*(Y[y] - Y[y-1])) 
            S.append(S[y-1] + change_S[y])
        # Calculate 2S/dt+Q in 2S_Dt+Q & Pond_X hr sheets
        twoS_dtplusQ.append((2*S[y]/(60*burst_duration))+Q[y])

    # print('Q:', Q) 
    # print('S:', S)
    # print('twoS_dtplusQ:', twoS_dtplusQ)
    # print('Y:', Y)
    # print('H:', h)

    return(Q, twoS_dtplusQ, Y)


# Pond option one calculations
def calcPondOne(length, w1, w2, side_slope_z, bottom_slope, pond_bottom_elev, 
                Orif1_Coeff, Orif1_Dia, Orif1_CtrEL, Orif1_NumOpenings, 
                Orif2_Coeff, Orif2_Dia, Orif2_CtrEL, Orif2_NumOpenings, 
                Rec_Weir_Coeff, Rec_Weir_Ex, Rec_Weir_Length, Rec_WeirCrest_EL, Rec_Num_Weirs,
                OS_BCWeir_Coeff, OS_Weir_Ex, OS_Length, OS_Crest_EL,
                Seepage_Bottom, Seepage_Side, max_depth, burst_duration):
    # Initialize arrays used in 
    Q = [] # Pond_X hr, 2S_Dt, Y-Q (1) 
    S = [] # Pond_X, 2S_Dt+Q, Y-S (1)
    Total_L = [] # Y-S (1)
    Total_W1 = [] # Y-S (1)
    Total_W2 = [] # Y-S (1)
    A = [] # Y-S (1)
    change_S = [] # Pond_X hr
    twoS_dtplusQ = [] # Y-S (1)
    Y = [] # Pond_X hr, 2S_Dt, Y-Q (1)
    h = [] # 2S_Dt+Q, Y-Q (1), Y-S (1)
    # Calculate values in Y-Q (1) sheet
    Orif1_A = 3.14159*((Orif1_Dia/12)**2)/4
    Orif2_A = 3.14159*((Orif2_Dia/12)**2)/4
    for y in range(0, max_depth+1):
        
        if y == 0:
            h.append(pond_bottom_elev)
        elif y == 1:
            h.append(pond_bottom_elev+length*bottom_slope/100)
        elif y == 2 or y == 3 or y == 4 or y == 5 or y == 6 or y == 7:
            h.append(min(h[y-1]+max_depth/10, pond_bottom_elev+8))
        else:
            h.append(min(h[y-1]+max_depth/10, pond_bottom_elev+10))

        Y.append(h[y]-pond_bottom_elev)

        # First Stage Orifice Total Flow
        Orif1_H = max(0,Y[y]-Orif1_CtrEL)
        Orif1_Q = max(0,Orif1_Coeff*Orif1_A*math.sqrt(64.4*Orif1_H))   
        Orif1_total_flow = Orif1_NumOpenings*Orif1_Q
        # Second Stage Orifice Total Flow
        Orif2_H = max(0,Y[y]-Orif2_CtrEL)
        Orif2_Q = max(0,Orif2_Coeff*Orif2_A*math.sqrt(64.4*Orif2_H)) 
        Orif2_total_flow = Orif2_NumOpenings*Orif2_Q
        # Upper Stage Rectangular Weir Total Flow
        Rec_Weir_H = max(0,Y[y]-Rec_WeirCrest_EL)
        Rec_Single_Weir_Q = Rec_Weir_Coeff*Rec_Weir_Length*Rec_Weir_H**Rec_Weir_Ex
        Rec_Stage_total_flow = Rec_Single_Weir_Q*Rec_Num_Weirs
        # Overflow Spillway Q
        OS_H = max(0,Y[y]-OS_Crest_EL)
        OS_Q = OS_BCWeir_Coeff*OS_Length*OS_H**OS_Weir_Ex
        # Seepage in cfs
        if y == 0:
            Total_L.append(length+2*bottom_slope*(h[y]-pond_bottom_elev))
            Total_W1.append(w1+2*side_slope_z*(h[y]-pond_bottom_elev))
            Total_W2.append(w2+2*side_slope_z*(h[y]-pond_bottom_elev))
            A1 = Total_L[y]*(Total_W1[y]+Total_W2[y])/2
            A.append(A1)
        else:
            Total_L.append(Total_L[y-1]+2*side_slope_z*(h[y] - h[y-1])) 
            Total_W1.append(Total_W1[y-1]+2*side_slope_z*(h[y] - h[y-1]))
            Total_W2.append(Total_W2[y-1]+2*side_slope_z*(h[y] - h[y-1]))
            A.append(Total_L[y]*(Total_W1[y]+Total_W2[y])/2)

        if y == 0:
            Seepage_Bottom_CFS = 0
            Seepage_Side_CFS = 0
        else:
            Seepage_Bottom_CFS = A1*Seepage_Bottom/(12*3600)
            Seepage_Side_CFS = (A[y]-A1)*Seepage_Side/(12*3600)
        
        # Calculate Q in 2S_Dt+Q & Pond_X hr sheets
        Outflow_Q = Orif1_total_flow+Orif2_total_flow+Rec_Stage_total_flow+OS_Q+Seepage_Bottom_CFS+Seepage_Side_CFS
        Q.append(Outflow_Q) 
        # Calculate S in 2S_Dt+Q & Pond_X hr sheets; Calculate change in S from Y-S (1) sheet 
        if y == 0:
            S.append(0)
            change_S.append(0)
        else:
            change_S.append(((A[y-1]+A[y])/2)*(Y[y] - Y[y-1])) 
            S.append(S[y-1] + change_S[y])
        # Calculate 2S/dt+Q in 2S_Dt+Q & Pond_X hr sheets
        twoS_dtplusQ.append((2*S[y]/(60*burst_duration))+Q[y])

    # print('Q:', Q) 
    # print('S:', S)
    # print('twoS_dtplusQ:', twoS_dtplusQ)
    # print('Y:', Y)
    # print('H:', h)

    return(Q, twoS_dtplusQ, Y)
        

