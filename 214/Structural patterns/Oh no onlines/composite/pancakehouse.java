// Structural pattern used: Composite Pattern
// Reason: Used to treat individual menu items and composite sub-menus uniformly when iterating and printing menus.
import java.util.ArrayList;
import java.util.List;

// -------------------------------------------------------------
// 1. Component (Abstract Class / Base Component)
// -------------------------------------------------------------
// Provides default implementations that throw UnsupportedOperationException
// so leaves and composites only override what they need.
abstract class MenuComponent {
    // Composite methods (managing children)
    public void add(MenuComponent menuComponent) {
        throw new UnsupportedOperationException();
    }
    public void remove(MenuComponent menuComponent) {
        throw new UnsupportedOperationException();
    }
    public MenuComponent getChild(int i) {
        throw new UnsupportedOperationException();
    }

    // Leaf methods (operations on individual items)
    public String getName() {
        throw new UnsupportedOperationException();
    }
    public String getDescription() {
        throw new UnsupportedOperationException();
    }
    public double getPrice() {
        throw new UnsupportedOperationException();
    }
    public boolean isVegetarian() {
        throw new UnsupportedOperationException();
    }

    // Common operation shared by both
    public void print() {
        throw new UnsupportedOperationException();
    }
}

// -------------------------------------------------------------
// 2. Leaf Class (MenuItem)
// -------------------------------------------------------------
class MenuItem extends MenuComponent {
    private String name;
    private String description;
    private boolean vegetarian;
    private double price;

    public MenuItem(String name, String description, boolean vegetarian, double price) {
        this.name = name;
        this.description = description;
        this.vegetarian = vegetarian;
        this.price = price;
    }

    @Override
    public String getName() {
        return name;
    }

    @Override
    public String getDescription() {
        return description;
    }

    @Override
    public double getPrice() {
        return price;
    }

    @Override
    public boolean isVegetarian() {
        return vegetarian;
    }

    @Override
    public void print() {
        System.out.print("  " + getName());
        if (isVegetarian()) {
            System.out.print("(v)");
        }
        System.out.println(", " + getPrice());
        System.out.println("     -- " + getDescription());
    }
}

// -------------------------------------------------------------
// 3. Composite Class (Menu)
// -------------------------------------------------------------
class Menu extends MenuComponent {
    private List<MenuComponent> menuComponents = new ArrayList<>();
    private String name;
    private String description;

    public Menu(String name, String description) {
        this.name = name;
        this.description = description;
    }

    @Override
    public void add(MenuComponent menuComponent) {
        menuComponents.add(menuComponent);
    }

    @Override
    public void remove(MenuComponent menuComponent) {
        menuComponents.remove(menuComponent);
    }

    @Override
    public MenuComponent getChild(int i) {
        return menuComponents.get(i);
    }

    @Override
    public String getName() {
        return name;
    }

    @Override
    public String getDescription() {
        return description;
    }

    @Override
    public void print() {
        System.out.println("\n" + getName() + ", " + getDescription());
        System.out.println("---------------------");

        // Delegates the print call recursively to all children (Items or Sub-Menus)
        for (MenuComponent menuComponent : menuComponents) {
            menuComponent.print();
        }
    }
    public double getPrice() {
        double total = 0;
        
       
        for (MenuComponent menuComponent : menuComponents) {
            total += menuComponent.getPrice();
        }
        
        return total;
    }
}

// -------------------------------------------------------------
// 4. Client Class (Waitress)
// -------------------------------------------------------------
class Waitress {
    private MenuComponent allMenus;

    public Waitress(MenuComponent allMenus) {
        this.allMenus = allMenus;
    }

    public void printMenu() {
        allMenus.print();
    }
}

// -------------------------------------------------------------
// 5. Main / Test Drive Class
// -------------------------------------------------------------
public class pancakehouse {
    public static void main(String[] args) {
        // Create individual menus
        MenuComponent pancakeHouseMenu = new Menu("PANCAKE HOUSE MENU", "Breakfast");
        MenuComponent dinerMenu = new Menu("DINER MENU", "Lunch");
        MenuComponent cafeMenu = new Menu("CAFE MENU", "Dinner");
        MenuComponent dessertMenu = new Menu("DESSERT MENU", "Dessert of course!");

        // Top-level root menu
        MenuComponent allMenus = new Menu("ALL MENUS", "All menus combined");

        // Build the tree hierarchy
        allMenus.add(pancakeHouseMenu);
        allMenus.add(dinerMenu);
        allMenus.add(cafeMenu);

        // Add items to Pancake House Menu
        pancakeHouseMenu.add(new MenuItem(
                "K&B's Pancake Breakfast",
                "Pancakes with scrambled eggs and toast",
                true,
                2.99));
        pancakeHouseMenu.add(new MenuItem(
                "Regular Pancake Breakfast",
                "Pancakes with fried eggs, sausage",
                false,
                2.99));

        // Add items to Diner Menu
        dinerMenu.add(new MenuItem(
                "Vegetarian BLT",
                "(Fakin') Bacon with lettuce & tomato on whole wheat",
                true,
                2.99));
        dinerMenu.add(new MenuItem(
                "BLT",
                "Bacon with lettuce & tomato on whole wheat",
                false,
                2.99));

        // Nesting: Add Dessert Menu as a sub-menu inside Diner Menu
        dinerMenu.add(dessertMenu);

        // Add items to Dessert Sub-Menu
        dessertMenu.add(new MenuItem(
                "Apple Pie",
                "Apple pie with a flakey crust, topped with vanilla ice-cream",
                true,
                1.59));

        // Client (Waitress) treats all menus recursively and uniformly
        Waitress waitress = new Waitress(allMenus);
        waitress.printMenu();
    }
}