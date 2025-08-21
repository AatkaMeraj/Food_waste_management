# create merged_data from the 4 food waste management tables 

CREATE TABLE merged_data AS
SELECT
    c.Claim_ID,
    c.Food_ID,
    c.Receiver_ID,
    c.Status,
    c.Timestamp,
    f.Food_Name,
    f.Quantity,
    f.Expiry_Date,
    f.Provider_ID,
    f.Provider_Type,
    f.Location,
    f.Food_Type,
    f.Meal_Type,
    p.Name AS Name_provider,
    p.Type AS Type_provider,
    p.Address,
    p.City,
    p.Contact,
    r.Name AS Name_receiver,
    r.Type AS Type_receiver,
    r.City AS City_receiver,
    r.Contact AS Contact_receiver
FROM claims c
JOIN food_listings f
    ON c.Food_ID = f.Food_ID
JOIN providers p
    ON f.Provider_ID = p.Provider_ID
JOIN receivers r
    ON c.Receiver_ID = r.Receiver_ID;

SELECT * FROM merged_data

#------------------------------------------------------------------------------------------------------------------------------

# QUERIES

# How many food providers and receivers are there in each city
SELECT 
    City,
    COUNT(DISTINCT Provider_ID) AS provider_count,
    COUNT(DISTINCT Receiver_ID) AS receiver_count
FROM merged_data
GROUP BY City
ORDER BY receiver_count DESC;

# which type of provider contribute to the most food
SELECT  
    Provider_Type,
    SUM(Quantity) AS total_quantity
FROM merged_data
GROUP BY Provider_Type
ORDER BY total_quantity DESC;

# What is the contact info of the food provider in a specific city ('Shelbychester')
SELECT 
	Provider_Type, Address, City, Contact
    FROM merged_data
    WHERE City= 'South Alicia';
    
# Which receivers have claimed the most food
SELECT 
	Name_receiver,
    COUNT(Claim_ID) as total_claims
    FROM merged_data 
    GROUP BY Name_receiver
    ORDER BY total_claims DESC;
    
# what is the total quantity of food available from all providers
SELECT 
	Provider_Type,
	SUM(Quantity) AS 'Total Quantity'
    FROM merged_data
    GROUP BY Provider_Type;
    
    
# which city has highest number of food listings 
SELECT city,
	COUNT(Food_ID) as food_listings
    FROM merged_data
    GROUP BY City
    ORDER BY food_listings DESC;
    
# What are the most commonly available food types?
SELECT Food_Type,
	COUNT(Food_Type) as frequency
	FROM merged_data 
    GROUP BY Food_Type 
    ORDER BY frequency DESC;
    
# How many food claims have been made for each food item?
SELECT 
    Food_Name,
    COUNT(DISTINCT Claim_ID) AS total_claims
    FROM merged_data
    GROUP BY Food_Name
    ORDER BY total_claims DESC;

# Which provider has had the highest number of successful food claims?
SELECT 
	Name_Provider,
    COUNT(DISTINCT Claim_ID) as success_claim
    FROM merged_data 
    WHERE Status= 'Completed'
    GROUP BY Name_Provider
    ORDER BY success_claim 
    LIMIT 1;
    
    
# What percentage of food claims are completed vs. pending vs. canceled?
SELECT
	Status,
    COUNT(*)*100/ SUM(COUNT(*)) OVER () AS percent
    FROM merged_data
    GROUP BY Status
    ORDER BY percent;

# What is the average quantity of food claimed per receiver?
SELECT 
	Name_receiver,
    ROUND(AVG(Quantity),1) as avg_quantity
    FROM merged_data
    WHERE Status= 'Completed'
    GROUP BY Name_receiver
    ORDER BY avg_quantity DESC;
    
# Which meal type is claimed the most?
SELECT 
	Meal_Type,
    COUNT(Claim_ID) AS total_claims
    FROM merged_data
    GROUP BY Meal_Type
    ORDER BY total_claims DESC;

# What is the total quantity of food donated by each provider?
SELECT
Name_provider,
SUM(Quantity) as total_quantity
FROM merged_data
GROUP BY Name_provider
ORDER BY total_quantity DESC;

# No of days food claimed before expiry 
SELECT
    City,
    Food_Type,
    COUNT(*) AS total_items_claimed,
    AVG(DATEDIFF(DATE(Expiry_Date), DATE(Timestamp))) AS avg_days_before_expiry,
    MIN(DATEDIFF(DATE(Expiry_Date), DATE(Timestamp))) AS min_days_before_expiry,
    MAX(DATEDIFF(DATE(Expiry_Date), DATE(Timestamp))) AS max_days_before_expiry
FROM merged_data
WHERE Timestamp IS NOT NULL
GROUP BY City, Food_Type
ORDER BY avg_days_before_expiry DESC;

# Items claimed after expiry
SELECT
    COUNT(*) AS total_records,
    SUM(CASE WHEN Timestamp > Expiry_Date THEN 1 ELSE 0 END) AS invalid_claims,
    ROUND(SUM(CASE WHEN Timestamp > Expiry_Date THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS expiry_prcnt
FROM merged_data;



