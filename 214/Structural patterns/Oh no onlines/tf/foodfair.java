// Structural pattern used: Decorator Pattern
// Reason: Used to dynamically add 'Extra Cheese' to different Pizza types without creating a subclass for every combination.
import java.util.ArrayList;
import java.util.List;

// =============================================================================
// SECTION 1: DECORATOR PATTERN (Pizza & Extra Cheese Customization)
// =============================================================================

// Base Component Interface for Pizza
interface Pizza {
    String getDescription();
    double getPrice();
}

// Concrete Component 1: Veggie Pizza
class VeggiePizza implements Pizza {
    @Override
    public String getDescription() {
        return "Veggie Pizza";
    }

    @Override
    public double getPrice() {
        return 350.0;
    }
}

// Concrete Component 2: Beef Pizza
class BeefPizza implements Pizza {
    @Override
    public String getDescription() {
        return "Beef Pizza";
    }

    @Override
    public double getPrice() {
        return 450.0;
    }
}

// Concrete Component 3: Chicken Pizza
class ChickenPizza implements Pizza {
    @Override
    public String getDescription() {
        return "Chicken Pizza";
    }

    @Override
    public double getPrice() {
        return 400.0;
    }
}

// Abstract Decorator
abstract class PizzaDecorator implements Pizza {
    protected Pizza pizza;

    public PizzaDecorator(Pizza pizza) {
        this.pizza = pizza;
    }

    @Override
    public String getDescription() {
        return pizza.getDescription();
    }

    @Override
    public double getPrice() {
        return pizza.getPrice();
    }
}

// Concrete Decorator: Extra Cheese
class ExtraCheese extends PizzaDecorator {
    public ExtraCheese(Pizza pizza) {
        super(pizza);
    }

    @Override
    public String getDescription() {
        return super.getDescription() + " + Extra Cheese";
    }

    @Override
    public double getPrice() {
        return super.getPrice() + 50.0; // Extra Cheese Price
    }
}


// =============================================================================
// SECTION 2: FACTORY METHOD PATTERN (Appetizers & Drinks Creation)
// =============================================================================

// Item Interface
interface Item {
    String getName();
    double getPrice();
}

// --- APPETIZERS ---
class FrenchFries implements Item {
    @Override
    public String getName() {
        return "French Fries";
    }

    @Override
    public double getPrice() {
        return 120.0;
    }
}

class OnionRings implements Item {
    @Override
    public String getName() {
        return "Onion Rings";
    }

    @Override
    public double getPrice() {
        return 140.0;
    }
}

// --- DRINKS ---
class Coffee implements Item {
    @Override
    public String getName() {
        return "Coffee";
    }

    @Override
    public double getPrice() {
        return 100.0;
    }
}

class Water implements Item {
    @Override
    public String getName() {
        return "Bottle of Water";
    }

    @Override
    public double getPrice() {
        return 20.0;
    }
}

class Coke implements Item {
    @Override
    public String getName() {
        return "Coke";
    }

    @Override
    public double getPrice() {
        return 35.0;
    }
}

// Factory Class to create Side Items
class SideItemFactory {
    public static Item createItem(String type) {
        if (type.equalsIgnoreCase("FrenchFries")) {
            return new FrenchFries();
        } else if (type.equalsIgnoreCase("OnionRings")) {
            return new OnionRings();
        } else if (type.equalsIgnoreCase("Coffee")) {
            return new Coffee();
        } else if (type.equalsIgnoreCase("Water")) {
            return new Water();
        } else if (type.equalsIgnoreCase("Coke")) {
            return new Coke();
        }
        throw new IllegalArgumentException("Unknown Item Type: " + type);
    }
}


// =============================================================================
// SECTION 3: BUILDER PATTERN (Constructing Combo Meal)
// =============================================================================

class Meal {
    private Pizza pizza;
    private Item appetizer;
    private List<Item> drinks = new ArrayList<>();

    public void setPizza(Pizza pizza) {
        this.pizza = pizza;
    }

    public void setAppetizer(Item appetizer) {
        this.appetizer = appetizer;
    }

    public void addDrink(Item drink) {
        drinks.add(drink);
    }

    // Method to calculate and get total price of the meal
    public double getPrice() {
        double total = 0.0;
        if (pizza != null) total += pizza.getPrice();
        if (appetizer != null) total += appetizer.getPrice();
        for (Item drink : drinks) {
            total += drink.getPrice();
        }
        return total;
    }

    public void showMealDetails() {
        System.out.println("--- Meal Description ---");
        if (pizza != null) System.out.println("Pizza: " + pizza.getDescription() + " ($" + pizza.getPrice() + ")");
        if (appetizer != null) System.out.println("Appetizer: " + appetizer.getName() + " ($" + appetizer.getPrice() + ")");
        if (!drinks.isEmpty()) {
            System.out.print("Drinks: ");
            for (Item d : drinks) {
                System.out.print(d.getName() + " ($" + d.getPrice() + ") ");
            }
            System.out.println();
        }
        System.out.println("Total Price: $" + getPrice());
        System.out.println("------------------------\n");
    }
}

// Meal Builder Class
class MealBuilder {
    private Meal meal;

    public MealBuilder() {
        this.meal = new Meal();
    }

    public MealBuilder setPizza(Pizza pizza) {
        meal.setPizza(pizza);
        return this;
    }

    public MealBuilder setAppetizer(Item appetizer) {
        meal.setAppetizer(appetizer);
        return this;
    }

    public MealBuilder addDrink(Item drink) {
        meal.addDrink(drink);
        return this;
    }

    public Meal build() {
        return this.meal;
    }
}


// =============================================================================
// MAIN / DRIVER CLASS (Executing Requirements 1 to 4)
// =============================================================================

public class foodfair {
    public static void main(String[] args) {
        System.out.println("==========================================");
        System.out.println("  BURGER & PIZZA SHOP ORDERING SYSTEM   ");
        System.out.println("==========================================\n");

        // ---------------------------------------------------------------------
        // Requirement (1): Beef pizza with French fry and cheese
        // ---------------------------------------------------------------------
        System.out.println("Order 1: Beef pizza with French fry and cheese");
        Pizza beefPizzaWithCheese = new ExtraCheese(new BeefPizza()); // Decorator
        Item frenchFry1 = SideItemFactory.createItem("FrenchFries");   // Factory

        Meal order1 = new MealBuilder()
                .setPizza(beefPizzaWithCheese)
                .setAppetizer(frenchFry1)
                .build();

        order1.showMealDetails();

        // ---------------------------------------------------------------------
        // Requirement (2): Chicken Pizza with onion rings and Bottle of Water
        // ---------------------------------------------------------------------
        System.out.println("Order 2: Chicken Pizza with onion rings and Bottle of Water");
        Pizza chickenPizza = new ChickenPizza();
        Item onionRings2 = SideItemFactory.createItem("OnionRings");
        Item water2 = SideItemFactory.createItem("Water");

        Meal order2 = new MealBuilder()
                .setPizza(chickenPizza)
                .setAppetizer(onionRings2)
                .addDrink(water2)
                .build();

        order2.showMealDetails();

        // ---------------------------------------------------------------------
        // Requirement (3): A combo meal with Veggi pizza, French Fry and two bottles of Coke
        // ---------------------------------------------------------------------
        System.out.println("Order 3: Combo meal with Veggi pizza, French Fry and two bottles of Coke");
        Pizza veggiePizza3 = new VeggiePizza();
        Item frenchFry3 = SideItemFactory.createItem("FrenchFries");
        Item coke1 = SideItemFactory.createItem("Coke");
        Item coke2 = SideItemFactory.createItem("Coke");

        Meal order3 = new MealBuilder()
                .setPizza(veggiePizza3)
                .setAppetizer(frenchFry3)
                .addDrink(coke1)
                .addDrink(coke2)
                .build();

        order3.showMealDetails();

        // ---------------------------------------------------------------------
        // Requirement (4): A combo meal with Veggi pizza, Onion Rings, Coffee and Water
        // ---------------------------------------------------------------------
        System.out.println("Order 4: Combo meal with Veggi pizza, Onion Rings, Coffee and Water");
        Pizza veggiePizza4 = new VeggiePizza();
        Item onionRings4 = SideItemFactory.createItem("OnionRings");
        Item coffee4 = SideItemFactory.createItem("Coffee");
        Item water4 = SideItemFactory.createItem("Water");

        Meal order4 = new MealBuilder()
                .setPizza(veggiePizza4)
                .setAppetizer(onionRings4)
                .addDrink(coffee4)
                .addDrink(water4)
                .build();

        order4.showMealDetails();
    }
}