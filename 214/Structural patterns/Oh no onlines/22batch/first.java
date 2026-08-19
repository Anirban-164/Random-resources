/*
You have installed an IoT security device in your home. Whenever an event occurs, the device sends a notification to your smartphone. The system currently supports three basic types of notifications:
l) Email Notification
2) SMS Notification, and
3) push Notification.
Each notification type delivers the Same alert message using a different communication channel.The
mobile app associated with the IoT device receives and displays these notifications.

The mobile app, as you can see in the figure above, provides users with configurable options to 
enhance how notifications are handled. The options are listed below:
• Enable Encryption: The message should be encrypted before being sent.
• Priority Label: The message should be tagged as "High Priority" before delivery.
• Logging: Thc notification delivery should be logged in the IoT device for record-keeping
and auditing purposes.

Task: Choose the appropriate design pattern for sending notifications to seamlessly provide the
above features to users.

*/

interface Notification{
    void send();
}

class Message implements Notification {
    public void send() {
        System.out.println("message sent");
    }
}

class Email implements Notification {
    public void send() {
        System.out.println("Email sent");
    }
}

abstract class Decorator implements Notification {
    public abstract void send();
}


class Encryption extends Decorator {
    Notification n1;

    public Encryption(Notification n1) {
        this.n1 = n1;
    }

    public void send() {
        n1.send();
        System.out.println("    also encrypted");
    }
}


class Priority extends Decorator {
    Notification n1;

    public Priority(Notification n1) {
        this.n1 = n1;
    }

    public void send() {
        n1.send();
        System.out.println("    priority added ");
    }
}


public class first {
    public static void main(String[] args) {
        
        Notification n1 = new Message();
        n1.send();

        System.out.println("--------------------------------------");

        
        Notification n2 = new Email(); 
        n2 = new Priority(n2);     
        n2 = new Encryption(n2);   
        n2.send();
    }
}