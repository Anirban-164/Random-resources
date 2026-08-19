/*
Starbuzz sells beverages. Then they add condiments: 
Steamed milk. Soy. Mocha. Whip.
A customer may take some (maybe multiple each) condiments, all, or none.

First instinct: make a subclass for every combination.
--> "Subclass explosion" — each cost() re-computes coffee + condiments. Definitely not an option.

Second instinct: push boolean flags hasMilk, hasSoy, hasMocha, hasWhip up into Beverage, and let the superclass cost() add condiment prices.
--> New condiments break the superclass. Adding "caramel" means editing Beverage — violates Open/Closed.
--> Inappropriate inheritance. An iced tea still inherits hasWhip/hasMocha even though those make no sense for it. (BAD)
--> No multiplicity. A boolean can't express double mocha. You'd need counters, and now the superclass is a mess.

Solution???
--> stop subclassing and start wrapping
*/

import java.util.Scanner;

abstract class Beverage {
    String description = "Unknown Beverage";

    public String getDescription() {
        return description;
    }

    public abstract double cost(); // concrete drinks must define
}

// Decorator shares the supertype so it "is a" Beverage...
abstract class CondimentDecorator extends Beverage {
    Beverage beverage; // "has a" Beverage (the wrapped one)

    public abstract String getDescription(); // force re-define
}

// Base Beverage classes
class DarkRoast extends Beverage {
    public DarkRoast() {
        description = "Dark Roast Coffee";
    }

    public double cost() {
        return 2.99;
    }
}

class HouseBlend extends Beverage {
    public HouseBlend() {
        description = "House Blend Coffee";
    }

    public double cost() {
        return 1.99;
    }
}

// Condiment Decorators --> goes on top of a Beverage, and adds its own cost
class Mocha extends CondimentDecorator {
    public Mocha(Beverage beverage) {
        this.beverage = beverage;
    }

    @Override
    public String getDescription() {
        return beverage.getDescription() + ", Mocha"; // append
    }

    @Override
    public double cost() {
        return 0.20 + beverage.cost(); // add own price, then recurse inward
    }
}

class Whip extends CondimentDecorator {
    public Whip(Beverage beverage) {
        this.beverage = beverage;
    }

    @Override
    public String getDescription() {
        return beverage.getDescription() + ", Whip";
    }

    @Override
    public double cost() {
        return 0.10 + beverage.cost();
    }
}

class Soy extends CondimentDecorator {
    public Soy(Beverage beverage) {
        this.beverage = beverage;
    }

    @Override
    public String getDescription() {
        return beverage.getDescription() + ", Soy";
    }

    @Override
    public double cost() {
        return 0.15 + beverage.cost();
    }
}

public class CoffeeShop {
    public static void main(String[] args) {
        Beverage b = null;
        Scanner cin = new Scanner(System.in);

        System.out.println("Choose a beverage: \n1. Dark Roast Coffee \n2. House Blend Coffee");
        int choice = cin.nextInt();
        if (choice == 1) {
            b = new DarkRoast();
        } else {
            b = new HouseBlend();
        }

        while (true) {
            System.out.println("Choose a condiment: \n1. Mocha \n2. Whip \n3. Soy \n0. Exit");
            choice = cin.nextInt();
            switch (choice) {
                case 1:
                    b = new Mocha(b);
                    break;
                case 2:
                    b = new Whip(b);
                    break;
                case 3:
                    b = new Soy(b);
                    break;
                default:
                    choice = 0;
                    break;
            }
            if (choice == 0)
                break;

            System.out.println(b.getDescription());
        }

        if (b != null) {
            System.out.println("---------------------");
            System.out.println("Your coffee is : " + b.getDescription());
            System.out.println("Total Cost : " + b.cost());
        }

    }
}