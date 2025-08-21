# Food_waste_management

Food waste is one of the biggest challenges in today’s world. Every year, tons of edible food goes to waste while millions of people face hunger. This project aims to reduce food waste by creating a platform that connects food providers (restaurants, hotels, individuals, NGOs) with receivers (charities, shelters, or people in need).

The system helps in:

📊 Tracking & managing food donations efficiently

🏢 Connecting providers and receivers in real-time

⏳ Reducing food spoilage by monitoring expiry dates

Our goal is to make food redistribution simple, transparent, and impactful through a digital solution.

**Tables Used:**

1️⃣ Providers Table

Stores details of individuals, restaurants, or organizations donating food.

Key Columns:

Provider_ID – Unique ID for each provider

Name, Type (NGO, Restaurant, Household, etc.)

Address, City, Contact


2️⃣ Receivers Table

Stores details of people or organizations receiving food donations.

Key Columns:

Receiver_ID – Unique ID for each receiver

Name_receiver, Type_receiver (NGO, Shelter, Individual, etc.)

City_receiver, Contact_receiver


3️⃣ Food Listings Table

Contains details about food being donated.

Key Columns:

Food_ID – Unique ID for each food item

Food_Name, Food_Type, Meal_Type

Quantity, Expiry_Date

Provider_ID (Foreign Key → Providers table)

4️⃣ Claims Table

Links food donations to receivers and tracks transaction status.

Key Columns:

Claim_ID – Unique ID for each claim

Food_ID (FK → Food Items)

Receiver_ID (FK → Receivers)

Timestamp, Status (Pending, Completed, Expired)


🛠️ **Tech Stack**

Frontend: Streamlit

Backend/Database: MySQL (with SQLAlchemy + PyMySQL)

Language: Python 3.10+

Libraries Used:

streamlit

sqlalchemy

pymysql

pandas

🚀 **Features of Streamlit app**

✅ Secure Login – Connect using MySQL credentials to get access to the dashboard

✅ Filter & Explore – Filter & explore data in real-time and download results

✅ Contact  – Select from Providers & receiver whom to contact  

✅ SQL Query Studio - Enter queries and get results in real time (Downloadable results)

✅ CRUD Operations – Create, Read, Update, and Delete records directly to and from the database




