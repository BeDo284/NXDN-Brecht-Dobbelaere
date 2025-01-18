import os
from datetime import *

import pandas as pd

from models import *

connect(host=os.getenv('MONGODB_LOCAL'), db='NXDN')

# Allowed file extensions for CSV files
ALLOWED_EXTENSIONS = {'csv'}


def get_data_from_dir(directory_path):
    files = [f for f in os.listdir(directory_path) if f.startswith('CommunicationLog') and f[22] == "4"]
    total_files = len(files)  # Total number of valid files
    processed_files = 0  # To count how many files are processed

    for filename in files:
        print(f"{processed_files} out of {total_files} files are done")
        try:
            if check_file_already_saved(filename):
                processed_files += 1
                continue

            file_path = os.path.join(directory_path, filename)
            df = pd.read_csv(file_path)
            site_number = filename[17]
            df['site_number'] = site_number

            df[['date', 'time']] = df['Date'].str.split(' ', expand=True)
            df[['Calling ID', 'Called ID', 'site_number']] = df[['Calling ID', 'Called ID', 'site_number']].fillna(
                0).astype(int)

            # Convert all other columns to strings using map
            int_columns = ['Calling ID', 'Called ID', 'site_number']
            other_columns = df.columns.difference(int_columns)
            df[other_columns] = df[other_columns].astype(str)

            for _, row in df.iterrows():
                log_entry = Log(
                    calling_id=row['Calling ID'],
                    called_id=row['Called ID'],
                    date=row['date'],
                    time=row['time'],
                    record_type=row['Record Type'],
                    call_type=row['Call Type'],
                    emergency=row['Emergency'],
                    talk_time=row['Talk Time'],
                    cause=row['Cause'],
                    direction=row['Direction'],
                    channel=row['Channel'],
                    site=row['site_number']
                )
                log_entry.save()

            # Save the processed filename in the ProcessedFile collection
            processed_file = ProcessedFile(filename=filename)
            processed_file.save()

            processed_files += 1
        except Exception as e:
            print(e)
    print("All eligible files have been processed and added to MongoDB.")


def get_new_data(file):
    try:
        # Check if file has already been processed
        if ProcessedFile.objects(filename=file.filename).first():
            return f"File '{file.filename}' has already been processed!", 400

        # Read the CSV file into a DataFrame
        df = pd.read_csv(file)
        site_number = file.filename[17]
        df['site_number'] = site_number

        df[['date', 'time']] = df['Date'].str.split(' ', expand=True)
        df[['Calling ID', 'Called ID', 'site_number']] = df[['Calling ID', 'Called ID', 'site_number']].fillna(
            0).astype(int)

        # Convert all other columns to strings using map
        int_columns = ['Calling ID', 'Called ID', 'site_number']
        other_columns = df.columns.difference(int_columns)
        df[other_columns] = df[other_columns].astype(str)

        inserted_count = 0

        for _, row in df.iterrows():
            log_entry = Log(
                calling_id=row['Calling ID'],
                called_id=row['Called ID'],
                date=row['date'],
                time=row['time'],
                record_type=row['Record Type'],
                call_type=row['Call Type'],
                emergency=row['Emergency'],
                talk_time=row['Talk Time'],
                cause=row['Cause'],
                direction=row['Direction'],
                channel=row['Channel'],
                site=row['site_number']
            )
            inserted_count += 1
            log_entry.save()

        # Save the processed filename in the ProcessedFile collection
        processed_file = ProcessedFile(filename=file.filename)
        processed_file.save()
        return f"File '{file.filename}' processed successfully with {inserted_count} records added.", 200

    except Exception as e:
        return {"error": str(e)}, 500


def check_file_already_saved(filename):
    if ProcessedFile.objects(filename=filename).first():
        return True
    else:
        return False


def get_filtered_logs(filters):
    query = Q()  # Start with an empty query

    if 'date__gte' in filters:
        query &= Q(date__gte=filters['date__gte'])
    if 'date__lte' in filters:
        query &= Q(date__lte=filters['date__lte'])
    if 'calling_id' in filters:
        query &= Q(calling_id=filters['calling_id'])
    if 'called_id' in filters:
        query &= Q(called_id=filters['called_id'])
    if 'site' in filters:
        query &= Q(site=filters['site'])

    return Log.objects(query).order_by('-date', '-time')


def get_unused_ids():
    unique_ids = Log.objects.distinct("calling_id")
    unique_ids.sort()
    unique_ids = [id for id in unique_ids if id <= 999]

    max_id = unique_ids[-1] if unique_ids else 0

    full_list = list(range(1, max_id + 1))

    missing_ids = list(set(full_list) - set(unique_ids))
    return missing_ids


def export_csv(data):
    current_datetime = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    downloads_folder = os.path.join(os.path.expanduser('~'), 'Downloads')
    output_path = os.path.join(downloads_folder, f"output_{current_datetime}.csv")

    logs_dict = []

    for log in data:
        log_data = log.to_mongo().to_dict()  # Convert the document to a dictionary
        log_data.pop('_id', None)
        logs_dict.append(log_data)

    df = pd.DataFrame(logs_dict)
    df.to_csv(output_path, index=False)
