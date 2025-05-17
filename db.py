from pymongo import MongoClient, ASCENDING
from datetime import datetime, timedelta
from datetime_truncate import truncate
import math
from setting import get_variables
from logger import *

class DatabaseExecutor(Logger):
    def __init__(self, logfile):
        super().__init__(logfile, self.__class__.__name__)
        self.host = get_variables().MONGODB_HOST
        self.port = get_variables().MONGODB_PORT
        self.username = get_variables().MONGODB_USERNAME
        self.password = get_variables().MONGODB_PASSWORD
        self.data_retention_days = get_variables().DATA_RETENTION_DAYS
        self.batch_size = get_variables().BATCH_SIZE

        # Archive
        self.host_archive = get_variables().ARCHIVE_MONGODB_HOST
        self.port_archive = get_variables().ARCHIVE_MONGODB_PORT
        self.username_archive = get_variables().ARCHIVE_MONGODB_USERNAME
        self.password_archive = get_variables().ARCHIVE_MONGODB_PASSWORD
        self.is_archive_enabled = get_variables().IS_ARCHIVE_ENABLED
    
    # Connection method
    def connect(self):
        try:
            # Construct the MongoDB connection URI
            connection = MongoClient(f"mongodb://{self.host}:{self.port}/", username=self.username, password=self.password)

            return connection  # Success
        
        except Exception as e:
            print(f"Error: {e}")
            self.log_error(f"Exception: {str(e)}", exc_info=True)
            return None  # Error
    
    # Return database object - if does not exist, it will be created first
    def get_database(self, db_name):
        try:
            conn = self.connect()
            #db = conn[self.database]
            db = conn[db_name]

            return db # Success
        except Exception as e:
            print(f"Error: {e}")
            self.log_error(f"Exception: {str(e)}", exc_info=True)
            return None  # Error

    # Connection method for archive database
    def connect_archive(self):
        try:

            connection = MongoClient(f"mongodb://{self.host_archive}:{self.port_archive}/", username=self.username_archive, password=self.password_archive)

            return connection  # Success
        
        except Exception as e:
            print(f"Error: {e}")
            self.log_error(f"Exception: {str(e)}", exc_info=True)
            return None  # Error
    
    # Return database object - if does not exist, it will be created first
    def get_database_archive(self, db_name):
        try:
            conn = self.connect_archive()
            #db = conn[self.database_archive]
            db = conn[db_name]

            return db # Success
        except Exception as e:
            print(f"Error: {e}")
            self.log_error(f"Exception: {str(e)}", exc_info=True)
            return None  # Error
        
    # Create Index
    def create_index(self, collection_name, field_name, db_name):
        try:
            db = self.get_database(db_name=db_name)
            collection = db[collection_name]

            # Get a list of existing indexes
            existing_indexes = collection.index_information()

            # Check if the field name already exists in any existing indexes
            if any(field_name in index['key'] for index in existing_indexes.values()):
                # Check if field_name exists in any existing index
                for index_name, index in existing_indexes.items():
                    if field_name in index['key']:
                        print(f"Index '{index_name}' already exists for field '{field_name}'.")
                        self.log_info(f"Index '{index_name}' already exists for field '{field_name}'.")
                        return index_name
            else:
                # Create the index
                index_name = collection.create_index([(field_name, ASCENDING)])
                print(f"Index for field '{field_name}' created successfully.")
                self.log_info(f"Index for field '{field_name}' created successfully.")

            return index_name
    
        except Exception as e:
            print(f"Error: {e}")
            self.log_error(f"Exception: {str(e)}", exc_info=True)
            return None  # Error

    # Archive Data
    def archive_data(self, source_collection, archive_collection, filter_condition):
        try:
            
            # print(f"filter_condition : {filter_condition}")
            # self.log_info(f"filter_condition : {filter_condition}")

            # Fetch data
            data = source_collection.find(filter_condition)

            cnt = len(list(data))
            print(f"Count : {cnt}")

            if cnt>0: # Check empty document
                
                try:
                    # Insert batch into destination collection
                    result =  archive_collection.insert_many(data, ordered=False)

                    total_records_inserted = len(result.inserted_ids)

                    print(f"Archived {total_records_inserted} records.")
                    self.log_info(f"Archived {total_records_inserted} records.")
                
                except Exception as e:
                    print(f"Error: {e}")
                    self.log_error(f"Exception: {str(e)}")
            else:
                print("No record found in archive process")
                self.log_info("No record found in archive process")

            return True
        
        except Exception as e:
            print(f"Error: {e}")
            self.log_error(f"Exception: {str(e)}", exc_info=True)
            return None  # Error   
        
    # Get record counts
    def get_records_count(self, collection_name, filter_criteria, db_name):
        total_docs = 0

        try:

            # Source database
            db = self.get_database(db_name=db_name)
            collection = db[collection_name]

            # Aggregation pipeline
            pipeline = [
                    {"$match": filter_criteria},  # Match documents based on filter criteria
                    {"$group": {
                        "_id": None,
                        "count": {"$sum": 1}
                    }},
                    {"$project": {
                        "_id": 0,
                        "count": 1
                    }}
                    ]

            # Execute the aggregation pipeline
            result = list(collection.aggregate(pipeline))

            if result:
                total_docs = result[0]["count"]
            else:
                total_docs = 0

            return total_docs
        
        except Exception as e:
            print(f"Error: {e}")
            self.log_error(f"Exception: {str(e)}", exc_info=True)
            return total_docs  # Error
            
    # Remove data from a collection by timestmap
    def delete_old_data_by_date(self, collection_name, ts_field_name, id_field_name, db_name):
        total_deleted = 0

        try:

            # Source database
            db = self.get_database(db_name=db_name)
            collection = db[collection_name]

            # Archive database
            db_archive = self.get_database_archive(db_name=db_name)
            collection_archive = db_archive[collection_name]

            # Create index on the date field for faster query
            index_name = self.create_index(collection_name=collection_name, field_name=ts_field_name, db_name=db_name)
            print(f"Index using: {index_name}")
            self.log_info(f"Index using: {index_name}")

            # Calculate the date X days ago
            retention_days_ago = datetime.utcnow() - timedelta(days=int(self.data_retention_days))
            iso_date_str = retention_days_ago.isoformat()

            print(f"Data Retention From: {retention_days_ago}")
            self.log_info(f"Data Retention From: {retention_days_ago}")

            # Use cursor to iterate over documents older than 30 days and delete them in batches
            #query = {ts_field_name: { "$lt": retention_days_ago.strftime('%Y-%m-%d %H:%M:%S') } }
            query = f"{{'{ts_field_name}': {{'$lt': ISODate('{iso_date_str}')}}}}"

            print(f"Executing: {query}")
            self.log_info(f"Executing: {query}")

            filter_criteria = {f"{ts_field_name}" : {"$lt" : retention_days_ago} }
            #filter_criteria = f"{{'{ts_field_name}': {{'$lt': ISODate('{iso_date_str}')}}}}"
            
            # Aggregation pipeline
            pipeline = [
                    {"$match": filter_criteria},  # Match documents based on filter criteria
                    {"$group": {
                        "_id": None,
                        "min_date": {"$min": f"${ts_field_name}"},
                        "max_date": {"$max": f"${ts_field_name}"},
                        "count": {"$sum": 1}
                    }},
                    {"$project": {
                        "_id": 0,
                        "min_date": 1,
                        "max_date": 1,
                        "count": 1
                    }}
                    ]

            # Execute the aggregation pipeline
            result = list(collection.aggregate(pipeline))
            # Print minimum and maximum dates
            from_date = truncate(datetime.now(), 'day')
            to_date = from_date

            if result:
                from_date = result[0]['min_date']
                to_date = result[0]['max_date']
                total_docs = result[0]["count"]

                from_date = truncate(from_date, 'day')
                to_date = truncate(to_date, 'day')

            else:
                from_date = to_date + timedelta(days=1)
                total_docs = 0
                print("No documents match the filter criteria.")
                self.log_info("No documents match the filter criteria.")

        
            batch_size = self.batch_size  # Adjust batch size as needed  

            print(f"Total records for deletion: {total_docs}")
            #print(f"Batch Size: {batch_size}")
            
            print(f"Archive Start Date: {from_date}")
            print(f"Archive End Date: {to_date}")

            self.log_info(f"Total records for deletion : {total_docs}")
            #self.log_info(f"Batch Size: {batch_size}")
            self.log_info(f"Archive Start Date: {from_date}")
            self.log_info(f"Archive End Date: {to_date}")

            # Calculate number of iterations based on document count and batch size
            # iterations = math.ceil(total_docs / batch_size)
            # print(f"Total iterations = {iterations}")
            # self.log_info(f"Total iterations = {iterations}")

            while (from_date<=to_date):
                
                start_date = from_date
                end_date = start_date + timedelta(days=1)

                iso_start_date_str = start_date.isoformat()
                iso_end_date_str = end_date.isoformat()

                #filter_condition = {ts_field_name: {"$gte": start_date, "$lt": end_date}}
                filter_condition = {
                    f"{ts_field_name}": {
                        "$gte": iso_start_date_str,
                        "$lt": iso_end_date_str
                    }
                }
                
                # filter_condition = f"{{'{ts_field_name}': {{'$gte': ISODate('{iso_start_date_str}'), '$lt': ISODate('{iso_end_date_str}')}}}}"

                #print(f"filter_condition={filter_condition}")

                # Archive records
                if (self.is_archive_enabled=="YES"):
                    archive_status = self.archive_data(source_collection=collection, archive_collection=collection_archive, filter_condition=filter_condition)
                    if (archive_status==None or archive_status==False):
                        print("Archive is failed!")
                        self.log_error("Archive is failed!")
                        break
                # Delete records
                result = collection.delete_many(filter_condition)
                #result = collection.delete_many({ts_field_name: {"$gte": start_date, "$lt": end_date}})
 
                if (result.deleted_count>0):
                    total_deleted += result.deleted_count
                    print(f"Deleted [{start_date}]: {total_deleted}/{total_docs} documents")
                    self.log_info(f"Deleted [{start_date}]: {total_deleted}/{total_docs} documents")

                # Next date
                from_date = from_date + timedelta(days=1)

            return total_deleted
        
        except Exception as e:
            print(f"Error: {e}")
            self.log_error(f"Exception: {str(e)}", exc_info=True)
            total_deleted = -1
            return total_deleted  # Error
        
    # Remove Older Data
    def delete_old_data(self, collection_name, ts_field_name, id_field_name, db_name):
        total_deleted = 0

        try:

            # Source database
            db = self.get_database(db_name=db_name)
            collection = db[collection_name]

            # Archive database
            db_archive = self.get_database_archive(db_name=db_name)
            collection_archive = db_archive[collection_name]

            # Create index on the date field for faster query
            index_name = self.create_index(collection_name=collection_name, field_name=ts_field_name)
            print(f"Index using: {index_name}")
            self.log_info(f"Index using: {index_name}")

            # Calculate the date X days ago
            retention_days_ago = datetime.utcnow() - timedelta(days=int(self.data_retention_days))
            print(f"Data Retention From: {retention_days_ago}")
            self.log_info(f"Data Retention From: {retention_days_ago}")

            # Use cursor to iterate over documents older than 30 days and delete them in batches
            query = {ts_field_name: { "$lt": retention_days_ago.strftime('%Y-%m-%d %H:%M:%S') } }
            print(f"Executing: {query}")
            self.log_info(f"Executing: {query}")
            #cursor = collection.find(query, projection={id_field_name: 1})
            #cursor = collection.find({ts_field_name: {"$lt": retention_days_ago}}, projection={id_field_name: 1})
            # Convert cursor to list
            # document_ids = [doc[id_field_name] for doc in cursor]

            # total_docs = len(document_ids)

            filter_criteria = {ts_field_name : {"$lt" : retention_days_ago} }

            # Aggregation pipeline to count number of documents
            pipeline = [
                { "$match": filter_criteria },  # Filter documents
                {
                    "$group": {
                        "_id": None,
                        "count": {"$sum": 1}
                    }
                }
            ]

            # Execute the aggregation pipeline
            result = list(collection.aggregate(pipeline))
            total_docs = result[0]["count"]

            batch_size = self.batch_size  # Adjust batch size as needed                    
            print(f"Total documents: {total_docs}")
            print(f"Batch Size: {batch_size}")
            
            self.log_info(f"Total documents: {total_docs}")
            self.log_info(f"Batch Size: {batch_size}")

            # Calculate number of iterations based on document count and batch size
            iterations = math.ceil(total_docs / batch_size)
            print(f"Total iterations = {iterations}")
            self.log_info(f"Total iterations = {iterations}")

            total_deleted = 0
            while (total_deleted<=total_docs):
                # Fetch documents older than 30 days in the current batch
                documents = collection.find({ts_field_name: {"$lt": retention_days_ago}}).limit(batch_size)

                # If Archive is enabled, insert records into archive database
                if (self.is_archive_enabled=="YES"):
                    archive_status = self.archive_data(archive_collection=collection_archive, data=documents, batch_size=batch_size)
                    if (archive_status==None or archive_status==False):
                        print("Archive is failed!")
                        self.log_error("Archive is failed!")
                        break

                # Get document IDs to delete
                ids_to_delete = [doc[id_field_name] for doc in documents]

                # Check if there are no more documents to delete
                if not ids_to_delete:
                    break

                # Delete documents in the current batch
                result = collection.delete_many({id_field_name: {"$in": ids_to_delete}})
                total_deleted += result.deleted_count
                print(f"Deleted: {total_deleted}/{total_docs}")
                self.log_info(f"Deleted: {total_deleted}/{total_docs}")

            return total_deleted
        
        except Exception as e:
            print(f"Error: {e}")
            self.log_error(f"Exception: {str(e)}", exc_info=True)
            return total_deleted  # Error
    
    # Compact Collection
    def compact_collection(self, collection_name, db_name):
        try:
            db = self.get_database(db_name=db_name)
            collection = db[collection_name]
        
            collection = db[collection_name]
            result = db.command('compact', collection.name)
            print("Compact operation completed.")
            self.log_info("Compact operation completed.")
            return True
        
        except Exception as e:
            print(f"Error: {e}")
            self.log_error(f"Exception: {str(e)}")
            return None  # Error
    
    # Compact Database
    def compact_database(self, db_name):
        try:
            db = self.get_database(db_name=db_name)
            
            result = db.command('compact')
            print("Compact operation completed.")
            self.log_info("Compact operation completed.")

            return True
        
        except Exception as e:
            print(f"Error: {e}")
            self.log_error(f"Exception: {str(e)}", exc_info=True)
            return None  # Error
    
    # Repair Database
    def repair_database(self, db_name):
        try:
            db = self.get_database(db_name=db_name)
            
            result = db.command('repairDatabase')
            print("Repair operation completed.")
            self.log_info("Repair operation completed.")

            return True
        
        except Exception as e:
            print(f"Error: {e}")
            self.log_error(f"Exception: {str(e)}", exc_info=True)
            return None  # Error
    
    # Create (Insert) operation
    def create_document(self, collection, document, db_name):
        try:
            # Select database
            db = self.get_database(db_name=db_name)

            # Select collection
            collection = db[collection]

            result = collection.insert_one(document)
            print(f"Document inserted with id: {result.inserted_id}")
            self.log_info(f"Document inserted with id: {result.inserted_id}")

            return result.inserted_id
        
        except Exception as e:
            print(f"Error: {e}")
            self.log_error(f"Exception: {str(e)}", exc_info=True)
            return None  # Error
    
    # Update operation -- update set of document according to query
    def update_document(self, query, new_values, db_name):
        try:
            # Select database
            db = self.get_database(db_name=db_name)

            # Select collection
            collection = db[collection]

            result = collection.update_one(query, {'$set': new_values})
            print(f"Modified {result.modified_count} document(s)")
            self.log_info(f"Modified {result.modified_count} document(s)")

            return result.modified_count
        
        except Exception as e:
            print(f"Error: {e}")
            self.log_error(f"Exception: {str(e)}", exc_info=True)
            return None  # Error
    
    # Delete operation - delete set of documents according to query
    def delete_document(self, query, db_name):
        try:
            # Select database
            db = self.get_database(db_name=db_name)

            # Select collection
            collection = db[collection]

            result = collection.delete_one(query)
            print(f"Deleted {result.deleted_count} document(s)")
            self.log_info(f"Deleted {result.deleted_count} document(s)")


            return result.deleted_count
        
        except Exception as e:
            print(f"Error: {e}")
            self.log_error(f"Exception: {str(e)}", exc_info=True)
            return None  # Error
    
    # Find documents and return list
    def find_documents(self, collection_name, condition, db_name):
        try:
            # Select database
            db = self.get_database(db_name=db_name)

            # Select collection
            collection = db[collection]

            # Find documents based on the condition
            documents = collection.find(condition)

            # Return the set of documents
            return list(documents)
        
        except Exception as e:
            print(f"Error: {e}")
            self.log_error(f"Exception: {str(e)}", exc_info=True)
            return None  # Error
    
    # Read a document recursively
    def read_document_list(self, document_list, prefix=''):
        try:
            for document in document_list:
                # read all fields by recursively
                self.read_document(document, prefix)

        except Exception as e:
            print(f"Error: {e}")
            self.log_error(f"Exception: {str(e)}", exc_info=True)
            return None  # Error
        
    # Read a document recursively
    def read_document(self, document, prefix=''):
        try:
            for key, value in document.items():
                if isinstance(value, dict):
                    self.read_document(value, prefix + '.' + key if prefix else key)
                else:
                    print(f"{prefix + '.' if prefix else ''}{key}: {value}")

        except Exception as e:
            print(f"Error: {e}")
            self.log_error(f"Exception: {str(e)}", exc_info=True)
            return None  # Error
        

    # Find documents by list of ids
    def get_records_by_ids(self, collection_name, id_list, db_name):
        try:
            db = self.get_database(db_name=db_name)
            collection = db[collection_name]

            # Query to retrieve records by IDs
            query = {"_id": {"$in": id_list}}

            # Return the records
            return list(collection.find(query))
        
        except Exception as e:
            print(f"Error: {e}")
            self.log_error(f"Exception: {str(e)}", exc_info=True)
            return None  # Error
    
    # Find Collection existances in existing database
    def check_colection_existance(self, collection_name, db_name):
        try:
            db = self.get_database(db_name=db_name)

            # Get list of collection names for the collection
            collection_lst = db.list_collection_names()

            # Check if the collection exists
            if collection_name in collection_lst:
                print(f"The collection '{collection_name}' exists.")
                self.log_info(f"The collection '{collection_name}' exists.")
                return True
            else:
                print(f"The collection '{collection_name}' does not exist.")
                self.log_info(f"The collection '{collection_name}' does not exist.")
                return False

        except Exception as e:
            print(f"Error: {e}")
            self.log_error(f"Exception: {str(e)}", exc_info=True)
            return None  # Error

    # Find Field existances in existing database
    def check_field_existance(self, collection_name, field_name, db_name):
        try:
            db = self.get_database(db_name=db_name)
            collection = db[collection_name]

            # Query the collection to find documents with the specified field
            documents_with_field = collection.find({field_name: {"$exists": True}})

            # Check if any documents with the field were found
            if documents_with_field.count() > 0:
                print(f"The field '{field_name}' exists in at least one document in the collection.")
                self.log_info(f"The field '{field_name}' exists in at least one document in the collection.")
                return True
            else:
                print(f"The field '{field_name}' does not exist in any document in the collection.")
                self.log_info(f"The field '{field_name}' does not exist in any document in the collection.")
                return False

        except Exception as e:
            print(f"Error: {e}")
            self.log_error(f"Exception: {str(e)}", exc_info=True)
            return None  # Error
            
    # Find Index existances in existing database
    def check_index_existance(self, collection_name, index_name, db_name):
        try:
            db = self.get_database(db_name=db_name)
            collection = db[collection_name]

            # Get list of index names for the collection
            index_names = collection.index_information()

            # Check if the index exists
            if index_name in index_names:
                print(f"The index '{index_name}' exists.")
                self.log_info(f"The index '{index_name}' exists.")
                return True
            else:
                print(f"The index '{index_name}' does not exist.")
                self.log_info(f"The index '{index_name}' does not exist.")
                return False

        except Exception as e:
            print(f"Error: {e}")
            self.log_error(f"Exception: {str(e)}", exc_info=True)
            return None  # Error

if __name__ == "__main__":
    operation_log = 'logs/test.log'
    db = DatabaseExecutor(operation_log)
    compact_status = db.compact_collection(collection_name='erp')
    if compact_status is not True:
        print("Database compact is failed!")
    
    compact_status = db.compact_database()
    if compact_status is not True:
        print("Database compact is failed!")