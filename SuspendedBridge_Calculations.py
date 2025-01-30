import Basic_Scripts as BS
import numpy as np
import math

def SpanHeight_Calculations():
    #Design span calculations
    NominalSpan = Survey_Distance + FoundationShift_Right + FoundationShift_Left
    DesignSpan = NominalSpan
    if CableAnchorage_DrumType:
        DesignSpan = NominalSpan + (0.25 * 2)
    else:
        DesignSpan = NominalSpan + (0.5 * 2)

    #Height Calculations and checks
    ElevationDifference = abs(MainCableEle_Left - MainCableEle_Right)

    #Check: The lowest point of the parabola of the inclined bridge must remain inside the span for all loading cases. For dead load case:
    hTolerance = DesignSpan/14

    LowestPoint_Check = True #The value true indicates for the fasses
    if hTolerance < ElevationDifference:
        LowestPoint_Check = False

    return DesignSpan,LowestPoint_Check, hTolerance, ElevationDifference


#Preliminary data (All units needs to be in meters, degree and kN
Survey_Distance = 107.76       #Refers to the span that was proposed during the survey period
FoundationShift_Right = 7.75   #Refers to the foundation location proposed after survey and other aspects (Right Bank)
FoundationShift_Left = 16.59   #Refers to the foundation location proposed after survey and other aspects (Left Bank)

#Cables elevation
MainCableEle_Right = 110.6
MainCableEle_Left = 105.6
WindguyEle_RightUp = 102.6
WindguyEle_RightDown = 102.3
WindguyEle_LeftUp = 97.5
WindguyEle_LeftDown = 96.4
HFL_Elevation = 90


CableAnchorage_DrumType = True
CableAnchorage_OpenType = True

#Step 1
DesignSpan,LowestPoint_Check, hTolerance, ElevationDifference = SpanHeight_Calculations()


#Step 2
StandardExcel_Path = r"C:\Users\Acer\Documents\Suspension Bridge Design\Design Standards.xlsx"
Sheetname = "Sheet1"
TableName = ['Table 7.3.1']
Table_List = BS.ExcelTable_extractor(StandardExcel_Path, Sheetname, TableName)

#Step 3 Precalculations of Cable tensions, Handrail cable and main cables
def preCalculation_TMCHC(DesignSpan,table):
    Tmax_Approx = 11 * DesignSpan           #Magnitude in kN
    header = table[0]
    rows = table[1:]

    # Dynamically find the index of the "Permissible Load (kN)" column
    normalized_header = [str(col).strip().lower() for col in header]
    normalized_SearchKeyword = str('Tpermissible (kN)').strip().lower()

    try:
        permissible_load_index = next((i for i, value in enumerate(header) if normalized_SearchKeyword in value.lower()), None)

    except ValueError:
        print("The column 'Permissible Load (kN)' was not found in the header. Setting as 5")
        permissible_load_index = 5

    if permissible_load_index is not None:
        result_row = next((row for row in rows if row[permissible_load_index] > Tmax_Approx), None)

    MCHC_Approx= dict((zip(header, result_row)))

    #Approximate load and Metallic area
    HeaderstringMCDia = "Main Cables Diameter"
    HeaderstringMCNo = "Main Cables Number"
    HeaderstringHCDia = "Handrail Cables Diameter"


    Required_MCDia_index = next((i for i, value in enumerate(header) if HeaderstringMCDia.lower() in value.lower()), None)
    Required_MCNo_index = next((i for i, value in enumerate(header) if HeaderstringMCNo.lower() in value.lower()), None)
    Required_HCDia_index = next((i for i, value in enumerate(header) if HeaderstringHCDia.lower() in value.lower()), None)

    Required_MCDia = result_row[Required_MCDia_index]
    Required_MCNo = result_row[Required_MCNo_index]
    Required_HCDia = result_row[Required_HCDia_index]
    #-------------------------------------------------------------------------------------------------------------------

    #For Metallic Area
    Sheetname = "Sheet1"
    TableName = ['Table 7.3.2']
    AreaTable = BS.ExcelTable_extractor(StandardExcel_Path, Sheetname, TableName)[0]

    Area_header = AreaTable[0]
    Area_rows = AreaTable[1:]

    HeadingText = "Metallic Area"
    DiaHeader = "Nominal Diameter"
    LoadHeader = "Approximate Load"
    MetallicArea_Index = next((i for i, value in enumerate(Area_header) if HeadingText.lower() in value.lower()), None)
    NominalDia_Index = next((i for i, value in enumerate(Area_header) if DiaHeader.lower() in value.lower()), None)
    ApproxLoad_Index = next((i for i, value in enumerate(Area_header) if LoadHeader.lower() in value.lower()), None)


    # MetallicArea, ApproxLoad  = next((value[MetallicArea_Index], value[ApproxLoad_Index] for i, value in enumerate(AreaTable) if Required_MCDia == value[NominalDia_Index], None)
    MCMetallicArea, MCApproxLoad = next(
        ((value[MetallicArea_Index], value[ApproxLoad_Index]) for value in Area_rows if
         Required_MCDia == value[NominalDia_Index]),
        None
    )

    HCMetallicArea, HCApproxLoad = next(
        ((value[MetallicArea_Index], value[ApproxLoad_Index]) for value in Area_rows if
         Required_HCDia == value[NominalDia_Index]),
        None
    )
    MetallicAreaC_All = Required_MCNo * MCMetallicArea + 2 * HCMetallicArea
    MCHCLoad_Dead = Required_MCNo * MCApproxLoad + 2 * HCApproxLoad

    return Tmax_Approx, MCHC_Approx,MetallicAreaC_All, MCHCLoad_Dead

Tmax_Approx, MCHC_Approx,MetallicAreaC_All, MCHCLoad_Dead = preCalculation_TMCHC(DesignSpan,Table_List[0])


#Step 4 WindGuy Approximation
def TensionCalculation(w, l, bw, V):
    return (w * l * l / (8 * bw)) * (1 + (2 * bw / V) ** 2) ** 0.5

def WindGuy_Approximation(DesignSpan):
    #Approx windguy sag = DesignSpan/8 to DesignSpan/10
    bw = DesignSpan/9               #windguySag_Approx

    #Approximate windguy cable Tension
    w = 0.5     #wind load taken as 0.5 kN/m
    l = DesignSpan
    V = DesignSpan/2            # V = (l/ 2 ± 1.20 i), here V taken as l/2 only


    Twindguy_LR = TensionCalculation(w, l, bw, V) #Tension on kN
    # Twindguy_LR = (w*l*l/(8*bw)) * (1+(2*bw/V)**2)**0.5

    #No and Dia of windguy Cables
    Table_List = BS.ExcelTable_extractor(Excel_Path = r"C:\Users\Acer\Documents\Suspension Bridge Design\Design Standards.xlsx", Sheetname = "Sheet1", TableName = ['Table 7.3.2'])
    WindGuy_Dia = BS.Table_Scraping(Table_List[0], SearchHeading="Permissible Load", SearchValue=Twindguy_LR, TargetHeading="Nominal Diameter",
                               SearchValueMultiplier=1, JustGreater=True)

    return WindGuy_Dia, Twindguy_LR

WindGuy_Dia, Twindguy_LR = WindGuy_Approximation(DesignSpan)


#Step 5:Dead Load Design

def betaCalc (bf, h, DesignSpan):
    return math.degrees(math.atan((4*bf+h)/DesignSpan))
def TensionCalc(gf, DesignSpan, bf, beta1fmax):
    return gf*DesignSpan*DesignSpan/(8*bf*math.cos(math.radians(beta1fmax)))

DeadLoad = 1.028
HoistingLoad = 0.288
FullLoad = 4.405
def Dead_Load_Design( DesignSpan, ElevationDifference, Tpermissible, LiveLoad = 0.00, HoistingLoad = 0.288, DeadLoad = 1.028):

    def beta_Tmax(bf, h, l, gf):
        beta1fmax = betaCalc (bf, h, DesignSpan)
        Tmax = TensionCalc(gf, DesignSpan, bf, beta1fmax)
        return beta1fmax, Tmax


    if LiveLoad == 0.00:
        LiveLoad = 3 + 50 / DesignSpan

    gf = DeadLoad + LiveLoad

    #Cable sag range
    bdmax = (DesignSpan/19) - (ElevationDifference/4)
    bdmin = (DesignSpan/23) - (ElevationDifference/4)

    #For full load sag

    bfmax = 1.22*bdmax
    beta1fmax, Tbfmax = beta_Tmax(bfmax, ElevationDifference, DesignSpan, gf)

    bfmin = 1.22*bdmin
    beta1fmin, Tbfmin = beta_Tmax(bfmin, ElevationDifference, DesignSpan, gf)

    #Tmax Checks
    bfmaxCheck = True
    bfminCheck = True

    if Tbfmax > Tpermissible:
        bfmaxCheck = False
    if Tbfmin > Tpermissible:
        bfminCheck = False

    Table_List = BS.ExcelTable_extractor(Excel_Path = r"C:\Users\Acer\Documents\Suspension Bridge Design\Design Standards.xlsx", Sheetname = "Sheet1", TableName = ['Table 7.3.1'])

    TpermCheck1 = BS.Table_Scraping(Table_List[0], SearchHeading="Tpermissible", SearchValue=Tbfmax,
                      TargetHeading="Tpermissible",
                      SearchValueMultiplier=1, JustGreater=True, wholeRow=1)
    TpermCheck2 = BS.Table_Scraping(Table_List[0], SearchHeading="Tpermissible", SearchValue=Tbfmin,
                      TargetHeading="Tpermissible",
                      SearchValueMultiplier=1, JustGreater=True, wholeRow=1)

    print(beta1fmin, gf, bfmin, bfmin, ElevationDifference, DesignSpan, gf, Tpermissible, bfminCheck, bfmaxCheck, TpermCheck2, TpermCheck1)
Tpermissible = MCHC_Approx[ 'Tpermissible (kN)']

Dead_Load_Design( DesignSpan, ElevationDifference,Tpermissible, LiveLoad = 0.00, HoistingLoad = HoistingLoad, DeadLoad = DeadLoad)

#Now in this phase the value of h abd bd can be chosen accordingly for stability, economic design but it must be under permissible limits
#Adopted values for the further proceedings
E = 110
bd = 5.6
ElevationDifference = 4.5
Tmax = 1466
H2 = 105.6
H1 = 110.1
Beta1d = betaCalc (bd, ElevationDifference, DesignSpan)
Beta2d = betaCalc (bd, -ElevationDifference, DesignSpan)
# print(Beta1d, Beta2d)

def ed_Distance(DesignSpan, ElevationDifference, bd):
    return (DesignSpan/2) * (1 + ElevationDifference/(4*bd))

def foundationSag (bd, ElevationDifference):
    return bd + (ElevationDifference/2) + (ElevationDifference*ElevationDifference/(16*bd))

# print(ed_Distance(DesignSpan, ElevationDifference, bd), foundationSag (bd, ElevationDifference))

def CableLength(DesignSpan, ElevationDifference, bd):
    return DesignSpan * (1 + 0.5*(ElevationDifference/DesignSpan)**2 + (8/3)*(bd/DesignSpan)**2)
cableLength = CableLength(DesignSpan, ElevationDifference, bd)
# print(CableLength(DesignSpan, ElevationDifference, bd))

def ConstantFactor(cableLength, E, MetallicAreaC_All, DesignSpan):
    return 64*E*MetallicAreaC_All/(3*cableLength*DesignSpan**3)
constantFactor = ConstantFactor(cableLength, E, MetallicAreaC_All, DesignSpan)
# print(ConstantFactor(cableLength, E, MetallicAreaC_All, DesignSpan))

def SagIteration(bd, b_, constantFactor, DeadLoad, HoistORfullLoad, MulFactor):
    b_ = MulFactor * b_
    g_ = constantFactor * b_ *(b_**2 - bd**2) + b_* DeadLoad/bd
    newB_ = bd + (b_ - bd) *(HoistORfullLoad - DeadLoad) / (g_ - DeadLoad)
    delG_ = HoistORfullLoad - g_

    return b_, g_,newB_,  abs(delG_)


#Hoisting load sag by iteration
delG_ = 1
bdHoisting = bd
MulFactor = 0.93
while delG_ > 0.00001:
    b_, g_,newB_,  delG_ = SagIteration(bd, bdHoisting, constantFactor, DeadLoad, HoistingLoad, MulFactor)
    MulFactor = 1
    bdHoisting = newB_
print(b_, g_, newB_, delG_, "Hoisting Case")

#Full load sag by iteration
delG_ = 1
bdHoisting = bd
MulFactor = 1.22
while delG_ > 0.0001:
    b_, g_,newB_,  delG_ = SagIteration(bd, bdHoisting, constantFactor, DeadLoad, FullLoad, MulFactor)
    MulFactor = 1
    bdHoisting = newB_
print(b_, g_, newB_, delG_, "Full Load Case")


#Step 7
def TensionCalculation(gf, l, b, ElevationDifference):
    return (gf * l * l / (8 * b)) * (1 + ((4 * b + ElevationDifference) / l) ** 2) ** 0.5
TensionFullLoad = TensionCalculation(FullLoad, DesignSpan, newB_, ElevationDifference)
print(TensionFullLoad)

#Step 8
FactorOfSafety = BS.dictValuefromTitlekey(MCHC_Approx,"Tbreak")/TensionFullLoad
print(FactorOfSafety)