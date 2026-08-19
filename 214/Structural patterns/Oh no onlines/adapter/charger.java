interface EuropeanSocket {
    void plugIntoRoundSocket();
}

class USCharger {
    public void chargeWithFlatPins() {
        System.out.println("🔌 [US Charger] Laptop is charging using flat pins (110V)...");
    }
}

class PowerAdapter implements EuropeanSocket {
    private USCharger usCharger;

    public PowerAdapter(USCharger usCharger) {
        this.usCharger = usCharger;
    }

    @Override
    public void plugIntoRoundSocket() {
        System.out.println("[Adapter] Converting European round socket input to US flat pin output...");
        
        // Pass the request to the wrapped US Charger
        usCharger.chargeWithFlatPins();
    }
}


// ==========================================
// 4. Main Class / Driver Code
// ==========================================
public class charger {
    public static void main(String[] args) {
        System.out.println(" Traveling to Europe with a US Laptop Charger...\n");

        // 1. You have your US Charger
        USCharger myLaptopCharger = new USCharger();

        // 2. You plug your US Charger into the Adapter
        EuropeanSocket adapter = new PowerAdapter(myLaptopCharger);

        // 3. You plug the Adapter into the European wall socket
        System.out.println(" Plugging adapter into the European wall socket:");
        adapter.plugIntoRoundSocket();
    }
}