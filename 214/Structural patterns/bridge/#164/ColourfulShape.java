/*
You have shapes: Circle and Square.
You want to add colors: Red and Blue.

The naïve inheritance approach creates one subclass per combination:
- RedCircle
- BlueCircle
- RedSquare
- BlueRectangle

If we add a new color e.g. (Green) or a new shape e.g. (Triangle).
--> the hierarchy grows exponentially: with S shapes and C colors you need S × C classes.
--> This happens because two entirely independent concerns — form and color — are entangled in the same inheritance hierarchy.

Trying to extend a class in two independent dimensions (shape + color) using inheritance always leads to exponential class growth.
--> The dimensions are independent — a change to color logic shouldn't require touching the shape hierarchy and vice versa.

Solution:
Instead of having RedCircle extend Shape, we extract color into its own hierarchy and give Shape a reference to a Color object.
*/

// IMPLEMENTATION side — Color hierarchy
interface Color {
    void applyColor();
}

class Red implements Color {
    public void applyColor() { System.out.println("Applying red"); }
}

class Blue implements Color {
    public void applyColor() { System.out.println("Applying blue"); }
}

class Green implements Color {
    // Adding green to Circle requires only ONE new class — not N new classes!
    public void applyColor() { System.out.println("Applying green"); }
}

// ABSTRACTION side — Shape hierarchy
abstract class Shape {
    protected Color color; // the BRIDGE — reference to implementation

    public Shape(Color color) {
        this.color = color;
    }

    public abstract void draw();
}

class Circle extends Shape {
    public Circle(Color color) { super(color); }

    public void draw() {
        System.out.print("Drawing circle. Color: ");
        color.applyColor(); // delegate color work to implementation
    }
}

class Rectangle extends Shape {
    public Rectangle(Color color) { super(color); }

    public void draw() {
        System.out.print("Drawing rectangle. Color: ");
        color.applyColor();
    }
}

class Triangle extends Shape {
    public Triangle(Color color) { super(color); }

    public void draw() {
        System.out.print("Drawing triangle. Color: ");
        color.applyColor();
    }
}

// Client
public class ColourfulShape{
    public static void main(String[] args) {
        Shape redCircle = new Circle(new Red());
        Shape blueRectangle = new Rectangle(new Blue());
        Shape blueCircle = new Circle(new Blue());

        Shape greenTriangle = new Triangle(new Green());
        
        redCircle.draw();
        blueRectangle.draw();
        blueCircle.draw();

        greenTriangle.draw();
    }
}