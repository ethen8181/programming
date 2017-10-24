/*
 * Task:
 * http://www.klintonbicknell.com/ling400fall2017/hw/hw2.html
 * 
 * External Jars:
 * stanford-corenlp-3.8.0-models.jar
 * stanford-corenlp-3.8.0.jar
 * lucene-core-7.1.0.jar
 * lucene-analyzers-common-7.1.0.jar
 * lucene-queryparser-7.1.0.jar
 * 
 * Reference:
 * https://stanfordnlp.github.io/CoreNLP/api.html
 */
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.HashSet;
import java.util.List;
import java.util.Properties;
import java.util.Scanner;
import java.util.Set;
import java.util.StringJoiner;

import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.ling.CoreAnnotations.LemmaAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.SentencesAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.TokensAnnotation;
import edu.stanford.nlp.pipeline.Annotation;
import edu.stanford.nlp.pipeline.StanfordCoreNLP;
import edu.stanford.nlp.util.CoreMap;


class Tokenizer3 {

    private StanfordCoreNLP pipeline;
    private Set<String> stopwords;

    Tokenizer3(String stopwordsPath) throws IOException {
        Properties props = new Properties();
        props.setProperty("annotators", "tokenize, ssplit, pos, lemma");
        pipeline = new StanfordCoreNLP(props);
        
        stopwords = new HashSet<String>();
        Scanner scanner = new Scanner(new File(stopwordsPath));
        while (scanner.hasNextLine()) {
            String stopword = scanner.nextLine();
            stopwords.add(stopword);
        }
        scanner.close();
    }
    
    public String coreNLPTokenize(String text) {
        Annotation document = new Annotation(text);
        pipeline.annotate(document);
        
        // Loop through sentences and tokens to build the tokenized string
        StringJoiner coreNLPJoiner = new StringJoiner(" ");
        List<CoreMap> sentences = document.get(SentencesAnnotation.class);
        for (CoreMap sentence: sentences) {      
            for (CoreLabel token: sentence.get(TokensAnnotation.class)) {
                String word = token.get(LemmaAnnotation.class);
                boolean keep = word.length() > 2 && !stopwords.contains(word);
                if (keep) {
                    coreNLPJoiner.add(word.toLowerCase());
                }
            }
        }
        String coreNLPString = coreNLPJoiner.toString();
        return coreNLPString;
    }
}


public class TextHomework3 {

    public static void main(String[] args) throws IOException {
        
        /*
         * Corenlp's normalization is chosen because the resulting normalization seems to
         * be on par with kstems from Lucene and it also provides the capability to
         * conduct sentence splitting. Although the Corenlp's default behavior does not have
         * stopwords removal and lowercasing tokens, this can be implemented without too much
         * effort (compared with say integrating Corenlp's sentence splitting to Lucene).
         */
        String stopwordsPath = "stopwords.txt";
        String inputPath = "classbios.txt", outputPath = "TextHomework3.txt";
        Scanner scanner = new Scanner(new File(inputPath));
        FileWriter fw = new FileWriter(outputPath);
        Tokenizer3 tokenizer = new Tokenizer3(stopwordsPath);

        while (scanner.hasNextLine()) {
            String text = scanner.nextLine();
            String coreNLPString = tokenizer.coreNLPTokenize(text);
            fw.write(coreNLPString + "\n");
        }
        fw.close();
        scanner.close();
    }
}
