/*
 * Reference:
 * https://stackoverflow.com/questions/6334692/how-to-use-a-lucene-analyzer-to-tokenize-a-string
 * 
 * TokenStream Documentation
 * - https://lucene.apache.org/core/7_1_0/core/index.html
 */
import java.io.IOException;
import java.io.Reader;
import java.io.StringReader;
import java.util.ArrayList;
import java.util.List;
import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.TokenStream;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.analysis.tokenattributes.CharTermAttribute;


public class Lucene1 {

    public static void main(String[] args) throws IOException {
        /*
         * TokenStream is the intermediate data formats between
         * components within the analysis process.
         * 
         * To start processing Text, we turn our input String to
         * a StringReader and pass it to analyzer's tokenStream method (a String
         * would also work), then we add the attributes to the TokenStream to
         * ensure availability these attributes are then re-used to access their value.
         * CharTermAttribute is essentially our token's value
         * 
         * We then iterate through the TokenStream to obtain the value, note that
         * we also need to call .reset prior to every iteration routine and call
         * .end and .close to execute any end-of-stream operations and close out
         * the resources
         */
        List<String> result = new ArrayList<String>();
        Reader reader = new StringReader("Text to be passed");
        Analyzer analyzer = new StandardAnalyzer();
        
        try {
            TokenStream stream = analyzer.tokenStream(null, reader);
            CharTermAttribute term = stream.addAttribute(CharTermAttribute.class);

            stream.reset();
            while (stream.incrementToken()) {
                String token = term.toString();
                System.out.println(token);
                result.add(token);
            }
            stream.end();
            stream.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
        analyzer.close();
    }

}
