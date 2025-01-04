import pandas as pd
import matplotlib.pyplot as plt

# Specify the full path of the CSV file
file_path = r"C:\Users\yasar\work_space\disrubition-and-frequency\data\precipitation_data.csv"

# Read the CSV file
df = pd.read_csv(file_path)

# Use the Year column as the first column in the index
df.set_index('Year', inplace=True)

# Calculate the annual maximum rainfall
max_rainfall = df.max(axis=1)

# Calculate the annual total rainfall
total_rainfall = df.sum(axis=1)

# Create a new DataFrame with the annual maximum rainfall and total rainfall
data = pd.DataFrame({
    'Max Rainfall (mm)': max_rainfall,
    'Total Rainfall (mm)': total_rainfall
})

# Save the data to an Excel file
excel_file = r"C:\Users\yasar\work_space\disrubition-and-frequency\precipitation_summary.xlsx"
data.to_excel(excel_file, sheet_name='Rainfall Data')

# Maximum Rainfall Graph
plt.figure(figsize=(10, 6))
plt.plot(data.index, data['Max Rainfall (mm)'], label='Annual Maximum Rainfall', color='blue', marker='o')
plt.title('Annual Maximum Rainfall Amounts', fontsize=14)
plt.xlabel('Year', fontsize=12)
plt.ylabel('Rainfall Amount (mm)', fontsize=12)
plt.grid(True)
plt.tight_layout()
plt.legend()
# Save the maximum rainfall graph as a PNG image
max_rainfall_graph = r"C:\Users\yasar\work_space\disrubition-and-frequency\graphs\total-max-rainfall-graph\max_rainfall_graph.png"
plt.savefig(max_rainfall_graph)
plt.show()

# Total Rainfall Graph
plt.figure(figsize=(10, 6))
plt.plot(data.index, data['Total Rainfall (mm)'], label='Annual Total Rainfall', color='green', marker='x')
plt.title('Annual Total Rainfall Amounts', fontsize=14)
plt.xlabel('Year', fontsize=12)
plt.ylabel('Rainfall Amount (mm)', fontsize=12)
plt.grid(True)
plt.tight_layout()
plt.legend()
# Save the total rainfall graph as a PNG image
total_rainfall_graph = r"C:\Users\yasar\work_space\disrubition-and-frequency\graphs\\total-max-rainfall-graph\total_rainfall_graph.png"
plt.savefig(total_rainfall_graph)
plt.show()

print(f"Data has been successfully saved to the Excel file: {excel_file}")
print(f"Graphs have been saved as images: {max_rainfall_graph} and {total_rainfall_graph}")
