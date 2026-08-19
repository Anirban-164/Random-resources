// 1. Target Interface 
interface LightningPhone {
    void recharge();
}

// 2. Adaptee 
class MicroUsbPhone {
    public void useMicroUsb() {
        System.out.println("Recharging with Micro-USB...");
    }
}


class LightningToMicroUsbAdapter implements LightningPhone {
    private MicroUsbPhone microUsbPhone;

    public LightningToMicroUsbAdapter(MicroUsbPhone microUsbPhone) {
        this.microUsbPhone = microUsbPhone;
    }

    @Override
    public void recharge() {
   
        microUsbPhone.useMicroUsb(); 
    }
}

// 4. Client Code
public class phonecharger {
    public static void main(String[] args) {
        MicroUsbPhone oldPhone = new MicroUsbPhone();
        
        
        LightningPhone adapter = new LightningToMicroUsbAdapter(oldPhone);
        adapter.recharge(); // Output: Recharging with Micro-USB...
    }
}