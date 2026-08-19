/*
ZBazar is an online grocery platform that offers multiple delivery options. as given below:
- Standard Delivery (delivered within 24 hours)
- Express Delivery (delivered within 4 hours)
- Scheduled Delivery (delivered at a chosen time slot)

Each delivery has its own pricing logic and estimated delivery time calculation. Regardless of the
type, every order must ultimately be dispatched using a physical transportation method. Until now,
ZBazar has relied on bike couriers and van deliveries to fulfill orders. Recently, however, the company
has decided to introduce drone delivery in selected cities to speed up last-mile logistics. As a result, the development team now finds itself updating multiple classes just to support this new transportation
method, such as adding drone-specific dispatch logic. tracking integration, safety checks. etc., in Several
places. The situation is becoming harder to manage because. in the near future, ZBazar is also considering
introducing robot delivery for gated communities smart neighborhoods.

The challenge is business policies for delivery types may change frequently, while transport
technologies may expand over time. However, the current design tightly couples everything and thus
forces code duplication and repeated modifications whenever either dimension changes. Your task is to
redesign the system with an appropriate design pattern so that new transport technologies like drones or
robots to be introduced without rewriting existing delivery-type logic, and vice versa
*/



import java.util.ArrayList;
import java.util.List;

// =============================================================
// 1. IMPLEMENTOR INTERFACE (Transport Technology Dimension)
// only responsibility it to deliver goods
// =============================================================
interface TransportMethod {
    void deliver();
}

// Concrete Implementors
class DroneTransport implements TransportMethod {
    @Override
    public void deliver() {
        System.out.println("Dispatched using Automated Drone.");
    }
}

class RobotTransport implements TransportMethod {
    @Override
    public void deliver() {
        System.out.println("Dispatched using Autonomous Robot.");
    }
}


abstract class DeliveryType {
    protected TransportMethod transport; // Bridge Reference

    public DeliveryType(TransportMethod transport) {
        this.transport = transport;
    }

    public abstract double getTime();
    public abstract double getPrice();
    public abstract void processOrder();
}

// Refined Abstractions
class StandardDelivery extends DeliveryType {
    public StandardDelivery(TransportMethod transport) {
        super(transport);
    }

    @Override
    public double getTime() {
        return 24.0; // 24 Hours
    }

    @Override
    public double getPrice() {
        return 60.0;
    }

    @Override
    public void processOrder() {
        System.out.println("Standard Delivery [Price: ৳" + getPrice() + ", Est. Time: " + getTime() + " hrs]");
        transport.deliver(); // leave rest of the job to transport method 
    }
}

class ExpressDelivery extends DeliveryType {
    public ExpressDelivery(TransportMethod transport) {
        super(transport);
    }

    @Override
    public double getTime() {
        return 4.0; // 4 Hours
    }

    @Override
    public double getPrice() {
        return 150.0;
    }

    @Override
    public void processOrder() {
        System.out.println("Express Delivery [Price: ৳" + getPrice() + ", Est. Time: " + getTime() + " hrs]");
        transport.deliver();
    }
}

// =============================================================
// 3. CLIENT CODE
// =============================================================
public class sixth {
    public static void main(String[] args) {
        System.out.println("=== ZBazar Logistics System (Bridge Pattern) ===\n");

        // Scenario 1: Standard Delivery using Robot
        DeliveryType order1 = new StandardDelivery(new RobotTransport());
        order1.processOrder();

        System.out.println("----------------------------------------------");

        // Scenario 2: Express Delivery using Drone
        DeliveryType order2 = new ExpressDelivery(new DroneTransport());
        order2.processOrder();
    }
}