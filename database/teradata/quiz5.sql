
# 1. How many distinct skus have the brand “Polo fas”, and are either size “XXL” or “black” in color?

SELECT COUNT(*)
FROM SKUINFO
WHERE brand = 'Polo fas' AND ( size = 'XXL' OR color = 'black' )

# A: 13,623


# 2. There was one store in the database which had only 11 days in one of its months 
# (in other words, that store/month/year combination only contained 11 days of transaction 
# data). In what city and state was this store located?

SELECT s.city, s.state, s.store
FROM STRINFO AS s INNER JOIN ( SELECT 	EXTRACT( MONTH from SALEDATE ) AS month_num, 
										EXTRACT( YEAR from SALEDATE )  AS year_num, 
										store,
										COUNT( DISTINCT SALEDATE ) AS day_nums
							   FROM 	TRNSACT
							   GROUP BY month_num, year_num, store
							   HAVING	day_nums = 11 ) AS store_clean
ON s.store = store_clean.store

# A: Atlanta, GA


# 3. Which sku number had the greatest increase in total sales revenue from November to December?

SELECT   TOP 1 sku,
	     SUM( CASE EXTRACT( MONTH from SALEDATE )
	   		  WHEN 11 THEN AMT 
	   		  END ) AS november,
	     SUM( CASE EXTRACT( MONTH from SALEDATE )
	   		  WHEN 12 THEN AMT
	   		  END ) AS december,
	     ( december - november ) AS increase
FROM     TRNSACT
GROUP BY sku
ORDER BY increase DESC

# A: 3949538


# 5. What is the brand of the sku with the greatest standard deviation in sprice? 
# Only examine skus which have been part of over 100 transactions.

# standard deviation : STDDEV_SAMP
SELECT 	 TOP 1 s.sku, s.brand, STDDEV_SAMP(t.sprice) AS std
FROM 	 TRNSACT AS t INNER JOIN SKUINFO AS s
ON 		 t.sku = s.sku
WHERE 	 STYPE = 'P'
GROUP BY s.sku, s.brand
HAVING 	 COUNT(t.sprice) > 100
ORDER BY std DESC

# A: Hart Sch


# 6. What is the city and state of the store which had the greatest increase in average daily revenue 
# (as I define it in Teradata Week 5 Exercise Guide) from November to December?

SELECT   TOP 1 s1.store, s1.city, s1.state,
	     SUM( CASE s2.month_num
	   		  WHEN 11 THEN s2.avg_revenue
	   		  END ) AS  november,
	     SUM( CASE s2.month_num
	   		  WHEN 12 THEN s2.avg_revenue
	   		  END ) AS december,
	     ( december - november ) AS increase
FROM     STRINFO AS s1 INNER JOIN ( SELECT 	 EXTRACT( MONTH from SALEDATE ) AS month_num,
										   	 EXTRACT( YEAR from SALEDATE )  AS year_num,
										   	 store,
										   	 SUM(AMT) AS revenue,
										   	 COUNT( DISTINCT SALEDATE ) AS transaction_count,
										   	 ( revenue / transaction_count ) AS avg_revenue
									FROM   	 TRNSACT
									WHERE 	 STYPE = 'P' AND NOT 
											 ( EXTRACT( MONTH from SALEDATE ) = 8 AND 
											   EXTRACT( YEAR from SALEDATE ) = 2005 )
									GROUP BY month_num, year_num, store
									HAVING 	 transaction_count > 20 AND month_num IN ( 11, 12 ) ) AS s2
ON s1.store = s2.store
GROUP BY s1.store, s1.city, s1.state
ORDER BY increase DESC

# A: Metairie, LA




