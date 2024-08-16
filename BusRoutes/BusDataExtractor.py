import pdfplumber
import csv
import re
import os

# Initialize CSV file
output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bus_routes.csv')

def extract_table_3(tables):
    """Function to extract table_3 based on the number of tables present."""
    if len(tables) > 2:
        return tables[2]  # Use the third table
    else:
        return tables[1]  # Fall back to the second table if only two tables exist

# Helper function to remove last two rows from a list of rows
def remove_last_two_rows(rows):
    if len(rows) >= 2:
        return rows[:-2]  # Remove the last two rows
    return rows  # Return as is if there are less than two rows

with open(output_file, mode='w', newline='') as file:
    writer = csv.writer(file)

    # Store all rows here temporarily
    all_rows = []

    with pdfplumber.open('/home/teshwar/Desktop/MoBis/BusRoutes/timer12345.pdf') as pdf:
        for page_num, page in enumerate(pdf.pages):
            tables = page.extract_tables()

            # Check if it is an empty page, cause there is one present 
            if len(tables) == 0 :
                print(f'{page_num} Empty Page, Done!')

                continue

            # Check if there's only one table, append data to previous table
            if len(tables) == 1:
                table_3 = tables[0]

                # Remove the last two rows
                all_rows = remove_last_two_rows(all_rows)

                # Append new data from the current table to the previous data
                for row in table_3[1:]:
                    all_rows.append([row[0], row[1]])

                # Add blank rows to separate pages
                all_rows.append([])
                all_rows.append([])

                continue

            # Extract data from Table 1
            table_1 = tables[0]

            if len(table_1) == 1 and len(table_1[0]) == 3:  # Three-column case
                route_text = table_1[0][0]
                operator_text = table_1[0][1]
                remark_text = table_1[0][2]

                route_number_match = re.search(r'\d+[A-Za-z]*', route_text)
                route_number = route_number_match.group() if route_number_match else 'Unknown'

                route_info = [
                    ('Route:', route_number),          # Extracted route number
                    ('Operator:', operator_text),      # Extracted operator
                    ('Remark:', remark_text)           # Extracted remark
                ]
            elif len(table_1) == 1 and len(table_1[0]) == 2:  # Two-column case
                operator_text = table_1[0][0]
                remark_text = table_1[0][1]

                print(f'ERR404: Page {page_num} Route not found ')
                route_info = [
                    ('Route:', 'Route not found'),  # Default route number
                    ('Operator:', operator_text),           # Operator from first column
                    ('Remark:', remark_text)                # Remark from second column
                ]
            else:
                route_text = " ".join(table_1[0][0].split())  # Join all lines into one string

                # Use regex to find a sequence of digits followed by optional letters
                route_number_match = re.search(r'\d+[A-Za-z]*', route_text)
                route_number = route_number_match.group() if route_number_match else 'Unknown'
            

                try: 
                    if (len(table_1) == 2):
                        print(f'ERR404: Page {page_num} Second location not found ')

                        route_info = [
                        ('Route:', route_number),          # Extracted route number (e.g., '1D', '200W')
                        ('Operator:', table_1[0][1]),      # "RHT"
                        ('Location 1:', table_1[1][1]),    # "Port Louis"
                        ('Location 2:', 'No second location')     # "Rose Hill"
                    ]
                    elif (len(table_1) == 3):
                         route_info = [
                        ('Route:', route_number),          # Extracted route number (e.g., '1D', '200W')
                        ('Operator:', table_1[0][1]),      # "RHT"
                        ('Location 1:', table_1[1][1]),    # "Port Louis"
                        ('Location 2:', table_1[2][1])     # "Rose Hill"
                    ]
                         
                    else:
                        route_info = [
                            ('Route:', route_number),          # Extracted route number (e.g., '1D', '200W')
                            ('Operator:', table_1[0][1]),      # "RHT"
                            ('Location 1:', table_1[2][1]),    # "Port Louis"
                            ('Location 2:', table_1[3][1])     # "Rose Hill"
                        ]
                except IndexError:
                    print(table_1)

            # Append Route info to the all_rows list
            for i, (label, data) in enumerate(route_info):
                all_rows.append([label, data])

            # Extract and append Fare Stage and Locality
            table_3 = extract_table_3(tables)
            for row in table_3[1:]:
                all_rows.append([row[0], row[1]])

            # Add blank rows to separate pages
            all_rows.append([])
            all_rows.append([])

            print(f'{page_num} done!')
    # Write all collected rows to the CSV file
    for row in all_rows:
        writer.writerow(row)
