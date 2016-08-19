library(dplyr)
library(tidyr)
library(ggplot2)
library(viridis)
library(reshape2)
library(tidytext)
library(wordcloud)
library(janeaustenr)

# https://cran.r-project.org/web/packages/tidytext/vignettes/tidytext.html
# http://juliasilge.com/blog/Life-Changing-Magic/

# CHAPTER and Chapter
original_books <- janeaustenr::austen_books() %>%
				  group_by(book) %>%
				  mutate( linenumber = row_number(),
						  chapter = cumsum( grepl( '^CHAPTER', text, ignore.case = TRUE ) ) ) %>%
				  ungroup()
original_books

# unnest_tokens from tidytext,
# split a column into tokens
tidy_books <- original_books %>%
			  unnest_tokens( output = 'word', input = 'text' )
tidy_books
dim(tidy_books)

# removing stop words using anti_join
data('stop_words')
tidy_books <- tidy_books %>%
			  anti_join(stop_words)
dim(tidy_books)

# most frequent words
count( tidy_books, word, sort = TRUE )


# sentiment data
bing <- sentiments %>%
		filter(lexicon == 'bing') %>%
		select(-score)
bing

# 1. %/% indicates integer division
# 2. compute the sentiment score by simply subtracting the number of positive words
# and negative words (each word's weight is equivalent)
janeausten_sentiment <- tidy_books %>%
						inner_join(bing) %>% 
						count( book, index = linenumber %/% 80, sentiment) %>% 
						spread( sentiment, n ) %>% 
						mutate( sentiment = positive - negative )
janeausten_sentiment

# group by different books, to plot the sentiment trend
ggplot( janeausten_sentiment, aes( index, sentiment, fill = book ) ) +
geom_bar( stat = 'identity', show.legend = FALSE) +
facet_wrap( ~book, ncol = 2, scales = 'free_x' ) +
theme_minimal( base_size = 13 ) +
scale_fill_viridis( end = 0.75, discrete = TRUE, direction = -1 ) +
labs( title = "Sentiment in Jane Austen's Novels", y = 'Sentiment' ) +
theme( strip.text = element_text( hjust = 0, face = 'italic' ),
	   axis.title.x = element_blank(),
	   axis.text.x = element_blank(),
	   axis.ticks.x = element_blank() )


# analyze word counts that contribute to each sentiment
bing_word_counts <- tidy_books %>%
					inner_join(bing) %>%
					count(word, sentiment, sort = TRUE) %>%
					ungroup()

# visualize the count for the commonly appeared positive and 
# negative word
bing_word_counts %>%
filter(n > 150) %>%
mutate( n = ifelse( sentiment == 'negative', -n, n ) ) %>%
mutate( word = reorder( word, n ) ) %>%
ggplot( aes( word, n, fill = sentiment ) ) +
geom_bar(stat = 'identity') +
theme( axis.text.x = element_text( angle = 90, hjust = 1 ) ) +
ylab('Contribution to sentiment')




# plot a single wordcloud
# max.words only plots the # of most frequent words

# you can also use input a Corpus to the wordcloud 
# http://datascienceplus.com/building-wordclouds-in-r/
tidy_books %>%
count(word) %>%
with( wordcloud( word, n, max.words = 100 ) )



# comparison.cloud between positive and negative sentiment
# count the number of each words grouped by sentiment (pos/neg)
tidy_books %>%
inner_join(bing) %>%
count( word, sentiment, sort = TRUE ) %>%
acast( word ~ sentiment, value.var = "n", fill = 0 ) %>%
comparison.cloud( colors = c( "#F8766D", "#00BFC4" ), max.words = 100 )



# pair_count function from tidytext
# counting words that appeared together
pride_prejudice_words <- filter( tidy_books, book == "Pride & Prejudice" )
word_cooccurences <- pride_prejudice_words %>%
					 pair_count( linenumber, word, sort = TRUE )
word_cooccurences


# -----------------------------------------------------------------------------------------
# topic-modeling
# https://cran.r-project.org/web/packages/tidytext/vignettes/topic_modeling.html
# https://eight2late.wordpress.com/2015/09/29/a-gentle-introduction-to-topic-modeling-using-r/

library(dplyr)
library(gutenbergr)
library(tidytext)
library(stringr)
library(tidyr)

# some preprocessing
titles <- c("Twenty Thousand Leagues under the Sea", "The War of the Worlds",
			"Pride and Prejudice", "Great Expectations")
books <- gutenberg_works(title %in% titles) %>%
		 gutenberg_download(meta_fields = "title")


by_chapter <- books %>%
group_by(title) %>%
mutate(chapter = cumsum(str_detect(text, regex("^chapter ", ignore_case = TRUE)))) %>%
ungroup() %>%
filter(chapter > 0)

by_chapter_word <- by_chapter %>%
unite(title_chapter, title, chapter) %>%
unnest_tokens(word, text)

word_counts <- by_chapter_word %>%
anti_join(stop_words) %>%
count(title_chapter, word, sort = TRUE) %>%
ungroup()

word_counts


# convert tidy word count into document-term matrix
chapters_dtm <- word_counts %>%
				cast_dtm(title_chapter, word, n)
chapters_dtm


library(topicmodels)
chapters_lda <- LDA(chapters_dtm, k = 4, method = "Gibbs", control = list(seed = 1234) )
chapters_lda


# the top five terms for each topic
terms( chapters_lda, 5 )

# we can go a step further
# beta: the probability of that word generated from that topic
chapters_lda_td <- tidy(chapters_lda)
chapters_lda_td

top_terms <- chapters_lda_td %>%
			 group_by(topic) %>%
			 top_n(5, beta) %>%
			 ungroup() %>%
			 arrange(topic, -beta)

top_terms %>%
mutate(term = reorder(term, beta)) %>%
ggplot(aes(term, beta)) +
geom_bar(stat = "identity") +
facet_wrap(~ topic, scales = "free") +
theme(axis.text.x = element_text(size = 15, angle = 90, hjust = 1))


# topics associated with each word
topics(chapters_lda)
chapters_lda_gamma <- tidy(chapters_lda, matrix = "gamma")
chapters_lda_gamma %>% arrange( document )



# LDA visualization
# https://github.com/cpsievert/LDAvis
# http://cpsievert.github.io/LDAvis/newsgroup/newsgroup.html
library(LDAvis)
json <- with( TwentyNewsgroups, 
			  createJSON( phi = phi, theta = theta, vocab = vocab,
						  doc.length = doc.length, term.frequency = term.frequency ) )


serVis(json)


# matrix format
# topic-term distributions (stored in a K×W matrix denoted ϕ)
# document-topic distributions (stored in a D×K matrix denoted θ)
phi <- posterior(chapters_lda)$terms
theta <- posterior(chapters_lda)$topics

# vocabulary names (in the same order as phi)
vocab <- colnames(phi)

# count the number of occurences for each word
term_frequency <- colSums( as.matrix(chapters_dtm) )

# obtain the number of tokens per document
# match the document order the theta
doc_length <- word_counts %>% count(title_chapter)
row_order  <- match( rownames(theta), doc_length$title_chapter )
doc_length <- doc_length[ row_order, ][['nn']]

json <- createJSON(
	phi = phi,
	theta = theta,
	vocab = vocab,
	doc.length = doc_length,
	term.frequency = term_frequency

)
serVis(json)
