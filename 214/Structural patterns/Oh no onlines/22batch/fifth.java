// Structural pattern used: Decorator Pattern
// Reason: Used to dynamically customize Ramadan packages (adding fruit, sweets) without modifying the base package classes.
/*
ZBazar traditionally offers three fixed Ramadan packages every year. They are: Standard, Special, and Premium.
 
These packages have predefined contents and pricing, and over time, they have become very popular. Many customers not only purchase them for personal use but also send them as gifts to friends and relatives during Ramadan. The structure and pricing of these Ramadan packages well-established and are part of   ZBazar's seasonal business model.

However, recently, ZBazar has received requests for slight customization. Some customers want to add fruit, others want to include sweets, and others want to opt for premium gift packaging when sending a package to loved ones.
Instead of allowing full customization, ZBazar decided to provide limited flexibility by allowing customers to optionally add:
(l) a predefined Fruit Package,
(2) a predefined Sweet Package, and 
(3) premium gift packaging for presentation purposes. 
These enhancements may be applied in any combination. 
[The fruit and sweet packages are sold throughout the whole year and
are also part of ZBazar's business model.]
Your task is to make the existing system capable ofhandling this Ramadan's special flexibility without
modifying the existing packages. You can safely assume that the system already supports the previous
business model. The system must correctly calculate the final price and description of the customized
bundle while preserving the original package structure
*/


abstract class Package {
    String description = "Unknown Packages";
  
    public String getDescription() {
        return description;
    }
  
    public abstract double cost();
}

class StandardPackage extends Package {
    public StandardPackage() {
        description = "Standard_package";
    }
  
    @Override
    public double cost() {
        return 1.99;
    }
}

class SpecialPackage extends Package {
    public SpecialPackage() {
        description = "Special package";
    }
  
    @Override
    public double cost() {
        return 0.99;
    }
}



abstract class Decorator extends Package {
    public abstract String getDescription();
}

class AddFruit extends Decorator {
    Package packagess;

    public addfruit(packagess packagess) {
        this.packagess = packagess;
    }

    @Override
    public String getDescription() {
        return packagess.getDescription() + ", addfruit";
    }

    @Override
    public double cost() {
        return 0.20 + packagess.cost();
    }
}

class AddSweet extends Decorator {
    Package packagess;

    public AddSweet(Package packagess) {
        this.packagess = packagess;
    }

    @Override
    public String getDescription() {
        return packagess.getDescription() + ", addsweet";
    }

    @Override
    public double cost() {
        return 0.10 + packagess.cost();
       }
}


public class fifth {
    public static void main(String[] args) {
        Package packagess = new StandardPackage();
        System.out.println(packagess.getDescription() + " $" + packagess.cost());

        System.out.println("--------------------------------------");

        Package packagess2 = new SpecialPackage(); 
        packagess2 = new AddFruit(packagess2);     
        packagess2 = new AddFruit(packagess2);   
        
        System.out.println(packagess2.getDescription() + " $" + String.format("%.2f", packagess2.cost()));

        System.out.println("--------------------------------------");
    }
}