// Structural pattern used: Adapter Pattern
// Reason: Used to adapt a SquarePeg to be treated as a RoundPeg so it can be checked against a RoundHole.
// -------------------------------------------------------------
// 1. Target Class 
// -------------------------------------------------------------
class RoundHole {
    private double radius;

    public RoundHole(double radius) {
        this.radius = radius;
    }

    public double getRadius() {
        return radius;
    }

    // 
    public boolean fits(RoundPeg peg) {
        return this.getRadius() >= peg.getRadius();
    }
}

// -------------------------------------------------------------
// 2. Compatible Object 
// -------------------------------------------------------------
class RoundPeg {
    private double radius;

    public RoundPeg() {}

    public RoundPeg(double radius) {
        this.radius = radius;
    }

    public double getRadius() {
        return radius;
    }
}

// -------------------------------------------------------------
// 3. Adaptee / Incompatible Class 
// -------------------------------------------------------------
class SquarePeg {
    private double width;

    public SquarePeg(double width) {
        this.width = width;
    }

    public double getWidth() {
        return width;
    }

    
    
}

// -------------------------------------------------------------
// 4. Adapter Class 
// -------------------------------------------------------------
class SquarePegAdapter extends RoundPeg {
    private SquarePeg peg;

    public SquarePegAdapter(SquarePeg peg) {
        this.peg = peg;
    }

    @Override
    public double getRadius() {
         
        // Radius = (Width * sqrt(2)) / 2
        return (Math.sqrt(Math.pow(peg.getWidth(), 2) * 2) / 2);
    }
}

// -------------------------------------------------------------
// 5. Main / Client Class
// -------------------------------------------------------------
public class roundsquare {
    public static void main(String[] args) {
       
        RoundHole hole = new RoundHole(5);
        
        
        RoundPeg rpeg = new RoundPeg(5);
        if (hole.fits(rpeg)) {
            System.out.println("Round peg r5 fits round hole r5.");
        }

        
        SquarePeg smallSqPeg = new SquarePeg(2);
        SquarePeg largeSqPeg = new SquarePeg(20);

        

        
        SquarePegAdapter smallSqPegAdapter = new SquarePegAdapter(smallSqPeg);
        SquarePegAdapter largeSqPegAdapter = new SquarePegAdapter(largeSqPeg);

        if (hole.fits(smallSqPegAdapter)) {
            System.out.println("Square peg w2 fits round hole r5.");
        }

        if (!hole.fits(largeSqPegAdapter)) {
            System.out.println("Square peg w20 does not fit into round hole r5.");
        }
    }
}