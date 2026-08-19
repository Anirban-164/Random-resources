// 2 way Adapter example:

// Target Interface 1: Expected by OldClient
interface OldPrinter {
    void printText(String text);
}

// Client 1: Only knows how to work with OldPrinter
class OldClient {
    private OldPrinter printer;

    public OldClient(OldPrinter printer) {
        this.printer = printer;
    }

    public void work() {
        printer.printText("Hello from OLD client");
    }
}

// Target Interface 2: Expected by NewClient
interface NewPrinter {
    void printDocument(String document);
}

// Client 2: Only knows how to work with NewPrinter
class NewClient {
    private NewPrinter printer;

    public NewClient(NewPrinter printer) {
        this.printer = printer;
    }

    public void work() {
        printer.printDocument("Hello from NEW client");
    }
}

// Adaptee: The existing, incompatible class that has the functionality we need
class ModernPrinter {
    public void print(String data) {
        System.out.println("Printing: " + data);
    }
}

// Adapter: Implements both target interfaces and wraps the Adaptee
class PrinterAdapter implements OldPrinter, NewPrinter {
    private ModernPrinter printer;

    public PrinterAdapter(ModernPrinter printer) {
        this.printer = printer;
    }

    // Translates the OldPrinter interface method to the Adaptee's method
    @Override
    public void printText(String text) {
        printer.print(text);
    }

    // Translates the NewPrinter interface method to the Adaptee's method
    @Override
    public void printDocument(String document) {
        printer.print(document);
    }
}


public class PrinterAdapterPattern {
    public static void main(String[] args) {
        // 1. Create the Adaptee
        ModernPrinter modernPrinter = new ModernPrinter();

        // 2. Wrap the Adaptee inside the Adapter
        PrinterAdapter adapter = new PrinterAdapter(modernPrinter);

        // 3. Pass the Adapter to the OldClient (which expects an OldPrinter)
        OldClient oldClient = new OldClient(adapter);

        // 4. Pass the Adapter to the NewClient (which expects a NewPrinter)
        NewClient newClient = new NewClient(adapter);

        // 5. The clients work with their expected interfaces, and the Adapter translates the calls
        oldClient.work();
        newClient.work();
    }

}