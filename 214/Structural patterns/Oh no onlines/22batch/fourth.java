// Structural pattern used: Adapter Pattern
// Reason: Used to integrate third-party devices (OldSmartBulb, LegacyHeater) into the existing SmartHome system without modifying them.
/*
A company is developing a Smart Home Control App that allows users to control various
smart devices using voice commands.

system already supports devices that follow the company's standard interface:
public interface Smart Device{
    void turnOn ( ) ;
    void turnOff() ;
}

Currently supported devices include Smart Light, Smart Fan, and Smart AC. All of them
correctly implement SmartDevice. The company now wants to integrate third-party smart
devices from other manufacturers. However, these devices do not follow the Smartl)evice
interface.

1. OldSmartBulb
public class OldSHartBuIb{
    public void powerOn(){}
    public void powerOff(){}
}

2. Legacylleatar
public class LegacyHeater {
    public void startHeating() {}
    public void stopHeating ( ){}
}

However, these devices need to be integrated without modifying the existing interface. Also,
third-party device classes cannot be changed, and the app should continue to work using the
existing methods. Also, the System should allow adding more third-party devices easily in the
future. Your task is to design a solution that allows all third-party devices to be controlled using
the SmartDevice interface without modifying their original implementations.

*/


import java.util.ArrayList;
import java.util.List;

// =============================================================
// 1. Existing System Interface & Classes (Target Interface)
// =============================================================
interface SmartDevice {
    void turnOn();
    void turnOff();
}

// Existing supported devices
class SmartLight implements SmartDevice {
    @Override
    public void turnOn() {
        System.out.println("Smart Light is now ON");
    }

    @Override
    public void turnOff() {
        System.out.println("Smart Light is now OFF");
    }
}

class SmartAC implements SmartDevice {
    @Override
    public void turnOn() {
        System.out.println("Smart AC is cooling the room");
    }

    @Override
    public void turnOff() {
        System.out.println("Smart AC is turned OFF");
    }
}

// =============================================================
// 2. Third-Party / Legacy Classes (Adaptee) - CANNOT BE MODIFIED
// =============================================================
class OldSmartBulb {
    public void powerOn() {
        System.out.println("Old Smart Bulb powered ON via legacy method");
    }

    public void powerOff() {
        System.out.println("Old Smart Bulb powered OFF via legacy method");
    }
}

class LegacyHeater {
    public void startHeating() {
        System.out.println("Legacy Heater started heating");
    }

    public void stopHeating() {
        System.out.println("Legacy Heater stopped heating");
    }
}

// =============================================================
// 3. Adapters (Object Adapter Pattern)
// =============================================================
abstract class DeviceAdapter <Adaptee> implements SmartDevice {
    protected Adaptee adaptee;
    public DeviceAdapter(Adaptee adaptee) {
        this.adaptee = adaptee;
    }
    public abstract void turnOn();
    public abstract void turnOff();
}


// Adapter for OldSmartBulb
class OldSmartBulbAdapter extends DeviceAdapter<OldSmartBulb> {
    public OldSmartBulbAdapter(OldSmartBulb oldBulb) {
        super(oldBulb);
    }

    @Override
    public void turnOn() {
        adaptee.powerOn(); // Map turnOn() to powerOn()
    }

    @Override
    public void turnOff() {
        adaptee.powerOff(); // Map turnOff() to powerOff()
    }
}

// Adapter for LegacyHeater
class LegacyHeaterAdapter extends DeviceAdapter<LegacyHeater> {
    public LegacyHeaterAdapter(LegacyHeater legacyHeater) {
        super(legacyHeater);
    }

    @Override
    public void turnOn() {
        adaptee.startHeating(); // Map turnOn() to startHeating()
    }

    @Override
    public void turnOff() {
        adaptee.stopHeating(); // Map turnOff() to stopHeating()
    }
}

// =============================================================
// 4. Client Code (Smart Home App)
// =============================================================
public class fourth {
    public static void main(String[] args) {
        // লিস্টের মধ্যে সব ডিভাইস রাখব (Native + Third Party)
        List<SmartDevice> devices = new ArrayList<>();

        // ১. অরিজিনাল ডিভাইসগুলো যোগ করা হলো
        devices.add(new SmartLight());
        devices.add(new SmartAC());

        // ২. থার্ড-পার্টি ডিভাইসগুলোকে Adapter দিয়ে র‍্যাপ করে যোগ করা হলো
        OldSmartBulb oldBulb = new OldSmartBulb();
        devices.add(new OldSmartBulbAdapter(oldBulb));

        LegacyHeater legacyHeater = new LegacyHeater();
        devices.add(new LegacyHeaterAdapter(legacyHeater));

        // ৩. অ্যাপের মাধ্যমে সব ডিভাইস একইভাবে অন করা হচ্ছে
        System.out.println("=== TURNING ON ALL DEVICES ===");
        for (SmartDevice device : devices) {
            device.turnOn();
        }

        System.out.println("\n=== TURNING OFF ALL DEVICES ===");
        for (SmartDevice device : devices) {
            device.turnOff();
        }
    }
}