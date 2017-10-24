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
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Properties;
import java.util.Scanner;
import java.util.StringJoiner;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.TokenStream;
import org.apache.lucene.analysis.Tokenizer;
import org.apache.lucene.analysis.core.LowerCaseTokenizer;
import org.apache.lucene.analysis.en.EnglishAnalyzer;
import org.apache.lucene.analysis.en.KStemFilter;
import org.apache.lucene.analysis.en.PorterStemFilter;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.analysis.tokenattributes.CharTermAttribute;

import edu.stanford.nlp.ling.CoreAnnotations.LemmaAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.SentencesAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.TokensAnnotation;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.pipeline.Annotation;
import edu.stanford.nlp.pipeline.StanfordCoreNLP;
import edu.stanford.nlp.util.CoreMap;

/*
 * Reference:
 * https://stackoverflow.com/questions/38682588/extending-lucene-analyzer
 * https://lucene.apache.org/core/5_5_1/core/org/apache/lucene/analysis/Analyzer.html
 * https://github.com/apache/lucene-solr/blob/master/lucene/analysis/common/src/java/org/apache/lucene/analysis/en/EnglishAnalyzer.java#L98
 */
class PorterStemAnalyzer extends Analyzer {

    @Override
    protected TokenStreamComponents createComponents(String fieldname) {
        Tokenizer source = new LowerCaseTokenizer();
        TokenStream result = new PorterStemFilter(source);
        return new TokenStreamComponents(source, result);
    }
}


class KStemAnalyzer extends Analyzer {

    @Override
    protected TokenStreamComponents createComponents(String fieldname) {
        Tokenizer source = new LowerCaseTokenizer();
        TokenStream result = new KStemFilter(source);
        return new TokenStreamComponents(source, result);
    }
}


class Tokenizer2 {
    private StanfordCoreNLP pipeline;

    Tokenizer2() {
        Properties props = new Properties();
        props.setProperty("annotators", "tokenize, ssplit, pos, lemma");
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
                String word = token.get(LemmaAnnotation.class);
                coreNLPJoiner.add(word);
            }
        }
        String coreNLPString = coreNLPJoiner.toString();
        return coreNLPString;
    }
    
    public String LuceneTokenize(String text, String analyzerType) {
        StringJoiner LuceneJoiner = new StringJoiner(" ");
        Analyzer analyzer;
        switch (analyzerType) {
            case "english":
                analyzer = new EnglishAnalyzer();
                break;
            case "porter":
                analyzer = new PorterStemAnalyzer();
                break;
            case "kstem":
                analyzer = new KStemAnalyzer();
                break;
            default:
                analyzer = new StandardAnalyzer();
                break;
        }
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


public class TextHomework2 {

    public static void main(String[] args) throws IOException {
        
        /*
         * Judging from the output, the normalization used by Corenlp and kstems seems
         * to be the most reasonable. Due to the fact that it uses lemmatization or kstems
         * as oppose to porter stemming to perform the normalization. Although both stemming
         * and lemmization both converts words to their root form, lemmization tends
         * to give friendlier results as stemming operates on a single word without
         * the knowledge of the context, e.g. for the word economy. Porter stemming would
         * give us economi, whereas lemmization and kstems would retain the original form economy.
         */
        String inputPath = "wsj_0036", outputPath = "TextHomework2.txt";
        Scanner scanner = new Scanner(new File(inputPath));
        FileWriter fw = new FileWriter(outputPath);
        Tokenizer2 tokenizer = new Tokenizer2();

        while (scanner.hasNextLine()) {
            String text = scanner.nextLine();
            String coreNLPString = tokenizer.coreNLPTokenize(text);
            
            /*
             * loop through different varients of EnglishAnalyzer,PorterStemAnalyzer
             * and KStemAnalyzer
             */
            List<String> analyzerTypes = new ArrayList<String>(
                Arrays.asList("english", "porter", "kstem"));
            
            /*
             *  the original sentence and corenlp tokenized sentence will only be
             *  printed once if the lucene tokenzied sentence differs from them
             */
            boolean refresh = true;
            for (String analyzerType: analyzerTypes) {
                String LuceneString = tokenizer.LuceneTokenize(text, analyzerType);
                if (!LuceneString.equalsIgnoreCase(coreNLPString)) {
                    if (refresh) {
                        fw.write("[Original] " + text + "\n");
                        fw.write("[coreNLP] " + coreNLPString + "\n");
                        refresh = false;
                    }
                    fw.write("[Lucene " + analyzerType + "] " + LuceneString + "\n");
                }
            }
        }
        fw.close();
        scanner.close();
    }
}
