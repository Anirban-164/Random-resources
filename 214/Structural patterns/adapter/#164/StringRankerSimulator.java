import java.util.*;

// Adaptee — legacy class, cannot be changed
class StringRanker {
    // Positive → a comes after b, negative → a comes before b
    public int rank(String a, String b) {
        return Integer.compare(a.length(), b.length()); // sort by length
    }
}

// Adapter — implements Comparator (target), delegates to StringRanker (adaptee)
class RankerAdapter implements Comparator<String> {
    private final StringRanker ranker;
    public RankerAdapter(StringRanker ranker) {
        this.ranker = ranker;
    }

    @Override
    public int compare(String a, String b) {
        return ranker.rank(a, b); // translate Comparator.compare → StringRanker.rank
    }
}

public class StringRankerSimulator{
    public static void main(String[] args) {
        // Client — standard Java sort, unaware of StringRanker
        List<String> words = new ArrayList<>(List.of("banana", "kiwi", "fig", "apple"));
        
        // Use the adapter to make StringRanker work with Collections.sort
        Comparator<String> comp = new RankerAdapter(new StringRanker());
        
        Collections.sort(words, comp);
        System.out.println(words); // [fig, kiwi, apple, banana]
    }
}