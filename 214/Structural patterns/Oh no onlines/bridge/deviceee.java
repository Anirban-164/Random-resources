// Structural pattern used: Bridge Pattern
// Reason: Used to decouple the abstraction (RemoteControl) from its implementation (Device) so they can vary independently.
interface Device {
    boolean isEnabled();
    void enable();
    void disable();
    int getVolume();
    void setVolume(int percent);
    int getChannel();
    void setChannel(int channel);
    void printStatus();
}

// ---- Concrete Implementor 1 ----
class Tv implements Device {
    private boolean on = false;
    private int volume = 30;
    private int channel = 1;

    @Override
    public boolean isEnabled() {
        return on;
    }

    @Override
    public void enable() {
        on = true;
    }

    @Override
    public void disable() {
        on = false;
    }

    @Override
    public int getVolume() {
        return volume;
    }

    @Override
    public void setVolume(int percent) {
        volume = Math.max(0, Math.min(100, percent));
    }

    @Override
    public int getChannel() {
        return channel;
    }

    @Override
    public void setChannel(int channel) {
        this.channel = channel;
    }

    @Override
    public void printStatus() {
        System.out.println("------------------------------------");
        System.out.println("| TV: " + (on ? "ON" : "OFF"));
        System.out.println("| Volume: " + volume);
        System.out.println("| Channel: " + channel);
        System.out.println("------------------------------------");
    }
}

// ---- Concrete Implementor 2 ----
class Radio implements Device {
    private boolean on = false;
    private int volume = 20;
    private int channel = 88; // e.g. FM frequency step

    @Override
    public boolean isEnabled() {
        return on;
    }

    @Override
    public void enable() {
        on = true;
    }

    @Override
    public void disable() {
        on = false;
    }

    @Override
    public int getVolume() {
        return volume;
    }

    @Override
    public void setVolume(int percent) {
        volume = Math.max(0, Math.min(100, percent));
    }

    @Override
    public int getChannel() {
        return channel;
    }

    @Override
    public void setChannel(int channel) {
        this.channel = channel;
    }

    @Override
    public void printStatus() {
        System.out.println("------------------------------------");
        System.out.println("| Radio: " + (on ? "ON" : "OFF"));
        System.out.println("| Volume: " + volume);
        System.out.println("| Frequency: " + channel + " FM");
        System.out.println("------------------------------------");
    }
}

// ---- Abstraction ----
// Holds a reference to a Device (Implementor) instead of inheriting from it.
// This reference IS the bridge between the two hierarchies.
class RemoteControl {
    protected Device device;

    public RemoteControl(Device device) {
        this.device = device;
    }

    public void togglePower() {
        if (device.isEnabled()) {
            device.disable();
        } else {
            device.enable();
        }
    }

    public void volumeUp() {
        device.setVolume(device.getVolume() + 10);
    }

    public void volumeDown() {
        device.setVolume(device.getVolume() - 10);
    }

    public void channelUp() {
        device.setChannel(device.getChannel() + 1);
    }

    public void channelDown() {
        device.setChannel(device.getChannel() - 1);
    }
}

// ---- Refined Abstraction ----
// Extends the abstraction with extra features WITHOUT touching any Device code.
class AdvancedRemoteControl extends RemoteControl {

    public AdvancedRemoteControl(Device device) {
        super(device);
    }

    public void mute() {
        device.setVolume(0);
    }

    public void showStatus() {
        device.printStatus();
    }
}

// ---- Client ----
public class deviceee{
    public static void main(String[] args) {
        Device tv = new Tv();
        RemoteControl basicRemoteForTv = new RemoteControl(tv);
        basicRemoteForTv.togglePower();
        basicRemoteForTv.volumeUp();
        basicRemoteForTv.channelUp();
        tv.printStatus();

        Device radio = new Radio();
        AdvancedRemoteControl advancedRemoteForRadio = new AdvancedRemoteControl(radio);
        advancedRemoteForRadio.togglePower();
        advancedRemoteForRadio.volumeUp();
        advancedRemoteForRadio.mute();
        advancedRemoteForRadio.showStatus();

        // Key point: AdvancedRemoteControl works with Radio, Tv, or any
        // future Device (e.g. SmartSpeaker) without any of these classes
        // knowing about each other's inheritance tree.
    }
}