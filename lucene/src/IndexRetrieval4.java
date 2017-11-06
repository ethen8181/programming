import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.Scanner;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.TextField;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.index.Term;
import org.apache.lucene.queryparser.classic.ParseException;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.search.BooleanClause;
import org.apache.lucene.search.BooleanQuery;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.PhraseQuery;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TermQuery;
import org.apache.lucene.search.TopDocs;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.RAMDirectory;


class LuceneIndexRetrieval {
    Directory directory;
    Analyzer analyzer;
    
    LuceneIndexRetrieval() {
        directory = new RAMDirectory();
        analyzer = new StandardAnalyzer();
    }
    
    public void createIndex(String inputPath) throws IOException {
        IndexWriterConfig config = new IndexWriterConfig(analyzer);
        IndexWriter indexWriter = new IndexWriter(directory, config);
        Scanner scanner = new Scanner(new File(inputPath));
        
        Document doc;
        while (scanner.hasNextLine()) {
            String[] line = scanner.nextLine().split(",");
            String city_name = line[0], country_name = line[1];
            String city_text = line[2], country_text = line[3];
            doc = new Document();
            doc.add(new TextField("city_name", city_name, Field.Store.YES));
            doc.add(new TextField("city_text", city_text, Field.Store.YES));
            doc.add(new TextField("country_name", country_name, Field.Store.YES));
            doc.add(new TextField("country_text", country_text, Field.Store.YES));
            indexWriter.addDocument(doc);
        }
        scanner.close();
        indexWriter.commit();
        indexWriter.close();
    }
    
    public void fuzzyQuery(String outputPath, String inputQuery, float fuzzyMinSim) throws ParseException, IOException {
        // find the pattern in the city's wiki page field
        QueryParser queryParser = new QueryParser("city_text", analyzer);
        queryParser.setFuzzyMinSim(fuzzyMinSim);
        Query query = queryParser.parse(inputQuery);
        writeOutput(query, outputPath);
    }
    
    public void boolQuery(String outputPath, Map<String, String[]> terms) throws ParseException, IOException {
        Query termQuery;
        BooleanQuery.Builder queryBuilder = new BooleanQuery.Builder();

        for (Map.Entry<String, String[]> entry: terms.entrySet()) {
            String occur = entry.getKey();
            for (String term: entry.getValue()) {
                termQuery = new TermQuery(new Term("city_text", term));
                if (occur == "MUST") {
                    queryBuilder.add(termQuery, BooleanClause.Occur.MUST);
                } else if (occur == "MUST_NOT") {
                    queryBuilder.add(termQuery, BooleanClause.Occur.MUST_NOT);
                } else {  // anything else is assume to match should
                    queryBuilder.add(termQuery, BooleanClause.Occur.SHOULD);
                }  
            }
        }
        BooleanQuery query = queryBuilder.build();
        writeOutput(query, outputPath);
    }

    public void phraseQuery(String outputPath, String inputQuery, int slop) throws ParseException, IOException {
        // each term in the inputQuery should be delimited by a space
        PhraseQuery.Builder queryBuilder = new PhraseQuery.Builder();
        for (String term: inputQuery.split(" ")) {
            queryBuilder.add(new Term("city_text", term));
        }
        queryBuilder.setSlop(slop);
        PhraseQuery query = queryBuilder.build();
        writeOutput(query, outputPath);
    }
    
    private void writeOutput(Query query, String outputPath) throws IOException {
        // output the matched city to a .txt file
        IndexReader indexReader = DirectoryReader.open(directory);
        IndexSearcher indexSearcher = new IndexSearcher(indexReader);
        TopDocs topdocs = indexSearcher.search(query, indexReader.numDocs());
        ScoreDoc[] hits = topdocs.scoreDocs;
        
        FileWriter fw = new FileWriter(outputPath);
        for (ScoreDoc hit: hits) {
            int docId = hit.doc;
            Document docSearched = indexSearcher.doc(docId);
            fw.write(docSearched.get("city_name") + "\n");
        }
        fw.close();
        indexReader.close();
    }
}


public class IndexRetrieval4 {

    public static void main(String[] args) throws IOException, ParseException {
        String inputPath = "capitals.txt";
        LuceneIndexRetrieval lucene = new LuceneIndexRetrieval(); 
        lucene.createIndex(inputPath);

        // fuzzy query
        float fuzzyMinSim = 5f;
        String inputQuery1 = "shakespeare";
        String outputPath1 = "fuzzyQuery.txt";
        lucene.fuzzyQuery(outputPath1, inputQuery1, fuzzyMinSim);

        // boolean query "Greek" and "Roman" but not "Persian"
        String outputPath2 = "booleanQuery.txt";
        Map<String, String[]> terms = new HashMap<String, String[]>();
        terms.put("MUST", new String[] {"greek", "roman"});
        terms.put("MUST_NOT", new String[] {"persian"});
        lucene.boolQuery(outputPath2, terms);
        
        // phrase query located below sea level with a slop of 10
        int slop = 10;
        String outputPath3 = "phraseQuery.txt";
        String inputQuery3 = "located below sea level";
        lucene.phraseQuery(outputPath3, inputQuery3, slop);
        
        // interesting query of our own choice
        String outputPath4 = "interestingQuery.txt";
        String inputQuery4 = "night market";
        lucene.phraseQuery(outputPath4, inputQuery4, 0);
    }
}
