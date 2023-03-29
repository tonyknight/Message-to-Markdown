import csv

# Set the name of the CSV file and the output file
csv_file = 'chat_logs.csv'
md_file = 'chat_logs.md'

# Define the CSS styles for the message blocks
css_styles = '''
<style>
    /* Style for sender messages */
    code[lang="sender"] {
        display: block;
        padding: 8px;
        margin: 10px 0;
        background-color: #f3f3f3;
        color: #000;
        float: left;
        clear: both;
    }
    /* Style for receiver messages */
    code[lang="receiver"] {
        display: block;
        padding: 8px;
        margin: 10px 0;
        background-color: #0074D9;
        color: #fff;
        float: right;
        clear: both;
    }
</style>
'''

# Open the CSV file for reading
with open(csv_file, 'r') as f:
    # Read the CSV data using the csv module
    reader = csv.DictReader(f)
    # Open the Markdown file for writing
    with open(md_file, 'w') as out:
        # Write the CSS styles to the file
        out.write(css_styles)
        # Loop through each row in the CSV file
        for row in reader:
            # Extract the necessary data from the row
            message_date = row['Message Date']
            sender_name = row['Sender Name']
            text = row['Text']
            attachment = row['Attachment']
            attachment_type = row['Attachment type']
            # Determine the message type (incoming or outgoing)
            message_type = 'Incoming' if row['Type'] == 'Incoming' else 'Outgoing'
            # Determine the sender name (if null, assume it's from me)
            if sender_name == '':
                sender_name = 'receiver.TonyKnight'
            # Write the Markdown code for the message
            lang = 'sender' if sender_name != 'receiver.TonyKnight' else 'receiver'
            out.write(f'```{lang}\n')
            out.write(f'{text}\n\n')
            if attachment:
                if attachment_type == 'Image':
                    out.write(f'![{attachment}]({attachment})\n\n')
                else:
                    out.write(f'[Attachment: {attachment}]({attachment})\n\n')
            out.write('```\n\n')
