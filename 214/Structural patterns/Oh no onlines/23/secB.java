// Structural pattern used: Composite Pattern
// Reason: Used to uniformly treat individual food/grocery items and composite packages (like combo meals or grocery packs).
/*
A restaurant chain wants to build a flexible food ordering system. A customer can order individual food items as well as bundled packages such as combo meals and grocery packs. All of these items should be treated uniformly in the system because they all have a price and can be displayed in a receipt.

Each food item has a name and a base price. A combo meal contains multiple food items, and a grocery package can contain both individual items and other packages. The system should support nested combinations, so a package may contain another package inside it. The total price of an order must be calculated automatically, regardless of whether the order contains single items or groups of items.

Your task is to implement the whole system so that:
- every item can be treated using one common interface,
- simple items and composite items are handled in the same way,
- nested packages can be added without changing the code structure,
- the final bill can be printed clearly.

You may use one or more structural design patterns as needed, but the design should allow easy extension if more food items or package types are introduced in the future.
*/

import java.util.ArrayList; 
import java.util.List;

interface OrderItem {
  public double getPrice();
  public void print();
}

class Food implements OrderItem{
    String name;
    double price;

    Food(String name,double price){
        this.name = name;
        this.price = price;
    }

    public double getPrice(){
        return this.price;
    }

    public void print(){
        System.out.println(name);
        System.out.println(price);
    }
}

class SetMenu implements OrderItem{
    String name;
    private List<Food> food = new ArrayList<>();

    public SetMenu(String name){
        this.name = name;
    }

    public void addFood(Food f){
        food.add(f);
    }

    public double getPrice() {
        double total = 0;
        for (Food item : food) {
            total += item.getPrice();
        }

        return total;
    }

    public void print(){
       for (Food item : food) {
            item.print();
        }
    }
}

class Grocery implements OrderItem{
    String name;
    double price;
   
    public Grocery(String name,double price){
        this.name=name;
        this.price=price;
    }
  
    public double getPrice() {
       return price;
    }
   public void print(){
        System.out.println(name);
        System.out.println(price);
    }
}

class GroceryPackage implements OrderItem{
    String name;
    private List<OrderItem> or = new ArrayList<>();
    public GroceryPackage(String name){
        this.name=name;
    }
    public void add(OrderItem orr){
        or.add(orr);
    }
    public double getPrice() {

        double total = 0;

        for (OrderItem item : or) {
            total += item.getPrice();
        }

        return total;
    }
    public void print(){
        for (OrderItem item : or) {
           item.print();
        }
    }
}

class Order {
    private List<OrderItem> items = new ArrayList<>();

    public void add(OrderItem item) {
        items.add(item);
    }

    public double getPrice() {
        double total = 0;

        for (OrderItem item : items) {
            total += item.getPrice();
        }

        return total;
    }

    public void printReceipt() {
        System.out.println("========== RECEIPT ==========");

        for (OrderItem item : items) {
            item.print();

        }

        System.out.println("-----------------------------");
        System.out.printf("Total Bill: £%.2f%n", getPrice());
    } 
} 
 
public class secB {

    public static void main(String[] args) {
        // Foods
        Food burger = new Food("Burger", 8);
        Food pizza = new Food("Pizza", 10);
        Food fries = new Food("French Fries", 3);

        // Set Menu
        SetMenu lunch = new SetMenu("Lunch Combo");
        lunch.addFood(burger);
        lunch.addFood(fries);

        // Grocery Items
        Grocery rice = new Grocery("Rice", 20);
        Grocery oil = new Grocery("Cooking Oil", 12);
        Grocery eggs = new Grocery("Eggs", 6);
        Grocery sugar = new Grocery("Sugar", 5);

        // Small Package
        GroceryPackage breakfastPack = new GroceryPackage("Breakfast Pack");
        breakfastPack.add(eggs);
        breakfastPack.add(sugar);

        // Large Package (contains another package)
        GroceryPackage monthlyPack = new GroceryPackage("Monthly Essentials");
        monthlyPack.add(rice);
        monthlyPack.add(oil);
        monthlyPack.add(breakfastPack);

        // Customer Order
        Order order = new Order();

        order.add(pizza);
        order.add(lunch);
        order.add(rice);
        order.add(monthlyPack);

        order.printReceipt();
    } 
} 
