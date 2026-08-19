// Structural pattern used: Composite Pattern
// Reason: Used to handle individual shapes (Dot, Circle) and composite groups (CompoundGraphic) uniformly for drawing and bounds checking.
import java.awt.Color;
import java.awt.Graphics;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

// -------------------------------------------------------------
// 1. Common Component Interface
// -------------------------------------------------------------
interface Component {
    int getX();
    int getY();
    int getWidth();
    int getHeight();
    void move(int x, int y);
    boolean isInsideBounds(int x, int y);
    void select();
    void unSelect();
    boolean isSelected();
    void draw(Graphics graphics);
}

// -------------------------------------------------------------
// 2. Base Component (Common default behavior for leaves)
// -------------------------------------------------------------
abstract class BaseShape implements Component {
    public int x;
    public int y;
    public Color color;
    private boolean selected = false;

    BaseShape(int x, int y, Color color) {
        this.x = x;
        this.y = y;
        this.color = color;
    }

    @Override
    public int getX() { return x; }

    @Override
    public int getY() { return y; }

    @Override
    public int getWidth() { return 0; }

    @Override
    public int getHeight() { return 0; }

    @Override
    public void move(int x, int y) {
        this.x += x;
        this.y += y;
    }

    @Override
    public boolean isInsideBounds(int x, int y) {
        return x >= this.x && x <= (this.x + getWidth()) &&
               y >= this.y && y <= (this.y + getHeight());
    }

    @Override
    public void select() { selected = true; }

    @Override
    public void unSelect() { selected = false; }

    @Override
    public boolean isSelected() { return selected; }

    protected void enableSelectionStyle(Graphics graphics) {
        graphics.setColor(Color.LIGHT_GRAY);
        graphics.drawRect(x - 1, y - 1, getWidth() + 2, getHeight() + 2);
        graphics.setColor(color);
    }
}

// -------------------------------------------------------------
// 3. Leaf Class 1: Dot
// -------------------------------------------------------------
class Dot extends BaseShape {
    private final int DOT_SIZE = 3;

    public Dot(int x, int y, Color color) {
        super(x, y, color);
    }

    @Override
    public int getWidth() { return DOT_SIZE; }

    @Override
    public int getHeight() { return DOT_SIZE; }

    @Override
    public void draw(Graphics graphics) {
        graphics.setColor(color);
        graphics.fillRect(x, y, getWidth(), getHeight());
        if (isSelected()) {
            enableSelectionStyle(graphics);
        }
    }
}

// -------------------------------------------------------------
// 4. Leaf Class 2: Circle
// -------------------------------------------------------------
class Circle extends BaseShape {
    public int radius;

    public Circle(int x, int y, int radius, Color color) {
        super(x, y, color);
        this.radius = radius;
    }

    @Override
    public int getWidth() { return radius * 2; }

    @Override
    public int getHeight() { return radius * 2; }

    @Override
    public void draw(Graphics graphics) {
        graphics.setColor(color);
        graphics.drawOval(x, y, getWidth(), getHeight());
        if (isSelected()) {
            enableSelectionStyle(graphics);
        }
    }
}

// -------------------------------------------------------------
// 5. Composite Class: CompoundGraphic (Holds other Components)
// -------------------------------------------------------------
class CompoundGraphic implements Component {
    protected List<Component> children = new ArrayList<>();

    public CompoundGraphic(Component... components) {
        add(components);
    }

    public void add(Component component) {
        children.add(component);
    }

    public void add(Component... components) {
        children.addAll(Arrays.asList(components));
    }

    public void remove(Component child) {
        children.remove(child);
    }

    public void clear() {
        children.clear();
    }

    @Override
    public int getX() {
        if (children.isEmpty()) return 0;
        int x = children.get(0).getX();
        for (Component child : children) {
            if (child.getX() < x) x = child.getX();
        }
        return x;
    }

    @Override
    public int getY() {
        if (children.isEmpty()) return 0;
        int y = children.get(0).getY();
        for (Component child : children) {
            if (child.getY() < y) y = child.getY();
        }
        return y;
    }

    @Override
    public int getWidth() {
        int maxCX = 0;
        for (Component child : children) {
            int childRight = child.getX() + child.getWidth();
            if (childRight > maxCX) maxCX = childRight;
        }
        return maxCX - getX();
    }

    @Override
    public int getHeight() {
        int maxCY = 0;
        for (Component child : children) {
            int childBottom = child.getY() + child.getHeight();
            if (childBottom > maxCY) maxCY = childBottom;
        }
        return maxCY - getY();
    }

    @Override
    public void move(int x, int y) {
        for (Component child : children) {
            child.move(x, y);
        }
    }

    @Override
    public boolean isInsideBounds(int x, int y) {
        for (Component child : children) {
            if (child.isInsideBounds(x, y)) return true;
        }
        return false;
    }

    @Override
    public void select() {
        for (Component child : children) {
            child.select();
        }
    }

    @Override
    public void unSelect() {
        for (Component child : children) {
            child.unSelect();
        }
    }

    @Override
    public boolean isSelected() {
        for (Component child : children) {
            if (child.isSelected()) return true;
        }
        return false;
    }

    // Delegation to child components recursively
    @Override
    public void draw(Graphics graphics) {
        for (Component child : children) {
            child.draw(graphics);
        }
    }
}

// -------------------------------------------------------------
// 6. Main Runner Class
// -------------------------------------------------------------
public class shape {
    public static void main(String[] args) {
        // Individual Leaf items
        Dot dot = new Dot(10, 10, Color.RED);
        Circle circle = new Circle(20, 30, 15, Color.BLUE);

        // Group 1 (Composite)
        CompoundGraphic group1 = new CompoundGraphic();
        group1.add(dot);
        group1.add(circle);

        // Group 2 (Composite holding another Composite)
        CompoundGraphic mainGroup = new CompoundGraphic();
        mainGroup.add(group1);
        mainGroup.add(new Circle(100, 100, 50, Color.GREEN));

        // Operation on the root Composite (moves all nested shapes automatically)
        System.out.println("Initial Root Component Boundary Width: " + mainGroup.getWidth());
        mainGroup.move(5, 10);
        System.out.println("Main Group Moved! New Root Component X: " + mainGroup.getX());
    }
}