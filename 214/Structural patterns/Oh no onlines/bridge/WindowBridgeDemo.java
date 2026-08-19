
interface WindowImp {
    void implTop();
    void implBottom();
    void implSetExtent(int x, int y, int width, int height);
    void implDrawLine(int x1, int y1, int x2, int y2);
    void implDrawRect(int x, int y, int width, int height);
    void implDrawText(String text, int x, int y);
}

// ---- Concrete Implementor 1 ----
// Implements WindowImp using primitives of the X Window System.
class XWindowImp implements WindowImp {
    @Override
    public void implTop() {
        System.out.println("[XWindowImp] raising window to top via XMapRaised");
    }

    @Override
    public void implBottom() {
        System.out.println("[XWindowImp] lowering window via XLowerWindow");
    }

    @Override
    public void implSetExtent(int x, int y, int width, int height) {
        System.out.println("[XWindowImp] XMoveResizeWindow(" + x + "," + y + "," + width + "," + height + ")");
    }

    @Override
    public void implDrawLine(int x1, int y1, int x2, int y2) {
        System.out.println("[XWindowImp] XDrawLine(" + x1 + "," + y1 + " -> " + x2 + "," + y2 + ")");
    }

    @Override
    public void implDrawRect(int x, int y, int width, int height) {
        System.out.println("[XWindowImp] XDrawRectangle(" + x + "," + y + "," + width + "," + height + ")");
    }

    @Override
    public void implDrawText(String text, int x, int y) {
        System.out.println("[XWindowImp] XDrawString(\"" + text + "\" at " + x + "," + y + ")");
    }
}

// ---- Concrete Implementor 2 ----
// Implements WindowImp using primitives of IBM's Presentation Manager.
class PMWindowImp implements WindowImp {
    @Override
    public void implTop() {
        System.out.println("[PMWindowImp] WinSetWindowPos(..., HWND_TOP, ...)");
    }

    @Override
    public void implBottom() {
        System.out.println("[PMWindowImp] WinSetWindowPos(..., HWND_BOTTOM, ...)");
    }

    @Override
    public void implSetExtent(int x, int y, int width, int height) {
        System.out.println("[PMWindowImp] WinSetWindowPos with size " + width + "x" + height + " at (" + x + "," + y + ")");
    }

    @Override
    public void implDrawLine(int x1, int y1, int x2, int y2) {
        System.out.println("[PMWindowImp] GpiLine(" + x1 + "," + y1 + " -> " + x2 + "," + y2 + ")");
    }

    @Override
    public void implDrawRect(int x, int y, int width, int height) {
        System.out.println("[PMWindowImp] GpiBox(" + x + "," + y + "," + width + "," + height + ")");
    }

    @Override
    public void implDrawText(String text, int x, int y) {
        System.out.println("[PMWindowImp] GpiCharString(\"" + text + "\" at " + x + "," + y + ")");
    }
}

// ---- Abstraction ----
// Defines the window-level interface application code actually uses. It keeps a
// reference to a WindowImp and forwards platform-specific requests to it — that
// reference is the bridge.
class Window {
    protected WindowImp imp;
    protected int x, y, width, height;

    public Window(WindowImp imp, int x, int y, int width, int height) {
        this.imp = imp;
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
    }

    public void drawContents() {
        imp.implDrawRect(x, y, width, height);
    }

    public void open() {
        imp.implSetExtent(x, y, width, height);
        imp.implTop();
        drawContents();
    }

    public void close() {
        imp.implBottom();
    }

    public void moveTo(int newX, int newY) {
        this.x = newX;
        this.y = newY;
        imp.implSetExtent(x, y, width, height);
    }
}

// ---- Refined Abstraction ----
// Adds icon-specific behaviour on top of Window, still oblivious to which
// platform's WindowImp it is actually talking to.
class IconWindow extends Window {
    private String label;

    public IconWindow(WindowImp imp, int x, int y, int width, int height, String label) {
        super(imp, x, y, width, height);
        this.label = label;
    }

    @Override
    public void drawContents() {
        imp.implDrawRect(x, y, width, height);
        imp.implDrawText(label, x + 4, y + height / 2);
    }
}

// ---- Client ----
public class WindowBridgeDemo {
    public static void main(String[] args) {
        System.out.println("--- Same Window logic, X Window System backend ---");
        Window xWindow = new Window(new XWindowImp(), 10, 10, 200, 100);
        xWindow.open();
        xWindow.moveTo(20, 20);
        xWindow.close();

        System.out.println("\n--- Same IconWindow logic, Presentation Manager backend ---");
        IconWindow pmIcon = new IconWindow(new PMWindowImp(), 0, 0, 64, 64, "notes.txt");
        pmIcon.open();
        pmIcon.close();

        // Notice: Window/IconWindow never changed between the two runs.
        // Only the WindowImp implementation swapped — that's the bridge at work.
    }
}