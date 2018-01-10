/**
 * Created by ethen on 4/10/17.
 */
public class Hello {
    public static void main(String[] args) {
        String s = "A Strings are immutable";
        String[] s1 = s.split(" ");
        char result1 = s1[0].charAt(0);
        System.out.println(result1);
        int result2 = (int)result1;
        System.out.println(result2);

        int a = 66 / 5;
        System.out.println(a);

        String artist = " aRtist";
        artist = artist.substring(0, 1).toUpperCase() + artist.substring(1);

        String test = "a";
        if (artist.contains(test) ) {
            System.out.println("1");
        }
        
        System.out.println(artist);
        System.out.println(artist.toLowerCase().trim());

        String parsedLine = "nuke";
        String[] targets = {"nu", "chi", "haw"};

        for (String i: targets){
            if (parsedLine.contains(i)) {
                System.out.println(parsedLine);
            }
        }

        String word = "2";
        word += 1;
        System.out.println(word);
    }
}
