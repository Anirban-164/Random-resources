"""
Add verify_linearity(self, x1, x2, a, b) to LTISystem. Compute both sides of the superposition equation and return the maximum absolute sample difference. A correct linear system returns 0 (up to floating-point tolerance).
Formula
LHS = T{ a·x₁[n] + b·x₂[n] }
RHS = a·T{x₁[n]} + b·T{x₂[n]}
return  max_n |LHS[n] − RHS[n]|
Method signature
def verify_linearity(self, x1, x2, a, b) -> float:
"""

from signal_lti import *

class q4(LTISystem):
    def verify_linearity(self, x1, x2, a, b):
        # LHS = T{ a·x₁[n] + b·x₂[n] }
        x1_scaled = x1.multiply(a)
        x2_scaled = x2.multiply(b)
        x_in = x1_scaled.add(x2_scaled)
        lhs = self.output(x_in)
        
        # RHS = a·T{x₁[n]} + b·T{x₂[n]}
        y1 = self.output(x1)
        y2 = self.output(x2)
        y1_scaled = y1.multiply(a)
        y2_scaled = y2.multiply(b)
        rhs = y1_scaled.add(y2_scaled)
        
        # max_n |LHS[n] − RHS[n]|
        start = min(lhs.start_time, rhs.start_time)
        end = max(lhs.end_time, rhs.end_time)
    
        max_diff = 0.0
        for n in range(start, end + 1):
            val1 = lhs.get_value_at_time(n)
            val2 = rhs.get_value_at_time(n)
            max_diff = max(max_diff, abs(val1 - val2))
    
        return max_diff

def main():
    h = DiscreteSignal(0, 1) # dummy to instantiate h
    h.set_value_at_time(0, 1)
    h.set_value_at_time(1, 0)
    sys = q4(h)
    
    x1 = DiscreteSignal(0, 2)
    x1.set_value_at_time(0, 1)
    x1.set_value_at_time(1, 0)
    x1.set_value_at_time(2, 2)
    
    x2 = DiscreteSignal(0, 2)
    x2.set_value_at_time(0, 0)
    x2.set_value_at_time(1, 3)
    x2.set_value_at_time(2, -1)
    
    diff = sys.verify_linearity(x1, x2, 2.0, .5)
    print(f"Linearity difference: {diff}")

if __name__ == "__main__":
    main()
