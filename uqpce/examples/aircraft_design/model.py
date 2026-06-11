import openmdao.api as om
from aero import AeroDicipline
from BreguetRangeComp import BreguetRangeComp
from propAndCost import Propulsion
from propAndCost import EngineWeight
from propAndCost import DOC
from WeightsComp import Weights_Struct
#from mass import Residual
from total_mass import MassTotal


class CoupledGroup(om.Group):


    #add subsystems
    def setup(self):
        self.add_subsystem('Aero',AeroDicipline())
        self.add_subsystem('Weight',Weights_Struct())
        self.add_subsystem('Mass',MassTotal())
        self.add_subsystem('Range',BreguetRangeComp())

        Balance = om.BalanceComp()
        Balance.add_balance(
            name='m_fuel',
            val=1000,
            lhs_name='R',
            rhs_name='R_target')    
        self.add_subsystem('Balance',Balance)
        
        #not really grouped with above 4 plus balance
        self.add_subsystem('Prop',Propulsion())
        self.add_subsystem('Engine',EngineWeight())

        #system containing objective
        self.add_subsystem('DOC',DOC())
       
        
        #input connections for Range box
        self.connect('Balance.m_fuel','Range.m_fuel')
        self.connect('Mass.m_total','Range.m_total')
        self.connect('Aero.LD','Range.LD')
        self.connect('Prop.SFC','Range.SFC')
        #still needs V

        #input connections for balance
        self.connect('Range.R','Balance.R')
        
        #input connections for Mass box
        self.connect('Balance.m_fuel','Mass.m_fuel')
        self.connect('Weight.m_empty','Mass.m_empty')

        #input connections for Aero box
        self.connect('Mass.m_total','Aero.m_total')
        #still needs S, AR, and V 

        #input connections for Weight
        self.connect('Engine.m_engine','Weight.m_engine')
        self.connect('Mass.m_total', 'Weight.m_total')
        #still needs S, AR, and V
        
        #input connections for Engine box
        #still needs SFC_tech

        #input connections for Prop
        #still needs V and SFC_tech

        #input connections for DOC
        self.connect('Range.R','DOC.R')
        self.connect('Balance.m_fuel','DOC.m_fuel')
        #still needs V and SFC_tech











def main():


if __name__ == "__main__":
    main()