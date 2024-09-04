# Card Price Monitoring Tool

This project uses a Python script to monitor and track the prices of cards across two online stores, Liga and Myp. It stores the price history in a Supabase database and sends notifications via Telegram when a price change is detected.

## Features

- Fetches card data (name, links, and quantity) from a Supabase database
- Scrapes the latest prices for each card from the Liga and Myp store websites
- Compares the latest prices with the stored price history
- Updates the price history in the Supabase database when a price change is detected
- Sends a Telegram message to a specified chat when a price change is detected

## Prerequisites

- Python 3.7 or higher
- Supabase account and API keys
- Telegram bot token and chat ID

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/card-price-monitor.git
   ```
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root directory and add the following environment variables:
   ```
   DB_URL=your_supabase_database_url
   DB_KEY=your_supabase_database_key
   TELEGRAM_TOKEN=your_telegram_bot_token
   CHAT_ID=your_telegram_chat_id
   ```
4. Run the script:
   ```
   python main.py
   ```

## Database Schema

The database schema for the tables used in this project is defined in the `table.sql` file in the project repository.

## Adding Cards to Monitor

To add a new card to be monitored, you need to add the card's Liga and Myp links to the `cards` table in the Supabase database. The script will then automatically fetch the card data and start monitoring the prices.
