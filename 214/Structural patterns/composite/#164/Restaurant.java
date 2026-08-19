/*
The Pancake House merges with the Diner, and now the menu is a menu-of-menus: breakfast items, a dessert sub-menu inside the lunch menu, and so on.

The problems:
-—> something tree-like structure
-—> Traversal should be flexible — iterate over one sub-menu (e.g. desserts) or the entire hierarchy.

The pain without Composite:
the client must constantly ask "is this a single MenuItem or a whole Menu?"
-—> branching?
    if (x is Menu) loopThroughChildren();
    else printItem();
That conditional spreads everywhere.

Solution:
--> A Menu (composite) holds children that may be MenuItems (leaves) or other Menus.
--> A MenuItem (leaf) has no children; a composite forwards operations to its children.
 */

import java.util.*;

interface MenuComponent {
    String getDescription();
    double getPrice();
    void print(String indent);
}

// concrete classes
class MenuItem implements MenuComponent {
    String name;
    double price;

    public MenuItem(String name, double price) {
        this.name = name;
        this.price = price;
    }

    public String getDescription() {
        return name;
    }

    public double getPrice() {
        return price;
    }

    public void print(String indent) {
        System.out.println(indent + "- " + name + "  $" + price);
    }
}

class Menu implements MenuComponent {
    String name;
    ArrayList<MenuComponent> menuComponents = new ArrayList<>();

    public Menu(String name) {
        this.name = name;
    }

    public void add(MenuComponent menuComponent) {
        menuComponents.add(menuComponent);
    }

    public void remove(MenuComponent menuComponent) {
        menuComponents.remove(menuComponent);
    }

    public String getDescription() {
        return name;
    }

    public double getPrice() {
        double total = 0;
        for (MenuComponent menuComponent : menuComponents) {
            total += menuComponent.getPrice();
        }
        return total;
    }

    public void print(String indent) {
        System.out.println(indent + "+ " + name);
        for (MenuComponent children : menuComponents) {
            children.print(indent + "\t");
        }
    }
}

public class Restaurant {
    public static void main(String[] args) {
        // main menu
        Menu all = new Menu("ALL MENUS");
        // 2 submenus
        Menu diner = new Menu("DINER MENU");
        Menu pancakeHouse = new Menu("PANCAKE HOUSE MENU");

        // create pancakehouse items
        MenuItem pancake = new MenuItem("Pancakes", 2.99);
        MenuItem waffles = new MenuItem("Waffles", 2.79);
        pancakeHouse.add(pancake);
        pancakeHouse.add(waffles);

        // create diner items
        MenuItem hamburger = new MenuItem("Hamburger", 3.49);
        diner.add(hamburger);
        Menu dessert = new Menu("DESSERTS");
        diner.add(dessert); // another submenu under diner menu

        // create dessert items
        MenuItem cheesecake = new MenuItem("Cheesecake", 3.99);
        MenuItem pie = new MenuItem("Pie", 2.5);
        dessert.add(cheesecake);
        dessert.add(pie);

        // add them to all menus
        all.add(diner);
        all.add(pancakeHouse);

        all.print(""); // prints the entire hierarchy…
        // dessert.print("");
    }
}
