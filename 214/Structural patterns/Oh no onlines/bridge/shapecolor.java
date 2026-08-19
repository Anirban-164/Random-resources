// ---- 1. Implementor Interface ----
interface Color {
    void applyColor();
}

// ---- Concrete Implementors ----
class RedColor implements Color {
    @Override
    public void applyColor() {
        System.out.print("Applying Red color to ");
    }
}

class BlueColor implements Color {
    @Override
    public void applyColor() {
        System.out.print("Applying Blue color to ");
    }
}

// ---- 2. Abstraction ----
abstract class Shape {
    // This reference acts as the BRIDGE between Shape and Color
    protected Color color;

    public Shape(Color color) {
        this.color = color;
    }

    abstract public void draw();
}

// ---- Refined Abstractions ----
class Circle extends Shape {
    public Circle(Color color) {
        super(color);
    }

    @Override
    public void draw() {
        color.applyColor(); // Delegates the coloring responsibility to the Color object
        System.out.println("a Circle.");
    }
}

class Square extends Shape {
    public Square(Color color) {
        super(color);
    }

    @Override
    public void draw() {
        color.applyColor();
        System.out.println("a Square.");
    }
}

// ---- 3. Client ----
public class shapecolor {
    public static void main(String[] args) {
        // Red Circle
        Shape redCircle = new Circle(new RedColor());
        redCircle.draw();

        // Blue Square
        Shape blueSquare = new Square(new BlueColor());
        blueSquare.draw();

        // Reusing Blue color for a Circle without creating a "BlueCircle" class!
        Shape blueCircle = new Circle(new BlueColor());
        blueCircle.draw();
    }
}