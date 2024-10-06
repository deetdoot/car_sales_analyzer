import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

def salesBySalesPerson(file_path):
    # Load the sales table
    sales_data = pd.read_csv(file_path)
    
    # Group the data by Salesperson and sum the total price of cars sold
    sales_by_person = sales_data.groupby('Salesperson')['TotalPrice'].sum()
    
    # Create a plot
    plt.figure(figsize=(10, 6))
    sales_by_person.plot(kind='bar')
    
    # Set the labels and title
    plt.xlabel('Salesperson')
    plt.ylabel('Total Sales Price')
    plt.title('Total Sales by Salesperson')
    
    # Show the plot
    plt.show()

