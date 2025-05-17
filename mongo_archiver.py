from pymongo import MongoClient, ASCENDING, DESCENDING
from datetime import datetime, timedelta
from datetime_truncate import truncate
from logger import *
from setting import get_variables

class MongoArchiver(Logger):
    def __init__(self, logfile):
        super().__init__(logfile, self.__class__.__name__)
        self.host = get_variables().MONGODB_HOST
        self.port = get_variables().MONGODB_PORT
        self.username = get_variables().MONGODB_USERNAME
        self.password = get_variables().MONGODB_PASSWORD
        self.data_retention_days = int(get_variables().DATA_RETENTION_DAYS)
        self.batch_size = get_variables().BATCH_SIZE

        self.is_source_mongodb_atlas = get_variables().IS_SOURCE_MONGODB_ATLAS
        self.source_mongodb_url = get_variables().SOURCE_MONGODB_URL
        self.is_archive_mongodb_atlas = get_variables().IS_ARCHIVE_MONGODB_ATLAS
        self.archive_mongodb_url = get_variables().ARCHIVE_MONGODB_URL 

        # Archive
        self.host_archive = get_variables().ARCHIVE_MONGODB_HOST
        self.port_archive = get_variables().ARCHIVE_MONGODB_PORT
        self.username_archive = get_variables().ARCHIVE_MONGODB_USERNAME
        self.password_archive = get_variables().ARCHIVE_MONGODB_PASSWORD
        self.is_archive_enabled = get_variables().IS_ARCHIVE_ENABLED
        self.archive_connection=None
        self.source_connection=None

    # Connection method
    def source_connect(self):
        try:
            self.source_connection = MongoClient()

            # Construct the MongoDB connection URI
            if (self.is_source_mongodb_atlas=="NO"):
                self.source_connection = MongoClient(f"mongodb://{self.host}:{self.port}/", username=self.username, password=self.password)
            else:
                self.source_connection = MongoClient(self.source_mongodb_url)

            return self.source_connection  # Success
        
        except Exception as e:
            print(f"Error: {e}")
            self.log_error(f"Exception: {str(e)}", exc_info=True)
            return None  # Error
        
    # Connection method
    def source_db_connect(self, db_name):
        try:
            self.source_connection = MongoClient()

            # Construct the MongoDB connection URI
            if (self.is_source_mongodb_atlas=="NO"):
                self.source_connection = MongoClient(f"mongodb://{self.host}:{self.port}/", username=self.username, password=self.password)
            else:
                 self.source_connection = MongoClient(self.source_mongodb_url)

            db = self.source_connection[db_name]

            return db  # Success
        
        except Exception as e:
            print(f"Error: {e}")
            self.log_error(f"Exception: {str(e)}", exc_info=True)
            return None  # Error

    # Connection method for archive database
    def archive_connect(self):
        try:
            self.archive_connection = MongoClient()

            if (self.is_archive_mongodb_atlas=="NO"):
                self.archive_connection = MongoClient(f"mongodb://{self.host_archive}:{self.port_archive}/", username=self.username_archive, password=self.password_archive)
            else:
                self.archive_connection = MongoClient(self.archive_mongodb_url)

            return self.archive_connection  # Success
        
        except Exception as e:
            print(f"Error: {e}")
            self.log_error(f"Exception: {str(e)}", exc_info=True)
            return None  # Error
        
    # Connection method for archive database
    def archive_db_connect(self, db_name):
        try:

            self.archive_connection = MongoClient()

            if (self.is_archive_mongodb_atlas=="NO"):
                self.archive_connection = MongoClient(f"mongodb://{self.host_archive}:{self.port_archive}/", username=self.username_archive, password=self.password_archive)
            else:
                self.archive_connection = MongoClient(self.archive_mongodb_url)

            db = self.archive_connection[db_name]

            return db  # Success
        
        except Exception as e:
            print(f"Error: {e}")
            self.log_error(f"Exception: {str(e)}", exc_info=True)
            return None  # Error

    # Disconnect client
    def db_disconnect(self):
        try:
            if self.source_connection: #Check if the client is initialized
                self.source_connection.close()
                self.source_connection = None # Set client to None after closing

            if self.archive_connection: #Check if the client is initialized
                self.archive_connection.close()
                self.archive_connection = None # Set client to None after closing

        except Exception as e:
            print(f"Error: {e}")
            self.log_error(f"Exception: {str(e)}", exc_info=True)
            return None  # Error

    # Create Index in source database
    def create_index(self, source_db_connection, collection_name, field_name):
        try:
        
            collection = source_db_connection[collection_name]

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

    # Get record counts
    def get_records_count(self, db_connection, collection_name, filter_criteria):
        total_docs = 0
        try:
            # connection
            collection = db_connection[collection_name]

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
    
    # Compact Collection
    def compact_collection(self, db_connection, collection_name):
        try:
            #collection = db_connection[collection_name]
            result = db_connection.command('compact', collection_name)

            print("Compact operation completed.")
            self.log_info("Compact operation completed.")
            return True
        
        except Exception as e:
            print(f"Error: {e}")
            self.log_error(f"Exception: {str(e)}", exc_info=True)
            return None  # Error
    
    # Compact Database
    def compact_database(self, db_connection):
        try:
           
            result = db_connection.command('compact')
            print("Compact operation completed.")
            self.log_info("Compact operation completed.")

            return True
        
        except Exception as e:
            print(f"Error: {e}")
            self.log_error(f"Exception: {str(e)}", exc_info=True)
            return None  # Error
    
    # Repair Database
    def repair_database(self, db_connection):
        try:

            result = db_connection.command('repairDatabase')
            print("Repair operation completed.")
            self.log_info("Repair operation completed.")

            return True
        
        except Exception as e:
            print(f"Error: {e}")
            self.log_error(f"Exception: {str(e)}", exc_info=True)
            return None  # Error
        
    # Archive Collection        
    def archive_data(self, source_db_name, source_collection_name, archive_db_name, archive_collection_name, ts_field_name, data_retention_days):
        try:

            total_archived = 0
            total_deleted = 0
           
            # Connection 
            source_connection = self.source_connect()
            archive_connection=self.archive_connect()

            # DB Connection
            source_db_conn=source_connection[source_db_name]
            archive_db_conn=archive_connection[archive_db_name]

            # source_db_conn=self.source_connection[source_db_name]
            # archive_db_conn=self.archive_connection[archive_db_name]

            # Create index on source DB
            index_name = self.create_index(source_db_connection=source_db_conn, collection_name=source_collection_name, field_name=ts_field_name)
            
            if not index_name:
                raise Exception("Unable to create index.")
            
            # Find cutoff date
            cutoff_date = datetime.now() - timedelta(days=data_retention_days)
            cutoff_date = truncate(cutoff_date, 'day')

            print(f"Data Retention From: {cutoff_date}")
            self.log_info(f"Data Retention From: {cutoff_date}")

            # Query
            filter_query = {f"{ts_field_name}": {"$lt": cutoff_date}}
            print(filter_query)

            # # Aggregation pipeline
            # pipeline = [
            #             {"$match": filter_query},  # Match documents based on filter criteria
            #             {"$group": {
            #                 "_id": None,
            #                 "min_date": {"$min": f"${ts_field_name}"},
            #                 "max_date": {"$max": f"${ts_field_name}"},
            #                 "count": {"$sum": 1}
            #             }},
            #             {"$project": {
            #                 "_id": 0,
            #                 "min_date": 1,
            #                 "max_date": 1,
            #                 "count": 1
            #             }}
            #             ]

            # Connect to collection
            source_collection = source_db_conn[source_collection_name]
            archive_collection = archive_db_conn[archive_collection_name]

            from_date = truncate(datetime.now(), 'day')
            to_date = from_date
            min_date_doc = source_collection.find_one(filter_query, sort=[(f"{ts_field_name}", ASCENDING)])
            max_date_doc = source_collection.find_one(filter_query, sort=[(f"{ts_field_name}", DESCENDING)])
            total_docs = source_collection.count_documents(filter_query)
            if min_date_doc and max_date_doc:
                from_date = min_date_doc[f"{ts_field_name}"]
                to_date =  max_date_doc[f"{ts_field_name}"]
            else:
                total_docs=0
                from_date = to_date + timedelta(days=1)
                print("No documents match the filter criteria.")
                self.log_info("No documents match the filter criteria.")
                return total_archived, total_deleted
            
            from_date = min_date_doc[f"{ts_field_name}"] if min_date_doc else None
            to_date = max_date_doc[f"{ts_field_name}"] if max_date_doc else None

            # # Execute the aggregation pipeline
            # result = list(source_collection.aggregate(pipeline))
            # from_date = truncate(datetime.now(), 'day')
            # to_date = from_date

            # if result:
            #     from_date = result[0]['min_date']
            #     to_date = result[0]['max_date']
            #     total_docs = result[0]["count"]

            # else:
            #     from_date = to_date + timedelta(days=1)
            #     total_docs = 0
            #     print("No documents match the filter criteria.")
            #     self.log_info("No documents match the filter criteria.")
            
            from_date = truncate(from_date, 'day')
            to_date = truncate(to_date, 'day')

            print(f"Total records for archive: {total_docs}")
            print(f"Archive Start Date: {from_date}")
            print(f"Archive End Date: {to_date}")

            self.log_info(f"Total records for archive: {total_docs}")
            self.log_info(f"Archive Start Date: {from_date}")
            self.log_info(f"Archive End Date: {to_date}")

            while (from_date<=to_date):

                start_date = from_date
                end_date = start_date + timedelta(days=1)
                # iso_start_date_str = start_date.isoformat()
                # iso_end_date_str = end_date.isoformat()

                filter_query_datewise = {
                    f"{ts_field_name}": {
                        "$gte": start_date,
                        "$lt": end_date
                    }
                }
                while True:
                    # Read documents for archive
                    batch = []
                    deleted_count= 0
                    batch = list(source_collection.find(filter_query_datewise).limit(self.batch_size))

                    inserted_id_lst = []

                    if batch:
                        try:
                            try:
                                archive_result = archive_collection.insert_many(batch, ordered=False, bypass_document_validation=True)
                                if archive_result.acknowledged:
                                    total_archived+=len(archive_result.inserted_ids)
                                    inserted_id_lst.extend(archive_result.inserted_ids)

                            except Exception as e:
                                self.log_error(f"Exception: {str(e)}")
                                print(f"Exception: {str(e)}")
                                # If error occured in bulk insert, then insert one by one using upsert
                                for document in batch:
                                    archive_result_replace = archive_collection.replace_one({"_id": document["_id"]}, document, upsert=True)
                                    if archive_result_replace.acknowledged:
                                        total_archived += 1
                                        inserted_id_lst.extend(archive_result_replace.upserted_id)
                            
                            # Delete archived data from source collection after successful archiving
                            # deleted_result = source_collection.delete_many({"_id": {"$in": [doc["_id"] for doc in batch]}}, comment="Archiving records")
                            if inserted_id_lst:
                                deleted_result = source_collection.delete_many({"_id": {"$in": inserted_id_lst}})
                                if deleted_result.acknowledged:
                                    deleted_count = deleted_result.deleted_count
                                    total_deleted += deleted_count
    
                        except Exception as e:
                            print(f"Error deleting archived documents from source: {e}")
                            self.log_error(f"Error deleting archived documents from source: {e}")
                            #break
                    
                    # Exit loop if record does not exist
                    if deleted_count == 0:
                        break

                str_date=from_date.strftime("%Y-%m-%d")

                print(f"{source_db_name}->{source_collection_name} - Archived[{str_date}]: {total_archived}/{total_docs}")
                self.log_info(f"{source_db_name}->{source_collection_name} - Archived[{str_date}]: {total_archived}/{total_docs}")

                print(f"{source_db_name}->{source_collection_name} - Deleted[{str_date}]: {total_deleted}/{total_docs}")
                self.log_info(f"{source_db_name}->{source_collection_name} - Deleted[{str_date}]: {total_deleted}/{total_docs}")

                # Next date
                from_date = from_date + timedelta(days=1)
            
            # Compact collection
            compact_status=self.compact_collection(db_connection=source_db_conn, collection_name=source_collection_name)
            

            self.db_disconnect()
            
            return total_archived, total_deleted

        except Exception as e:
            self.db_disconnect()
            print(f"Error: {e}")
            self.log_error(f"Exception: {str(e)}", exc_info=True)
            print(f"Total Archived Documents: {total_archived}")
            self.log_info(f"Total Archived Documents: {total_archived}")
            return total_archived, total_deleted
        

# if __name__ == "__main__":
#     log_file = "logs/log_fc780a16-d10a-4aee-9e9f-597963c9028b_2025-01-22_23-52-43.log"
#     client = MongoArchiver(logfile=log_file)
#     conn = client.source_connect()
    
#     print("Archiving process completed.")