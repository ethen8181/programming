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
import java.util.List;
import java.util.Properties;
import java.util.Scanner;
import java.util.StringJoiner;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.TokenStream;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.analysis.tokenattributes.CharTermAttribute;

import edu.stanford.nlp.ling.CoreAnnotations.SentencesAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.TextAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.TokensAnnotation;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.pipeline.Annotation;
import edu.stanford.nlp.pipeline.StanfordCoreNLP;
import edu.stanford.nlp.util.CoreMap;


class Tokenizer1 {
    private StanfordCoreNLP pipeline;

    Tokenizer1() {
        Properties props = new Properties();
        props.setProperty("annotators", "tokenize, ssplit");
        pipeline = new StanfordCoreNLP(props);
    }
    
    public String coreNLPTokenize(String text) {
        Annotation document = new Annotation(text);
        pipeline.annotate(document);
        
        // Loop through sentences and tokens to build the tokenized string
        StringJoiner coreNLPJoiner = new StringJoiner(" ");
        List<CoreMap> sentences = document.get(SentencesAnnotation.class);
        for (CoreMap sentence: sentences) {      
            for (CoreLabel token: sentence.get(TokensAnnotation.class)) {
                String word = token.get(TextAnnotation.class);
                coreNLPJoiner.add(word);
            }
        }
        String coreNLPString = coreNLPJoiner.toString();
        return coreNLPString;
    }
    
    public String LuceneTokenize(String text) {
        StringJoiner LuceneJoiner = new StringJoiner(" ");
        Analyzer analyzer = new StandardAnalyzer();
        try {
            TokenStream stream = analyzer.tokenStream(null, text);
            CharTermAttribute term = stream.addAttribute(CharTermAttribute.class);

            stream.reset();
            while (stream.incrementToken()) {
                String token = term.toString();
                LuceneJoiner.add(token);
            }
            stream.end();
            stream.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
        analyzer.close();
        String LuceneString = LuceneJoiner.toString();
        return LuceneString;
    }
}


public class TextHomework1 {

    public static void main(String[] args) throws IOException {
        /*
         * Based on the output, the tokenization used by Lucene's StandardAnalyzer
         * is more "aggressive than the default tokenization from CoreNLP. To be
         * more explicit, the StandardAnalyzer removes common english stopwords,
         * lowercase the tokens, gets rid of punctuation marks, while the CoreNLP
         * tokenization doesn't perform any of those tasks.
         */
        String inputPath = "wsj_0036", outputPath = "TextHomework1.txt";
        Scanner scanner = new Scanner(new File(inputPath));
        FileWriter fw = new FileWriter(outputPath);
        Tokenizer1 tokenizer = new Tokenizer1();

        while (scanner.hasNextLine()) {
            String text = scanner.nextLine();
            String coreNLPString = tokenizer.coreNLPTokenize(text);
            String LuceneString = tokenizer.LuceneTokenize(text);
            if (!LuceneString.equalsIgnoreCase(coreNLPString)) {
                fw.write("[Original] " + text + "\n");
                fw.write("[coreNLP] " + coreNLPString + "\n");
                fw.write("[Lucene] " + LuceneString + "\n");
            }
        }
        fw.close();
        scanner.close();
    }
}
