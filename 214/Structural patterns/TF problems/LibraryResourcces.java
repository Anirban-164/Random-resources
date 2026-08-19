/* 
"At the company for which I work we are facing this problem: We have a large amount of application software written using a particular library. Let's call this library LibX. The provider of this library was XIndustries AB. We wanted to extend the functionality of our application and for this reason we tried to contact XIndustries AB to implement the necessary library functionality. To our surprise we found out that XIndustries AB has gone out of business. Fortunately we found out that there is another company called YEnterprise AB is producing LibY that provides the same functionality as LibX but many of the classes have different interfaces. We don't have access to the source code of the old library LibX and neither to the source code of LibY. What should we do?" 
Which design pattern is most appropriate to accommodate this change?
*/

class Result {}
class YResult {}

interface ILibX { // shape of the interface the app already depends on 
    Result operation(Object a, Object b); 
} 

class LibY { // third-party, no source access, different signature 
    YResult differentOperation(Object a, Object b) { 
        System.out.println("LibY processing data: " + a + ", " + b);
        return new YResult(); 
    } 
} 
  
class LibYAdapter implements ILibX { 
    private LibY libY; 
    
    // Injecting the Adaptee via constructor
    public LibYAdapter(LibY libY) {
        this.libY = libY;
    }
  
    public Result operation(Object a, Object b) { 
        System.out.println("Adapter: Translating ILibX operation to LibY differentOperation");
        YResult yr = libY.differentOperation(a, b); 
        return convert(yr);              // map YResult -> Result 
    } 
    
    private Result convert(YResult yr) { 
        System.out.println("Adapter: Converting YResult back to Result for the client");
        return new Result(); 
    } 
} 

public class LibraryResourcces {
    public static void main(String[] args) {
        // 1. Create the Adaptee
        LibY adaptee = new LibY();
        
        // 2. Wrap the Adaptee in the Adapter
        ILibX lib = new LibYAdapter(adaptee); 
        
        System.out.println("Client: Calling operation on ILibX");
        lib.operation("Data 1", "Data 2");
    }
}