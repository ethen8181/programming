import java.io.IOException;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.StringField;
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

public class Lucene2 {

    public static void main(String[] args) throws IOException, ParseException {
        // Searching with queryparser
        
        Analyzer analyzer = new StandardAnalyzer();
        Directory directory = new RAMDirectory();
        IndexWriterConfig config = new IndexWriterConfig(analyzer);
        IndexWriter indexWriter = new IndexWriter(directory, config);

        // add a bunch of sample documents
        Document doc = new Document();
        StringField stringField = new StringField("name", "", Field.Store.YES);
        TextField textField = new TextField("content", "", Field.Store.YES);

        doc.removeField("name"); doc.removeField("content"); 
        stringField.setStringValue("First");
        textField.setStringValue("Humpty Dumpty sat on a wall,");
        doc.add(stringField); doc.add(textField); 
        indexWriter.addDocument(doc);

        doc.removeField("name"); doc.removeField("content"); 
        stringField.setStringValue("Second");
        textField.setStringValue("Humpty Dumpty had a great fall.");
        doc.add(stringField); doc.add(textField); 
        indexWriter.addDocument(doc);

        doc.removeField("name"); doc.removeField("content"); 
        stringField.setStringValue("Third");
        textField.setStringValue("All the king's horses and all the king's men");
        doc.add(stringField); doc.add(textField); 
        indexWriter.addDocument(doc);

        doc.removeField("name"); doc.removeField("content"); 
        stringField.setStringValue("Fourth");
        textField.setStringValue("Couldn't put Humpty together again.");
        doc.add(stringField); doc.add(textField); 
        indexWriter.addDocument(doc);

        indexWriter.commit();
        indexWriter.close();
 
        /*
         *  fuzzy search using levenshtein distance,
         *  to trigger a fuzzy search, we use the ~ tilde
         *  character at the end
         */
        QueryParser queryParser1 = new QueryParser("content", analyzer);
        Query query1 = queryParser1.parse("hump~");
        queryParser1.setFuzzyMinSim(2f);

        /*
         * setFuzzyPrefixLength
         * That would at least insist on the n character 
         * being correct.
         * http://lucene.472066.n3.nabble.com/Funny-results-with-Fuzzy-td535763.html
         */
        queryParser1.setFuzzyPrefixLength(3);
        printOutput(query1, directory);
        

        // TermQuery is a query that matches documents containing a specific term
        Query termQuery = new TermQuery(new Term("content", "humpty"));
        
        /*
         *  use a query builder to build a boolean query
         *  it allows us to specify whether each subquery must, must not, or should match
         *  https://stackoverflow.com/questions/33439826/how-to-use-a-booleanquery-builder-in-lucene-5-3-x
         */
        BooleanQuery.Builder queryBuilder2 = new BooleanQuery.Builder();
        
        // The options for occur are MUST (And relationship), MUST_NOT, and SHOULD (OR relationship)
        queryBuilder2.add(termQuery, BooleanClause.Occur.MUST_NOT);
        BooleanQuery query2 = queryBuilder2.build();
        printOutput(query2, directory);
        
        /*
         *  phrase matches a particular sequence of terms, while MultiPhraseQuery
         *  gives us the option to match multiple terms in the same position.
         *  
         *  slop sets the number of other words permitted between words in query phrase.
         *  If zero, then this is an exact phrase search.
         *  The slop is in fact an edit-distance, where the units correspond to moves of terms
         *  in the query phrase out of position. Slop must be at least 2 to allow for term swapping
         *  
         *  http://www.avajava.com/tutorials/lessons/how-do-i-query-for-words-near-each-other-with-a-phrase-query.html
         */
        int slop = 0;
        PhraseQuery.Builder queryBuilder3 = new PhraseQuery.Builder();
        queryBuilder3.add(new Term("content", "humpty"));
        queryBuilder3.add(new Term("content", "together"));
        queryBuilder3.setSlop(slop);
        PhraseQuery query3 = queryBuilder3.build();
        printOutput(query3, directory);
    }
    
    public static void printOutput(Query query, Directory directory) throws IOException {
        // output the matched city to a .txt file
        IndexReader indexReader = DirectoryReader.open(directory);
        IndexSearcher indexSearcher = new IndexSearcher(indexReader);
        
        // search for all matching documents
        // https://stackoverflow.com/questions/7900503/querying-for-all-results-in-lucene-indexsearcher
        TopDocs topdocs = indexSearcher.search(query, indexReader.numDocs());
        ScoreDoc[] hits = topdocs.scoreDocs;
        System.out.println("Found " + hits.length + " hits.");
        
        for (ScoreDoc hit: hits) {
            int docId = hit.doc;
            Document docSearched = indexSearcher.doc(docId);
            System.out.println("Content: " + docSearched.get("content"));
        }
        indexReader.close();
    }
}
