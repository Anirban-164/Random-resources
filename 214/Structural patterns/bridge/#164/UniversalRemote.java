// IMPLEMENTATION side — device hierarchy
interface Device {
    boolean isEnabled();
    void enable();
    void disable();
    int getLevel();
    void setLevel(int percent);
}

class Tv implements Device {
    private boolean on = false;
    private int volume = 30;

    public boolean isEnabled() {
        return on;
    }
    
    public void enable() {
        on = true;
        System.out.println("TV ON");
    }

    public void disable() {
        on = false;
        System.out.println("TV OFF");
    }

    public int getLevel() {
        return volume;
    }

    public void setLevel(int v) {
        volume = v;
        System.out.println("TV volume: " + v);
    }
}

class AC implements Device{
    private boolean on = false;
    private int temperature = 24;

    public boolean isEnabled() {
        return on;
    }
    
    public void enable() {
        on = true;
        System.out.println("AC ON");
    }

    public void disable() {
        on = false;
        System.out.println("AC OFF");
    }

    public int getLevel() {
        return temperature;
    }

    public void setLevel(int t) {
        temperature = t;
        System.out.println("AC temperature: " + t + "Degree Celsius");
    }
}

class Speaker implements Device{
    private boolean on = false;
    private int volume = 30;

    public boolean isEnabled() {
        return on;
    }
    
    public void enable() {
        on = true;
        System.out.println("Speaker ON");
    }

    public void disable() {
        on = false;
        System.out.println("Speaker OFF");
    }

    public int getLevel() {
        return volume;
    }

    public void setLevel(int v) {
        volume = v;
        System.out.println("Speaker volume: " + v);
    }
}

// ABSTRACTION side — remote control hierarchy
class RemoteControl {
    // The base of the "Abstraction" hierarchy does not have to be an abstract class
    protected Device device; // THE BRIDGE

    public RemoteControl(Device device) {
        this.device = device;
    }

    public void togglePower() {
        if (device.isEnabled()) {
            device.disable();
        }
        else{
            device.enable();
        }
    }
    
    public void levelUp() {
        device.setLevel(device.getLevel() + 10);
    }
    
    public void levelDown() {
        device.setLevel(device.getLevel() - 10);
    }
}

// Refined Abstraction — adds mute functionality
class AdvancedRemote extends RemoteControl {
    public AdvancedRemote(Device device) {
        super(device);
    }

    public void mute() {
        System.out.println("Muting " + device.getClass());
        device.setLevel(0);
    }
}

public class UniversalRemote{
    public static void main(String[] args) {
        // Client — pick any remote × any device at runtime
        Device tv = new Tv();
        RemoteControl tvRemote = new RemoteControl(tv);
        System.out.println("--- Testing TV ---");
        tvRemote.togglePower();
        tvRemote.levelUp();

        AdvancedRemote advTvRemote = new AdvancedRemote(tv);
        advTvRemote.mute(); // Muting Tv → TV volume: 0
        
        System.out.println("\n--- Testing AC ---");
        Device ac = new AC();
        // The EXACT same RemoteControl class works for the AC!
        RemoteControl acRemote = new RemoteControl(ac);
        acRemote.togglePower();
        acRemote.levelDown(); // Lowers AC temp
        
        System.out.println("\n--- Testing Speaker ---");
        Device speaker = new Speaker();
        // The AdvancedRemote class works for the speaker too!
        AdvancedRemote speakerRemote = new AdvancedRemote(speaker);
        speakerRemote.togglePower();
        speakerRemote.levelUp();
        speakerRemote.mute();
    }
}