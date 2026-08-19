// An adapter using multiple classes (Facade-like Adapter):

// Target Interface: The interface the client (MediaPlayer) expects to interact with
interface SmartTV {
    void playMovie(String movieName);
}

// Adaptee 1: Existing, incompatible class handling video
class VideoPlayer {
    public void playVideo(String movie) {
        System.out.println("Playing video of " + movie);
    }
}

// Adaptee 2: Existing, incompatible class handling audio
class AudioPlayer {
    public void playAudio(String movie) {
        System.out.println("Playing audio of " + movie);
    }
}

// Adaptee 3: Existing, incompatible class handling subtitles
class SubtitlePlayer {
    public void showSubtitle(String movie) {
        System.out.println("Showing subtitles of " + movie);
    }
}


// Adapter: Implements the Target Interface and acts as a bridge, wrapping multiple Adaptees
class MovieAdapter implements SmartTV {
    private VideoPlayer videoPlayer;
    private AudioPlayer audioPlayer;
    private SubtitlePlayer subtitlePlayer;

    public MovieAdapter(VideoPlayer videoPlayer, AudioPlayer audioPlayer, SubtitlePlayer subtitlePlayer) {
        this.videoPlayer = videoPlayer;
        this.audioPlayer = audioPlayer;
        this.subtitlePlayer = subtitlePlayer;
    }

    // Translates the SmartTV playMovie method into calls across the multiple Adaptees
    @Override
    public void playMovie(String movieName) {
        videoPlayer.playVideo(movieName);
        audioPlayer.playAudio(movieName);
        subtitlePlayer.showSubtitle(movieName);
    }
}

// Client: Expects to work with a SmartTV interface
public class MediaPlayer {
    public static void main(String[] args) {
        // 1. Create the Adaptees
        VideoPlayer videoPlayer = new VideoPlayer();
        AudioPlayer audioPlayer = new AudioPlayer();
        SubtitlePlayer subtitlePlayer = new SubtitlePlayer();

        // 2. Wrap the Adaptees inside the Adapter
        SmartTV smartTV = new MovieAdapter(videoPlayer, audioPlayer, subtitlePlayer);
        
        // 3. The client (main) calls the Target Interface method, and the Adapter translates it
        smartTV.playMovie("Inception");
    }
}