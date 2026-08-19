/*
ZBazar is a Subscription-based grocery delivery service that lets customers set up a recurring monthly bazar bundle that is automatically delivered to their homes. The platform Offers preset
packages (such as Small, Family, and Mega) and single grocery items (individual items like rice, oil, pulse, etc.). Preset packages consist of multiple single items. Each item has its specific name,
price, and weight. Users can Create or modify their own Custom Bazar by combining one or more preset packages and/or single items. A custom package may include only individual itemse
only preset packages, or a mixture of both. Users can also include their previously created custom packages. The system must support calculating the total price and weight of any
configuration and displaying the complete structure of the custom package.

Task: Choose the appropriate design pattern to solve this problem and implement a minimal
demonstration
*/


import java.util.ArrayList;
import java.util.List;

// -------------------------------------------------------------
// 1. Common Component Interface

interface Component {
    double getPrice();
    double getweight();
}

// -------------------------------------------------------------
// 2. Leaf Class (Product)

class Product implements Component {
    private double weight;
    private double price;

    public Product(double weight, double price) {
        this.weight = weight;
        this.price = price;
    }

    @Override
    public double getPrice() {
        return this.price;
    }

    public double getweight() {
        return this.weight;
    }
}


class Package implements Component {
    private List<Component> children = new ArrayList<>();

    public void add(Component component) {
        children.add(component);
    }

    public void remove(Component component) {
        children.remove(component);
    }

    @Override
    public double getPrice() {
        double total = 0;
        for (Component child : children) {
            total += child.getPrice();
        }

        return total;
    }

    public double getweight() {
        double total = 0;
        for (Component child : children) {
            total += child.getweight();
        }

        return total;
    }
}

// -------------------------------------------------------------
// 4. Main / Client Class
// -------------------------------------------------------------
public class second {
    public static void main(String[] args) {
        
        Component phone = new Product(7, 999.99);
        Component charger = new Product(8, 25.00);
        Component caseCover = new Product(90, 15.00);
        Component headphone = new Product(10, 199.00);

        Package p1=new Package();
        p1.add(phone);

        Package p2=new Package();
        p2.add(p1);
        p2.add(charger);
        p2.add(caseCover);
        p2.add(headphone);

        System.out.println("price:    "+p1.getPrice());
        System.out.println("weight    "+p2.getweight());
    }
}