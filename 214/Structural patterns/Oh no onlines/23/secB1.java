// Structural pattern used: Composite Pattern and Decorator Pattern
// Reason: Composite is used to bundle gift items into packages. Decorator is used to add custom packaging (Premium, Eco-Friendly) at runtime.
/*
An e-commerce company sells gift items such as chocolates, mugs, perfumes, books, flowers, 
and many more. The company also offers several pre-defined gift packages, each consisting of 
one or more individual gift items.  
On the occasion of Eid, the company introduces a new feature that allows customers to create 
and publish their own gift packages. These user-crafted packages will be stored in the company's 
repository and displayed alongside the company's predefined packages for others to purchase. 
Customer-designed packages can be either a Personal Gift Package, intended for an individual 
recipient, or a Corporate Gift Package, intended to be distributed among employees of an 
organization. 
Customers will create a package by adding two or more individual gift items and may also use 
existing packages of the company or packages created by other customers if they wish. Usually, 
the packages of the company are packed in a standard gift box, which adds no extra cost. For 
user-crafted packages, the company has introduced two additional packaging options: 
● Premium Gift Box – adds $15 and includes premium wrapping with a decorative ribbon. 
● Eco-Friendly Gift Box – adds $8 and uses recyclable materials. 
The selected packaging style determines both the additional packaging cost and the presentation 
of the package. While creating a package, the customer must provide a name of the package, 
his/her name to be displayed as the creator of the package, and choose one packaging style.
*/

// Composite + Decorator Pattern

import java.util.ArrayList; 
import java.util.List;

// ===================== COMPOSITE PATTERN =====================

// Component
interface GiftItem {
  public double getPrice();
  public void print();
}

// Leaf
class Gift implements GiftItem {
    String name;
    double price;

    Gift(String name, double price) {
        this.name = name;
        this.price = price;
    }

    public double getPrice() {
        return this.price;
    }

    public void print() {
        System.out.println("  " + name + " - $" + price);
    }
}

// Composite (Company's predefined package — standard box, no extra cost)
class GiftPackage implements GiftItem {
    String name;
    private List<GiftItem> items = new ArrayList<>();

    public GiftPackage(String name) {
        this.name = name;
    }

    public void addItem(GiftItem item) {
        items.add(item);
    }

    public double getPrice() {
        double total = 0;
        for (GiftItem item : items) {
            total += item.getPrice();
        }
        return total;
    }

    public void print() {
        System.out.println("Package: " + name);
        for (GiftItem item : items) {
            item.print();
        }
        System.out.println("  Package Price: $" + getPrice());
    }
}

// ===================== DECORATOR PATTERN =====================

// Abstract Decorator
abstract class PackagingDecorator implements GiftItem {
    protected GiftItem wrappedItem;
    protected String creatorName;

    public PackagingDecorator(GiftItem wrappedItem, String creatorName) {
        this.wrappedItem = wrappedItem;
        this.creatorName = creatorName;
    }
}

// Concrete Decorator: Premium Gift Box (+$15)
class PremiumGiftBox extends PackagingDecorator {

    public PremiumGiftBox(GiftItem wrappedItem, String creatorName) {
        super(wrappedItem, creatorName);
    }

    public double getPrice() {
        return wrappedItem.getPrice() + 15;
    }

    public void print() {
        System.out.println(">>> Premium Gift Box (by " + creatorName + ") <<<");
        System.out.println("  [Premium wrapping with decorative ribbon]");
        wrappedItem.print();
        System.out.println("  Packaging Cost: +$15");
        System.out.println("  Total: $" + getPrice());
    }
}

// Concrete Decorator: Eco-Friendly Gift Box (+$8)
class EcoFriendlyGiftBox extends PackagingDecorator {

    public EcoFriendlyGiftBox(GiftItem wrappedItem, String creatorName) {
        super(wrappedItem, creatorName);
    }

    public double getPrice() {
        return wrappedItem.getPrice() + 8;
    }

    public void print() {
        System.out.println(">>> Eco-Friendly Gift Box (by " + creatorName + ") <<<");
        System.out.println("  [Recyclable materials packaging]");
        wrappedItem.print();
        System.out.println("  Packaging Cost: +$8");
        System.out.println("  Total: $" + getPrice());
    }
}

// ===================== ORDER =====================

class Order {
    private List<GiftItem> items = new ArrayList<>();

    public void add(GiftItem item) {
        items.add(item);
    }

    public double getPrice() {
        double total = 0;
        for (GiftItem item : items) {
            total += item.getPrice();
        }
        return total;
    }

    public void printReceipt() {
        System.out.println("========== RECEIPT ==========");
        for (GiftItem item : items) {
            item.print();
            System.out.println("-----------------------------");
        }
        System.out.printf("Total Bill: $%.2f%n", getPrice());
        System.out.println("=============================");
    } 
} 
 
public class secB1 {

    public static void main(String[] args) {
        // Individual gift items
        Gift chocolate = new Gift("Chocolate Box", 12);
        Gift mug = new Gift("Ceramic Mug", 8);
        Gift perfume = new Gift("Perfume", 25);
        Gift book = new Gift("Novel", 10);
        Gift flowers = new Gift("Flower Bouquet", 18);

        // Company's predefined package (standard box, no extra cost)
        GiftPackage companyPack = new GiftPackage("Classic Delight");
        companyPack.addItem(chocolate);
        companyPack.addItem(mug);

        // Customer-crafted Personal Gift Package with Premium Gift Box
        GiftPackage personalItems = new GiftPackage("Birthday Surprise");
        personalItems.addItem(perfume);
        personalItems.addItem(flowers);
        GiftItem personalPackage = new PremiumGiftBox(personalItems, "Alice");

        // Customer-crafted Corporate Gift Package with Eco-Friendly Gift Box
        // This package reuses the company's predefined package inside it
        GiftPackage corporateItems = new GiftPackage("Office Celebration");
        corporateItems.addItem(book);
        corporateItems.addItem(companyPack); // nested package
        GiftItem corporatePackage = new EcoFriendlyGiftBox(corporateItems, "Bob");

        // Customer Order
        Order order = new Order();
        order.add(chocolate);          // individual item
        order.add(companyPack);        // company package
        order.add(personalPackage);    // user-crafted, premium box
        order.add(corporatePackage);   // user-crafted, eco-friendly box

        order.printReceipt();
    } 
} 
