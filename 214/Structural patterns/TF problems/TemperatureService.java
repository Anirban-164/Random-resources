/* 
You have a service which returns the temperature (in celsius) by passing city name as an input
value. Now, assume that your client wants to pass zipcode as input and expecting the temperature of
the city in return. Develop a class diagram to present appropriate design pattern and write necessary
codes so that your code fulfils all the requirements. 
*/

import java.util.*;

interface ITemperatureService { 
    double getTemperature(String zip); 
}

// existing class — cannot be changed 
class CityTemperatureService {
    private Map<String, Double> cityTemp = new HashMap<>();
    
    public CityTemperatureService(){
        cityTemp.put("Dhaka", 25.0);
        cityTemp.put("Barisal", 26.0);
        cityTemp.put("Khulna", 27.0);
    }

    public double getTemperatureByCity(String city) { return cityTemp.getOrDefault(city, 0.0); }
} 
  
class ZipCodeTemperatureAdapter implements ITemperatureService { 
    private CityTemperatureService adaptee; 
    private Map<String, String> zipToCity; 
  
    ZipCodeTemperatureAdapter(CityTemperatureService adaptee, Map<String, String> 
zipToCity) { 
        this.adaptee = adaptee; 
        this.zipToCity = zipToCity; 
    } 
  
    public double getTemperature(String zip) { 
        String city = zipToCity.get(zip); 
        return adaptee.getTemperatureByCity(city);   // translate the call 
    } 
} 

public class TemperatureService {
    public static void main(String[] args) {
        Map<String, String> zipMap = new HashMap<>();
        zipMap.put("1207", "Dhaka");
        zipMap.put("1201", "Barisal");
        zipMap.put("1202", "Khulna");
        // client only ever depends on ITemperatureService 
        ITemperatureService service = new ZipCodeTemperatureAdapter(new CityTemperatureService(), 
        zipMap); 
        System.out.println(service.getTemperature("1207")); 
    }
}