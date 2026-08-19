// *** IGNORE ***: class LogRecord used in adaptee class constructor
class LogRecord {
    private final String level;
    private final String message;
    private final Instant timestamp;

    public LogRecord(String level, String message, Instant timestamp) {
        this.level = level;
        this.message = message;
        this.timestamp = timestamp;
    }

    public String getLevel() {
        return level;
    }

    public String getMessage() {
        return message;
    }

    public Instant getTimestamp() {
        return timestamp;
    }
}

// Target interface
interface AppLogger {
    void log(String level, String message);
}

// Adaptee
class ThirdPartyLogger {
    public void write(LogRecord record) {
        System.out.printf("[%s] %s: %s%n",
            record.getTimestamp(), record.getLevel(), record.getMessage());
    }
}

// Adapter
class ThirdPartyLoggerAdapter implements AppLogger {
    private final ThirdPartyLogger logger;

    public ThirdPartyLoggerAdapter(ThirdPartyLogger logger) {
        this.logger = logger;
    }

    public void log(String level, String message) {
        // translate: build a LogRecord from the two loose strings
        LogRecord record = new LogRecord(level, message, Instant.now());
        logger.write(record);  // delegate to adaptee
    }
}

public class LegacyLogger{
    public static void main(String[] args) {
        AppLogger logger = new ThirdPartyLoggerAdapter(new ThirdPartyLogger());
        
        logger.log("INFO",  "Server started on port 8080");
        logger.log("ERROR", "Database connection failed");
    }
}