// Structural pattern used: Adapter Pattern
// Reason: Used to convert XML data into JSON format to make it compatible with a 3rd-party SmartAnalyticsLibrary.
import java.io.StringReader;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import org.w3c.dom.Document;
import org.xml.sax.InputSource;

// ==========================================
// 1. 3rd-Party Analytics Library
// It only accepts JSON data and cannot process XML.
// ==========================================
class SmartAnalyticsLibrary {
    public void analyzeData(String jsonData) {
        System.out.println("📊 [Analytics Library] Analyzing JSON data...");
        System.out.println("👉 Received JSON: " + jsonData + "\n");
    }
}


// ==========================================
// 2. Client Interface (Target)
// Our app uses this interface to send XML data.
// ==========================================
interface StockXmlTarget {
    void sendXmlData(String xmlData);
}


// ==========================================
// 3. Adapter Class
// Converts incoming XML data to JSON and calls the library.
// ==========================================
class XmlToJsonAdapter implements StockXmlTarget {
    private SmartAnalyticsLibrary analyticsLibrary;

    public XmlToJsonAdapter(SmartAnalyticsLibrary analyticsLibrary) {
        this.analyticsLibrary = analyticsLibrary;
    }

    @Override
    public void sendXmlData(String xmlData) {
        System.out.println("🔄 [Adapter] Received XML data. Converting to JSON...");

        try {
            // Parse the XML using Java's built-in DOM Parser
            DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
            DocumentBuilder builder = factory.newDocumentBuilder();
            Document doc = builder.parse(new InputSource(new StringReader(xmlData)));

            // Extract values from XML tags
            String name = doc.getElementsByTagName("name").item(0).getTextContent();
            String price = doc.getElementsByTagName("price").item(0).getTextContent();

            // Construct JSON string
            String jsonData = String.format("{\"stock\": {\"name\": \"%s\", \"price\": %s}}", name, price);

            // Pass the formatted JSON to the 3rd-party library
            analyticsLibrary.analyzeData(jsonData);

        } catch (Exception e) {
            System.err.println("❌ Parsing error: " + e.getMessage());
        }
    }
}


// ==========================================
// 4. Main Class / Driver Code
// ==========================================
public class xmljson {
    public static void main(String[] args) {
        // XML data fetched by our app
        String xmlStockData = "<stock>"
                            + "   <name>AAPL (Apple Inc.)</name>"
                            + "   <price>230.50</price>"
                            + "</stock>";

        System.out.println("🚀 App started...");
        System.out.println("📥 Fetched XML Data:\n" + xmlStockData + "\n");

        // Initialize 3rd-party library
        SmartAnalyticsLibrary analyticsLib = new SmartAnalyticsLibrary();

        // Pass the library object into the Adapter
        StockXmlTarget adapter = new XmlToJsonAdapter(analyticsLib);

        // Send XML data through the adapter
        adapter.sendXmlData(xmlStockData);
    }
}