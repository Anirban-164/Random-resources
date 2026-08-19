// Structural Design Pattern Example for the A1 PDF
// Uses Bridge for delivery region + delivery mode, and Decorator for gift wrapping.

/*
    A gift shop sells gift items such as showpieces, decorative ornaments, souvenirs, etc. Each gift item has a description and a base price. Customers may optionally request that a purchased gift
    be wrapped, which adds $2 to the item's price. Customers may also request home delivery.
    Initially, the shop provided delivery only within the local city, charging $1 per mile from the shop to the destination, with an estimated delivery time of 1 week. Later, the shop expanded its
    service to support national delivery, where the delivery charge is $1 per mile plus a fixed surcharge of $20, with an estimated delivery time of 1–2 weeks.
    The shop is now planning to introduce international delivery for selected countries. International delivery incurs a fixed surcharge of $500 and has an estimated delivery time of 2–3 weeks. In addition, customers may choose one of the following delivery modes:
    Express Delivery: Adds $10 to the delivery charge. The estimated delivery time is 2 days for local and national deliveries, and 1 week for international deliveries.
    Priority Delivery: Adds $25 to the delivery charge. The estimated delivery time is 1 day for local and national deliveries, and 5 days for international deliveries.
    The shop expects to introduce additional delivery regions and delivery modes in the future. The design should support extending both independently without requiring significant modifications
    to the existing implementation. Your task is to implement the whole system so that a product’s price and delivery time (if applicable) can be calculated and shown properly. 
*/

interface GiftItem {
    String getDescription();
    double getPrice();
}

class Product implements GiftItem {
    private final String name;
    private final double price;

    public Product(String name, double price) {
        this.name = name;
        this.price = price;
    }

    public String getDescription() {
        return name;
    }

    public double getPrice() {
        return price;
    }
}

abstract class GiftDecorator implements GiftItem {
    protected GiftItem item;

    public GiftDecorator(GiftItem item) {
        this.item = item;
    }

    abstract String getDescription();
    abstract double getPrice();
}

class WrappedGift extends GiftDecorator {
    public WrappedGift(GiftItem item) {
        super(item);
    }

    public String getDescription() {
        return item.getDescription() + " + gift wrapping";
    }

    public double getPrice() {
        return item.getPrice() + 2;
    }
}

interface DeliveryRegion {
    double getBaseCharge(int miles);
    int getBaseDays();
    String getName();
}

class LocalDelivery implements DeliveryRegion {
    public double getBaseCharge(int miles) {
        return miles * 1.0;
    }

    public int getBaseDays() {
        return 7;
    }

    public String getName() {
        return "Local";
    }
}

class NationalDelivery implements DeliveryRegion {
    public double getBaseCharge(int miles) {
        return miles * 1.0 + 20;
    }

    public int getBaseDays() {
        return 14;
    }

    public String getName() {
        return "National";
    }
}

class InternationalDelivery implements DeliveryRegion {
    public double getBaseCharge(int miles) {
        return 500;
    }

    public int getBaseDays() {
        return 21;
    }

    public String getName() {
        return "International";
    }
}

interface DeliveryMode {
    double getExtraCharge();
    int getDeliveryDays(DeliveryRegion region);
    String getName();
}

class ExpressDelivery implements DeliveryMode {
    public double getExtraCharge() {
        return 10;
    }

    public int getDeliveryDays(DeliveryRegion region) {
        if (region instanceof InternationalDelivery) return 7;
        return 2;
    }

    public String getName() {
        return "Express";
    }
}

class PriorityDelivery implements DeliveryMode {
    public double getExtraCharge() {
        return 25;
    }

    public int getDeliveryDays(DeliveryRegion region) {
        if (region instanceof InternationalDelivery) return 5;
        return 1;
    }

    public String getName() {
        return "Priority";
    }
}

class DeliveryService {
    private final DeliveryRegion region;
    private final DeliveryMode mode;
    private final int miles;

    public DeliveryService(DeliveryRegion region, DeliveryMode mode, int miles) {
        this.region = region;
        this.mode = mode;
        this.miles = miles;
    }

    public double getTotalCost(GiftItem item) {
        return item.getPrice() + region.getBaseCharge(miles) + mode.getExtraCharge();
    }

    public int getDeliveryDays() {
        return mode.getDeliveryDays(region);
    }

    public String getSummary() {
        return region.getName() + " + " + mode.getName();
    }
}

public class secA {
    public static void main(String[] args) {
        // Case 1: Local delivery with wrapping
        GiftItem vase = new WrappedGift(new Product("Decorative Vase", 40));
        DeliveryService case1 = new DeliveryService(new LocalDelivery(), new ExpressDelivery(), 10);
        System.out.println("Case 1");
        System.out.println("Gift: " + vase.getDescription());
        System.out.println("Total Cost: $" + case1.getTotalCost(vase));
        System.out.println("Estimated Delivery Time: " + case1.getDeliveryDays() + " days");
        System.out.println();

        // Case 2: National delivery with wrapping and Express
        GiftItem souvenir = new WrappedGift(new Product("Wooden Souvenir", 60));
        DeliveryService case2 = new DeliveryService(new NationalDelivery(), new ExpressDelivery(), 50);
        System.out.println("Case 2");
        System.out.println("Gift: " + souvenir.getDescription());
        System.out.println("Total Cost: $" + case2.getTotalCost(souvenir));
        System.out.println("Estimated Delivery Time: " + case2.getDeliveryDays() + " days");
        System.out.println();

        // Case 3: International delivery with Priority
        GiftItem showpiece = new Product("Crystal Showpiece", 150);
        DeliveryService case3 = new DeliveryService(new InternationalDelivery(), new PriorityDelivery(), 0);
        System.out.println("Case 3");
        System.out.println("Gift: " + showpiece.getDescription());
        System.out.println("Total Cost: $" + case3.getTotalCost(showpiece));
        System.out.println("Estimated Delivery Time: " + case3.getDeliveryDays() + " days");
    }
}
