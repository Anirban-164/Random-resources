/*
You need to send notifications that vary along two independent dimensions:
--> Urgency: NormalNotification, UrgentNotification
--> Channel: EmailSender, SmsSender, PushSender

Motivation:
We assume a same notification can be sent through multiple mediums (though in real life it could be vice-versa)
--> so we can add a reference to the medium inside notification class
*/

// IMPLEMENTATION side — delivery channel hierarchy
interface MessageSender {
    void send(String recipient, String subject, String body);
}

class EmailSender implements MessageSender {
    public void send(String to, String subject, String body) {
        System.out.printf("EMAIL --> %s | %s: %s%n", to, subject, body);
    }
}

class SmsSender implements MessageSender {
    public void send(String to, String subject, String body) {
        System.out.printf("SMS --> %s | %s%n", to, body.substring(0, Math.min(60, body.length())));
    }
}

class PushSender implements MessageSender {
    public void send(String to, String subject, String body) {
        System.out.printf("PUSH --> %s | %s%n", to, subject);
    }
}

// ABSTRACTION side — urgency hierarchy
abstract class Notification {
    protected MessageSender sender; // THE BRIDGE

    public Notification(MessageSender sender) {
        this.sender = sender;
    }

    public abstract void notify(String recipient, String message);
}

// Refined Abstraction 1 — adds no extra formatting
class NormalNotification extends Notification {
    public NormalNotification(MessageSender sender) {
        super(sender);
    }
    public void notify(String recipient, String message) {
        sender.send(recipient, "Notification", message);
    }
}

// Refined Abstraction 2 — prefixes subject with URGENT and adds retry logic
class UrgentNotification extends Notification {
    public UrgentNotification(MessageSender sender) {
        super(sender);
    }
    public void notify(String recipient, String message) {
        sender.send(recipient, "URGENT", message.toUpperCase());
        System.out.println("--> Retrying in 60s if unacknowledged...");
    }
}


public class NotificationSender{
    public static void main(String[] args) {
        // Client — mix-and-match freely; only 2 + 3 = 5 classes total, not 2×3 = 6
        Notification n1 = new NormalNotification(new EmailSender());
        Notification n2 = new UrgentNotification(new SmsSender());
        Notification n3 = new UrgentNotification(new PushSender());

        n1.notify("alice@corp.com", "Your report is ready");
        n2.notify("+8801700000000", "Server is down!");
        n3.notify("device-token-xyz", "Payment failed");
        // Adding a WhatsAppSender? One new class — no Notification subclasses change.
        // Adding a ScheduledNotification? One new subclass — no Sender classes change.
    }
}

/*
    # in real life scenario, could it be other way around? i.e. notification inside messageSender
    --> yes it can

    # But is it still Bridge?
    --> Not exactly

    # but why?
    --> The key is: “What changes independently?”

        Current design:-
        You have 2 independent dimensions:
        - urgency: normal / urgent
        - channel: email / SMS / push
        These are separate concerns, so Bridge is useful.

        Think:
        - “Normal” is a kind of notification behavior
        - “Email” is a kind of delivery behavior
        - they can be combined freely

        Reversed design:-
        Now imagine:
        the sender is the real smart part
        the notification is just a data object like:
        - recipient
        - message text
        - priority flag
        
        Then the sender does all channel-specific work:
        - EmailSender sends email
        - SmsSender sends SMS
        - PushSender sends push

        This is more like:
        “Here is a payload; send it through this channel”
        not “This notification object uses a sender”
*/