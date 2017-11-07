import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Scanner;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.FieldType;
import org.apache.lucene.document.TextField;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexOptions;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.index.Term;
import org.apache.lucene.index.Terms;
import org.apache.lucene.index.TermsEnum;
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
import org.apache.lucene.util.BytesRef;


class LuceneIndexRetrieval {
    Directory directory;
    Analyzer analyzer;
    Map<String, Integer> vocabulary;

    LuceneIndexRetrieval() {
        directory = new RAMDirectory();
        analyzer = new StandardAnalyzer();
    }

    public void createIndex(String inputPath) throws IOException {
        IndexWriterConfig config = new IndexWriterConfig(analyzer);
        IndexWriter indexWriter = new IndexWriter(directory, config);
        Scanner scanner = new Scanner(new File(inputPath));

        // create termVector field to access the termVector of each document later
        FieldType termVectorFieldType = new FieldType();
        termVectorFieldType.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS);
        termVectorFieldType.setTokenized(true);
        termVectorFieldType.setStored(true);
        termVectorFieldType.setStoreTermVectors(true);

        Document doc;
        while (scanner.hasNextLine()) {
            String[] line = scanner.nextLine().split(",");
            String city_name = line[0], country_name = line[1];
            String city_text = line[2], country_text = line[3];
            doc = new Document();
            doc.add(new TextField("city_name", city_name, Field.Store.YES));
            doc.add(new TextField("city_text", city_text, Field.Store.YES));
            doc.add(new TextField("country_name", country_name, Field.Store.YES));
            doc.add(new Field("country_text", country_text, termVectorFieldType));
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

        FileWriter writer = new FileWriter(outputPath);
        for (ScoreDoc hit: hits) {
            int docId = hit.doc;
            Document docSearched = indexSearcher.doc(docId);
            writer.write(docSearched.get("city_name") + "\n");
        }
        writer.close();
        indexReader.close();
    }

    /*
     * Map term to a fix integer so that we can build document matrix later.
     * https://stackoverflow.com/questions/19250753/generate-term-document-matrix-using-lucene-4-4
     */
    public void outputDTM(boolean fixedVocab) throws IOException {
        // index is used for incrementing the vocabulary's id (word -> id mapping)
        int index = 0;
        Terms terms;
        BytesRef term;
        TermsEnum termsEnum;
        IndexReader indexReader = DirectoryReader.open(directory);
        if (!fixedVocab) {
            vocabulary = new HashMap<String, Integer>();
        }

        /*
         * wordIndex is initialized to Integer so is can be compared with null
         * for accessing invalid keys in a hashmap 
         * https://stackoverflow.com/questions/16124228/the-operator-is-undefined
         */
        long count;
        Integer wordIndex;
        Map<Integer, Long> wordCount;

        // information needed for python's csr_matrix
        List<Long> values = new ArrayList<Long>();
        List<Integer> indptr, indices;
        indptr = new ArrayList<Integer>();
        indices = new ArrayList<Integer>();
        indptr.add(0);

        for (int i = 0; i < indexReader.maxDoc(); i++) {
            wordCount = new HashMap<Integer, Long>(); 
            terms = indexReader.getTermVector(i, "country_text");

            if (terms != null && terms.size() > 0) {
                // access the terms for this field
                termsEnum = terms.iterator();          
                while ((term = termsEnum.next()) != null) {
                    String word = term.utf8ToString();
                    // System.out.println(word);

                    if (!fixedVocab) {
                        /*
                         *  include the word in the vocabulary if
                         *  it does not exist yet by assigning it a new id
                         */
                        if (!vocabulary.containsKey(word)) {
                            vocabulary.put(word, index++);
                        }
                    }
                    
                    // ignore out-of-vocabulary items for fixedVocab = True
                    wordIndex = vocabulary.get(word);
                    if (wordIndex != null) {
                        count = termsEnum.totalTermFreq();
                        wordCount.put(wordIndex, count);
//                        count = wordCount.get(wordIndex);
//                        System.out.println(wordCount.size());
//                        if (count == null) {
//                            wordCount.put(wordIndex, 1);
//                        } else {
//                            wordCount.put(wordIndex, count + 1);
//                        }
                    }
                }
            }

            // add to the csr_matrix after building the featureCount for a single document
            for (Map.Entry<Integer, Long> map: wordCount.entrySet()) {
                values.add(map.getValue());
                indices.add(map.getKey());
            }
            indptr.add(values.size());
        }
        indexReader.close();

        FileWriter valueWriter, indptrWriter, indicesWriter, vocabularyWriter;
        valueWriter = new FileWriter("values.txt");
        indptrWriter = new FileWriter("indptr.txt");
        indicesWriter = new FileWriter("indices.txt");
        vocabularyWriter = new FileWriter("vocabulary.txt");

        for(long value: values) {
            valueWriter.write(value + "\n");
        }
        valueWriter.close();

        for(int value: indptr) {
            indptrWriter.write(value + "\n");
        }
        indptrWriter.close();

        for(int value: indices) {
            indicesWriter.write(value + "\n");
        }
        indicesWriter.close();

        for(Map.Entry<String, Integer> map: vocabulary.entrySet()) {
            vocabularyWriter.write(map.getKey() + " " + map.getValue() + "\n");
        }
        vocabularyWriter.close();
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
        int slop3 = 10;
        String outputPath3 = "phraseQuery.txt";
        String inputQuery3 = "located below sea level";
        lucene.phraseQuery(outputPath3, inputQuery3, slop3);

        // interesting query of our own choice
        int slop4 = 0;
        String outputPath4 = "interestingQuery.txt";
        String inputQuery4 = "night market";
        lucene.phraseQuery(outputPath4, inputQuery4, slop4);

        boolean fixedVocab = false;
        lucene.outputDTM(fixedVocab);
    }
}
