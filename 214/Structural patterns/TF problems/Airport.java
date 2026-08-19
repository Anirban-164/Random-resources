import java.util.ArrayList;
import java.util.List;

/*
Air traffic controller (ATC) helps in communication between flights and coordinates/controls landing,
take-off. Two flights need not interact directly and there is no dependency between them. This
dependency is solved by the ATC. Draw a class diagram to present appropriate design pattern and
write necessary codes so that your code fulfills all the requirements.
 */

// Mediator Interface
interface ATCMediator { 
    void registerFlight(Flight f); 
    void requestLanding(Flight f); 
    void requestTakeoff(Flight f); 
    void freeRunway();
} 
  
// Concrete Mediator
class AirTrafficController implements ATCMediator { 
    private List<Flight> flights = new ArrayList<>(); 
    private boolean runwayFree = true; 
  
    public void registerFlight(Flight f) { 
        flights.add(f); 
    } 
  
    public void requestLanding(Flight f) { 
        if (runwayFree) { 
            runwayFree = false; 
            System.out.println(f.getId() + " cleared to land"); 
        } else {
            System.out.println(f.getId() + " told to hold, runway is busy"); 
        }
    } 
    
    public void requestTakeoff(Flight f) { 
        if (runwayFree) {
            runwayFree = false;
            System.out.println(f.getId() + " cleared for takeoff"); 
        } else {
            System.out.println(f.getId() + " told to wait, runway is busy"); 
        }
    } 
    
    // Method to free the runway after a flight lands/takes off
    public void freeRunway() {
        runwayFree = true;
        System.out.println("ATC: Runway is now free");
    }
} 
  
// Colleague Class
abstract class Flight { 
    protected ATCMediator mediator; 
    protected String id; 
    
    Flight(ATCMediator mediator, String id) { 
        this.mediator = mediator; 
        this.id = id; 
        mediator.registerFlight(this); 
    } 
    
    String getId() { return id; } 
    
    // flights never talk to each other directly
    void requestLanding() { 
        System.out.println(this.id + " is requesting to land...");
        mediator.requestLanding(this); 
    }   
    
    void requestTakeoff() { 
        System.out.println(this.id + " is requesting to takeoff...");
        mediator.requestTakeoff(this); 
    } 
    
    void finishAction() {
        System.out.println(this.id + " has cleared the runway.");
        mediator.freeRunway();
    }
} 
  
// Concrete Colleague
class PassengerFlight extends Flight { 
    PassengerFlight(ATCMediator m, String id) { 
        super(m, id); 
    } 
}

// Concrete Colleague
class CargoFlight extends Flight {
    CargoFlight(ATCMediator m, String id) {
        super(m, id);
    }
}

// Client
public class Airport {
    public static void main(String[] args) {
        ATCMediator atc = new AirTrafficController();
        
        Flight flight1 = new PassengerFlight(atc, "Flight 101");
        Flight flight2 = new CargoFlight(atc, "Cargo 404");
        
        // Scenario 1: flight 1 requests landing
        flight1.requestLanding();
        
        // Scenario 2: flight 2 requests landing while runway is occupied
        flight2.requestLanding();
        
        // Flight 1 finishes landing, freeing the runway
        flight1.finishAction();
        
        // Now Flight 2 can land
        flight2.requestLanding();
        flight2.finishAction();
    }
}