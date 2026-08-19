/*
Dalchal is an online grocery platform that has grown rapidly. It now needs to keep users informed
about key subscription events. Whenever a user's monthly bazar is confirmed, dispatched, or
renewed, the system must send out a relevant notification to the concemed user.
However, its user base is diverse. Some users prefer Email, others rely on SMS, and a growing
segment expects Push Notifications or WhatsApp messages. Product management has made it
clear that new communication channels will be added over time as the platform expands into new
markets.On the other side, the notifications themselves are also evolving. The content, tone, and
structure of a "payment failed" alert is very different from a "your bazar is on the way" update,
and the business team regularly wants to introduce new event types as new features roll out.
The engineering team has been tasked with designing a notification system that is clean,
maintainable, and easy to extend, without the codebase turning into an unmanageable mess every
time a new channel or a new event Wpe is introduced.
Task: Choose the appropriate design pattem to solve this problem and implement a minimal
demonstration.
*/


interface NotificationChannel {
    void send(String recipient, String message);
}

class WhatsAppChannel implements NotificationChannel {
    @Override
    public void send(String recipient, String message) {
        System.out.println("[WHATSAPP -> " + recipient + "]: " + message);
    }
}

class EmailChannel implements NotificationChannel {
    @Override
    public void send(String recipient, String message) {
        System.out.println("[EMAIL -> " + recipient + "]: " + message);
    }
}


abstract class Notification {
    // This is the BRIDGE referencing the channel implementation
    protected NotificationChannel channel;

    public Notification(NotificationChannel channel) {
        this.channel = channel;
    }

    public abstract void sendNotification(String user);
}

class BazarDispatchedNotification extends Notification {
    public BazarDispatchedNotification(NotificationChannel channel) {
        super(channel);
    }

    @Override
    public void sendNotification(String user) {
        String msg = "Your monthly bazar is packed and on the way to your home!";
        channel.send(user, msg);
    }
}

class PaymentFailedNotification extends Notification {
    public PaymentFailedNotification(NotificationChannel channel) {
        super(channel);
    }

    @Override
    public void sendNotification(String user) {
        String msg = "ALERT: Subscription renewal payment failed. Please update your payment method.";
        channel.send(user, msg);
    }
}

// =============================================================
// 3. CLIENT CODE (Dalchal System Demonstration)
// =============================================================
public class third {
    public static void main(String[] args) {
        System.out.println("=== Dalchal Notification System (Bridge Pattern) ===\n");

        // Scenario 1: User A (Rahim) wants Bazar Dispatched via WhatsApp
        Notification notification1 = new BazarDispatchedNotification(new WhatsAppChannel());
        notification1.sendNotification("Rahim");
    }
}