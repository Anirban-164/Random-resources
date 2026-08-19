/*
A US laptop uses a two-pin flat plug. A European wall outlet exposes a round two-pin socket.
The plug adapter converts one interface into another — your laptop doesn't know or care; it just plugs in.
This is exactly what the Adapter pattern does in software.

Motivation: The Duck Simulator
--> Your existing codebase uses a Duck interface with quack() and fly().
--> A new vendor library provides a Turkey interface with gobble() and fly() (but turkeys fly in short spurts).
--> Now you want to use these turkeys in your duck simulator — meaning you need them to respond to quack() and fly().
--> You could change the Turkey code, but what if the library updates? You’d have to change your code again.

Solution?
--> Use an converter that lets the Turkey objects respond to the Duck interface. Which is known as Adapter pattern
*/

interface Duck {
    void quack();
    void fly();
}

class MallardDuck implements Duck {
    public void quack() { System.out.println("Quack"); }
    public void fly()   { System.out.println("I'm flying"); }
}

class RuddyShelduck implements Duck {
    public void quack() { System.out.println("Quack"); }
    public void fly()   { System.out.println("I'm flying"); }
}

interface Turkey {
    void gobble(); // not quack() !
    void fly();    // flies short distances only
}

class WildTurkey implements Turkey {
    public void gobble() { System.out.println("Gobble gobble"); }
    public void fly()    { System.out.println("I'm flying a short distance"); }
}

// 1. Implement the TARGET interface (Duck) — what the client expects
class TurkeyAdapter implements Duck {
    private final Turkey turkey; // holds reference to the ADAPTEE --> final is recommended, not mandatory

    // 2. Get a reference to the adaptee via constructor
    public TurkeyAdapter(Turkey turkey) {
        this.turkey = turkey;
    }

    // 3. Translate each target method → adaptee method
    public void quack() {
        turkey.gobble(); // quack → gobble translation
    }

    public void fly() {
        // Turkeys fly in short bursts, so call 5 times to simulate one duck-fly
        for (int i = 0; i < 5; i++) {
            turkey.fly();
        }
    }
}

public class DuckSimulator {
    public static void main(String[] args) {
        MallardDuck duck = new MallardDuck();
        WildTurkey turkey = new WildTurkey();

        // Wrap Turkey in adapter so it looks like a Duck
        Duck newTurkey = new TurkeyAdapter(turkey);

        testDuck(duck);          // real duck
        testDuck(newTurkey); // turkey pretending to be a duck!
    }

    static void testDuck(Duck duck) {
        // doesn't need to be a separate method, just for readability
        duck.quack(); // client only knows about Duck interface
        duck.fly();
    }
}