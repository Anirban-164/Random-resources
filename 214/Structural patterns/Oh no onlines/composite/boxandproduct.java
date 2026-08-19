// Structural pattern used: Composite Pattern
// Reason: Used to uniformly calculate the total price of individual products and boxes (which can contain other boxes and products).
import java.util.ArrayList;
import java.util.List;

// -------------------------------------------------------------
// 1. Common Component Interface

interface Component {
    double getPrice();
}

// -------------------------------------------------------------
// 2. Leaf Class (Product)

class Product implements Component {
    private String name;
    private double price;

    public Product(String name, double price) {
        this.name = name;
        this.price = price;
    }

    @Override
    public double getPrice() {
        return this.price;
    }

    public String getName() {
        return name;
    }
}


class Box implements Component {
    private String boxName;
    private List<Component> children = new ArrayList<>();
    private double packagingCost; 

    public Box(String boxName, double packagingCost) {
        this.boxName = boxName;
        this.packagingCost = packagingCost;
    }

    public void add(Component component) {
        children.add(component);
    }

    public void remove(Component component) {
        children.remove(component);
    }

    @Override
    public double getPrice() {
        double total = packagingCost; 

        for (Component child : children) {
            total += child.getPrice();
        }

        return total;
    }
    public String getboxname(){
        return boxName;
    }
}

// -------------------------------------------------------------
// 4. Main / Client Class
// -------------------------------------------------------------
public class boxandproduct {
    public static void main(String[] args) {
        
        Component phone = new Product("iPhone 15", 999.99);
        Component charger = new Product("USB-C Charger", 25.00);
        Component caseCover = new Product("Phone Case", 15.00);
        Component headphone = new Product("AirPods", 199.00);

        Box smallBox = new Box("Accessories Box", 2.00); 
        smallBox.add(charger);
        smallBox.add(caseCover);

        
        Box mainBox = new Box("Main Order Box", 5.00); 
        mainBox.add(headphone);
        mainBox.add(smallBox); 

        System.out.println("=== Order Summary ===");
        System.out.println("Accessories Box Price: $" + smallBox.getPrice()); 
        // Output: 25.00 + 15.00 + 2.00 (packing) = $42.0

        System.out.println("Total Order Price: $" + mainBox.getPrice());
        // Output: 999.99 + 199.00 + 42.0 (smallBox) + 5.00 (main box packing) = $1245.99
    }
}