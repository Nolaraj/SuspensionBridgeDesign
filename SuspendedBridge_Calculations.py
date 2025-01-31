import Basic_Scripts as BS
import numpy as np
import math

class SuspendedBridge:
    def __init__(self):
        # Initialize all input parameters
        self.Survey_Distance = 107.76  # Proposed span during survey (meters)
        self.FoundationShift_Right = 7.75  # Foundation shift (Right Bank)
        self.FoundationShift_Left = 16.59  # Foundation shift (Left Bank)
        self.MainCableEle_Right = 110.6  # Main cable elevation (Right)
        self.MainCableEle_Left = 105.6  # Main cable elevation (Left)
        self.WindguyEle_RightUp = 102.6  # Windguy elevation upstream (Right)
        self.WindguyEle_RightDown = 102.3  # Windguy elevation downstream (Right)
        self.WindguyEle_LeftUp = 97.5  # Windguy elevation upstream (Left)
        self.WindguyEle_LeftDown = 96.4  # Windguy elevation downstream (Left)

        self.HFL_Elevation = 90  # High Flood Level elevation
        self.CableAnchorage_DrumType = True  # Cable anchorage type
        self.CableAnchorage_OpenType = True  # Cable anchorage type
        self.StandardExcel_Path = r"C:\Users\Acer\Documents\Suspension Bridge Design\Design Standards.xlsx"
        self.DeadLoad = 1.028  # Dead load (kN/m)
        self.HoistingLoad = 0.288  # Hoisting load (kN/m)
        self.FullLoad = 4.405  # Full load (kN/m)

    def SpanHeight_Calculations(self):
        # Design span calculations
        NominalSpan = self.Survey_Distance + self.FoundationShift_Right + self.FoundationShift_Left
        print(NominalSpan, "hdflalfja")
        DesignSpan = NominalSpan
        if self.CableAnchorage_DrumType:
            DesignSpan = NominalSpan + (0.25 * 2)
        else:
            DesignSpan = NominalSpan + (0.5 * 2)

        # Height calculations and checks
        ElevationDifference = abs(self.MainCableEle_Left - self.MainCableEle_Right)
        hTolerance = DesignSpan / 14  # Tolerance for the lowest point of the parabola
        LowestPoint_Check = hTolerance >= ElevationDifference  # Check if the lowest point is within the span

        return DesignSpan, LowestPoint_Check, hTolerance, ElevationDifference

    def preCalculation_TMCHC(self, DesignSpan, table):
        # Approximate maximum tension
        Tmax_Approx = 11 * DesignSpan  # Magnitude in kN
        header = table[0]
        rows = table[1:]

        # Find the index of the "Permissible Load (kN)" column
        permissible_load_index = next((i for i, value in enumerate(header) if 'Tpermissible (kN)' in value), None)
        if permissible_load_index is None:
            print("The column 'Permissible Load (kN)' was not found in the header. Setting as 5")
            permissible_load_index = 5

        # Find the row where permissible load exceeds Tmax_Approx
        result_row = next((row for row in rows if row[permissible_load_index] > Tmax_Approx), None)
        MCHC_Approx = dict(zip(header, result_row))

        # Find required diameters and numbers for main and handrail cables
        Required_MCDia_index = next((i for i, value in enumerate(header) if "Main Cables Diameter" in value), None)
        Required_MCNo_index = next((i for i, value in enumerate(header) if "Main Cables Number" in value), None)
        Required_HCDia_index = next((i for i, value in enumerate(header) if "Handrail Cables Diameter" in value), None)

        Required_MCDia = result_row[Required_MCDia_index]
        Required_MCNo = result_row[Required_MCNo_index]
        Required_HCDia = result_row[Required_HCDia_index]

        # Extract metallic area and approximate load
        AreaTable = BS.ExcelTable_extractor(self.StandardExcel_Path, "Sheet1", ['Table 7.3.2'])[0]
        Area_header = AreaTable[0]
        Area_rows = AreaTable[1:]

        HeadingText = "Metallic Area"
        DiaHeader = "Nominal Diameter"
        LoadHeader = "Approximate Load"
        MetallicArea_Index = next((i for i, value in enumerate(Area_header) if HeadingText.lower() in value.lower()),
                                  None)
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

        return Tmax_Approx, MCHC_Approx, MetallicAreaC_All, MCHCLoad_Dead

    def WindGuy_Approximation(self, DesignSpan):
        # Approximate windguy sag
        bw = DesignSpan / 9  # Windguy sag approximation

        # Approximate windguy cable tension
        w = 0.5  # Wind load (kN/m)
        l = DesignSpan
        V = DesignSpan / 2  # Vertical distance

        Twindguy_LR = (w * l * l / (8 * bw)) * (1 + (2 * bw / V) ** 2) ** 0.5  # Tension in kN

        # Find windguy cable diameter
        Table_List = BS.ExcelTable_extractor(self.StandardExcel_Path, "Sheet1", ['Table 7.3.2'])
        WindGuy_Dia = BS.Table_Scraping(Table_List[0], SearchHeading="Permissible Load", SearchValue=Twindguy_LR,
                                        TargetHeading="Nominal Diameter", SearchValueMultiplier=1, JustGreater=True)

        return WindGuy_Dia, Twindguy_LR

    def Dead_Load_Design(self, DesignSpan, ElevationDifference, Tpermissible, LiveLoad=0.00, HoistingLoad=0.288, DeadLoad=1.028):
        def beta_Tmax(bf, h, l, gf):
            beta1fmax = math.degrees(math.atan((4 * bf + h) / l))
            Tmax = (gf * l * l / (8 * bf)) * (1 + ((4 * bf + h) / l) ** 2) ** 0.5
            return beta1fmax, Tmax

        if LiveLoad == 0.00:
            LiveLoad = 3 + 50 / DesignSpan

        gf = DeadLoad + LiveLoad

        # Cable sag range
        bdmax = (DesignSpan / 19) - (ElevationDifference / 4)
        bdmin = (DesignSpan / 23) - (ElevationDifference / 4)

        # For full load sag
        bfmax = 1.22 * bdmax
        beta1fmax, Tbfmax = beta_Tmax(bfmax, ElevationDifference, DesignSpan, gf)

        bfmin = 1.22 * bdmin
        beta1fmin, Tbfmin = beta_Tmax(bfmin, ElevationDifference, DesignSpan, gf)

        # Tmax checks
        bfmaxCheck = Tbfmax <= Tpermissible
        bfminCheck = Tbfmin <= Tpermissible

        # Check permissible tension
        Table_List = BS.ExcelTable_extractor(self.StandardExcel_Path, "Sheet1", ['Table 7.3.1'])
        TpermCheck1 = BS.Table_Scraping(Table_List[0], SearchHeading="Tpermissible", SearchValue=Tbfmax,
                                        TargetHeading="Tpermissible", SearchValueMultiplier=1, JustGreater=True, wholeRow=1)
        TpermCheck2 = BS.Table_Scraping(Table_List[0], SearchHeading="Tpermissible", SearchValue=Tbfmin,
                                        TargetHeading="Tpermissible", SearchValueMultiplier=1, JustGreater=True, wholeRow=1)

        print(beta1fmin, gf, bfmin, bfmin, ElevationDifference, DesignSpan, gf, Tpermissible, bfminCheck, bfmaxCheck, TpermCheck2, TpermCheck1)

    def run(self):
        # Step 1: Span and height calculations
        DesignSpan, LowestPoint_Check, hTolerance, ElevationDifference = self.SpanHeight_Calculations()

        # Step 2: Extract table data
        Table_List = BS.ExcelTable_extractor(self.StandardExcel_Path, "Sheet1", ['Table 7.3.1'])

        # Step 3: Pre-calculate cable tensions
        Tmax_Approx, MCHC_Approx, MetallicAreaC_All, MCHCLoad_Dead = self.preCalculation_TMCHC(DesignSpan, Table_List[0])

        # Step 4: Windguy approximation
        WindGuy_Dia, Twindguy_LR = self.WindGuy_Approximation(DesignSpan)

        # Step 5: Dead load design
        Tpermissible = MCHC_Approx['Tpermissible (kN)']
        self.Dead_Load_Design(DesignSpan, ElevationDifference, Tpermissible)

        # Step 6: Sag iteration for hoisting and full load
        bd = 5.6  # Adopted value for further proceedings
        E = 110  # Modulus of elasticity
        cableLength = self.CableLength(DesignSpan, ElevationDifference, bd)
        constantFactor = self.ConstantFactor(cableLength, E, MetallicAreaC_All, DesignSpan)

        # Hoisting load sag iteration
        delG_ = 1
        bdHoisting = bd
        MulFactor = 0.93
        while delG_ > 0.00001:
            b_, g_, newB_, delG_ = self.SagIteration(bd, bdHoisting, constantFactor, self.DeadLoad, self.HoistingLoad, MulFactor)
            MulFactor = 1
            bdHoisting = newB_
        print(b_, g_, newB_, delG_, "Hoisting Case")

        # Full load sag iteration
        delG_ = 1
        bdHoisting = bd
        MulFactor = 1.22
        while delG_ > 0.0001:
            b_, g_, newB_, delG_ = self.SagIteration(bd, bdHoisting, constantFactor, self.DeadLoad, self.FullLoad, MulFactor)
            MulFactor = 1
            bdHoisting = newB_
        print(b_, g_, newB_, delG_, "Full Load Case")

        # Step 7: Tension calculation for full load
        TensionFullLoad = self.TensionCalculation(self.FullLoad, DesignSpan, newB_, ElevationDifference)
        print(TensionFullLoad)

        # Step 8: Factor of safety
        FactorOfSafety = BS.dictValuefromTitlekey(MCHC_Approx, "Tbreak") / TensionFullLoad
        print(FactorOfSafety)

    def CableLength(self, DesignSpan, ElevationDifference, bd):
        return DesignSpan * (1 + 0.5 * (ElevationDifference / DesignSpan) ** 2 + (8 / 3) * (bd / DesignSpan) ** 2)

    def ConstantFactor(self, cableLength, E, MetallicAreaC_All, DesignSpan):
        return 64 * E * MetallicAreaC_All / (3 * cableLength * DesignSpan ** 3)

    def SagIteration(self, bd, b_, constantFactor, DeadLoad, HoistORfullLoad, MulFactor):
        b_ = MulFactor * b_
        g_ = constantFactor * b_ * (b_ ** 2 - bd ** 2) + b_ * DeadLoad / bd
        newB_ = bd + (b_ - bd) * (HoistORfullLoad - DeadLoad) / (g_ - DeadLoad)
        delG_ = HoistORfullLoad - g_
        return b_, g_, newB_, abs(delG_)

    def TensionCalculation(self, gf, l, b, ElevationDifference):
        return (gf * l * l / (8 * b)) * (1 + ((4 * b + ElevationDifference) / l) ** 2) ** 0.5


# Run the design
# if __name__ == "__main__":
#     bridge_design = SuspendedBridge()
#     bridge_design.run()