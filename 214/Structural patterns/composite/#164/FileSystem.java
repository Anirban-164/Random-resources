import java.util.*;

// Component: The common interface for both files and directories (Safe approach --> interface includes only the methods wil be needed by both leaf and composites.)
interface FileSystemComponent {
    // Core operations that both File and Directory must support
    double getSize();
    void print(String indent); // 'indent' just for the visualisation of the hierarchy
}

// Leaf: Represents a file that cannot have children
class File implements FileSystemComponent {
    private String name;
    private double size;

    public File(String name, double size) {
        this.name = name;
        this.size = size;
    }

    @Override
    public double getSize() {
        return size;
    }

    @Override
    public void print(String indent) {
        System.out.println(indent + "- File: " + name + " (" + size + " KB)");
    }
}

// Composite: Represents a directory that can hold files or other directories
class Directory implements FileSystemComponent {
    private String name;
    private List<FileSystemComponent> components = new ArrayList<>();

    public Directory(String name) {
        this.name = name;
    }

    // Child management operations are only here, not in the interface
    public void add(FileSystemComponent component) {
        components.add(component);
    }

    public void remove(FileSystemComponent component) {
        components.remove(component);
    }

    @Override
    public double getSize() {
        double totalSize = 0;
        // Recursively calculate the size of all components in this directory
        for (FileSystemComponent component : components) {
            totalSize += component.getSize();
        }
        return totalSize;
    }

    @Override
    public void print(String indent) {
        System.out.println(indent + "+ Directory: " + name + " (Total Size: " + getSize() + " KB)");
        // Recursively print all components in this directory
        for (FileSystemComponent component : components) {
            component.print(indent + "\t");
        }
    }
}

// Client
public class FileSystem {
    public static void main(String[] args) {
        // Create root directory
        Directory rootDir = new Directory("root");

        // Create sub-directories
        Directory docsDir = new Directory("documents");
        Directory mediaDir = new Directory("media");

        // Create files
        FileSystemComponent resume = new File("resume.pdf", 1500);
        FileSystemComponent notes = new File("notes.txt", 15);
        
        FileSystemComponent photo1 = new File("vacation.jpg", 3500);
        FileSystemComponent photo2 = new File("family.jpg", 4200);

        // Build the structure
        docsDir.add(resume);
        docsDir.add(notes);

        mediaDir.add(photo1);
        mediaDir.add(photo2);

        rootDir.add(docsDir);
        rootDir.add(mediaDir);
        
        // Add a file directly to root
        FileSystemComponent config = new File("config.sys", 50);
        rootDir.add(config);

        // Print the entire file system
        System.out.println("--- Entire File System ---");
        rootDir.print("");
        
        System.out.println("\n--- Just the Media Directory ---");
        mediaDir.print("");
    }
}
