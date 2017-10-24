/*
 * Reference:
 * http://www.lucenetutorial.com/lucene-in-5-minutes.html
 */
import java.io.IOException;
import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.core.WhitespaceAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.TextField;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.queryparser.classic.ParseException;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TopDocs;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.RAMDirectory;


public class Lucene {

    public static void main(String[] args) throws IOException, ParseException {
        /*
         *  define an analyzer (what treatment to apply to the document
         *  before they are indexed) to tokenize texts into word tokens
         *  this will be used to instantiate the IndexWriterConfig;
         *  this along with the directory (where should we store the index)
         *  will be used to instantiate the actual IndexWriter
         *  
         *  Analyzer, Lucene-analyzers-common contains all major analyzer
         */

        Analyzer analyzer = new WhitespaceAnalyzer();
        // create in memory directory 
        Directory directory = new RAMDirectory();
        IndexWriterConfig config = new IndexWriterConfig(analyzer);
        IndexWriter indexWriter = new IndexWriter(directory, config);

        /*
         * Indexing information in Lucene requires creating a document,
         * and a document is composed of one or more field containing information
         * about the document.
         * 
         * A field contains name, value and type
         * 
         * Here we add the field to the document using the .add method
         * with the field's name as a first argument, the value as the second
         * and TextField type is used for content we want tokenize, and the last
         * argument configure the field to store a value so it can be retrieved
         * during a search
         * 
         * Finally, we add the document to the IndexWriter and the .close method
         * at the end commits the changes and close the writer
         */
        String text = "Lucene is an Information Retrieval library written in Java.";
        Document doc = new Document();
        doc.add(new TextField("Content", text, Field.Store.YES));
        indexWriter.addDocument(doc);
        indexWriter.close();

        /*
         * Now that we have the index built, we can perform some search query
         * 
         * We start off by opening the directory which gives us IndexReader (the
         * index for us to read) and use that to initialize the IndexSearcher. The
         * searcher is our gateway to search an index as far as Lucene is concerned
         */
        IndexReader indexreader = DirectoryReader.open(directory);
        IndexSearcher indexsearcher = new IndexSearcher(indexreader);

        /*
         * IndexSearcher performs the search by accepting a Query object and performs
         * the search with the IndexReader. In this case, we start with a QueryParser
         * specifying that we are searching for the fieldname "Content", then we also
         * pass in the analyzer (ideally we should be using the same analyzer for both
         * indexing and searching to obtain best result) so it can process the search
         * string into a set of tokens, then we parse the search string "Lucene"
         */
        QueryParser parser = new QueryParser("Content", analyzer);
        Query query = parser.parse("Lucene");

        /*
         * We now execute the search by specifying the number of hits
         * we wish to retrieve (Lucene will sort by the relevance of
         * the query with the documents). The result contains the relevant
         * document ids
         */
        int hitsPerPage = 10;
        TopDocs topdocs = indexsearcher.search(query, hitsPerPage);
        ScoreDoc[] hits = topdocs.scoreDocs;
        System.out.println("Found " + hits.length + " hits.");
        for (ScoreDoc hit: hits) {
            int docId = hit.doc;
            Document docSearched = indexsearcher.doc(docId);
            System.out.println("Content: " + docSearched.get("Content"));
        }

        // reader can only be closed when there is no need to access the documents anymore
        indexreader.close();
    }

}
