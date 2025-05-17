import xml.etree.ElementTree as ET
from logger import *
from setting import get_variables
import time
from task import *

class Index(Logger):
    def __init__(self, logfile, collection_no, collection_name, id_field_name, ts_field_name, description, collection_status, db_name, archived_records, deleted_records, data_retention_days):
        super().__init__(logfile, self.__class__.__name__)
        self.collection_no = collection_no
        self.collection_name = collection_name
        self.id_field_name = id_field_name
        self.ts_field_name = ts_field_name
        self.description=description
        self.collection_status=collection_status
        self.db_name=db_name
        self.archived_records=archived_records
        self.deleted_records=deleted_records
        self.data_retention_days=data_retention_days

    def __str__(self):
        return f"DB Name:{self.db_name}, Collection No: {self.collection_no}, Collection Name: {self.collection_name}, Id Field Name: {self.id_field_name}, Timestamp Field Name: {self.ts_field_name}, Description: {self.description}, collection status: {self.collection_status}"
    
class XmlReader(Logger):
    def __init__(self, logfile):
        super().__init__(logfile, self.__class__.__name__)
        self.operation_log = logfile
        self.indexes_xml_file_path = get_variables().INDEXES_XML_FILE_PATH
        self.total_collection=0

    # Read collection from xml file and load into task LIST and return a list
    def get_collection_list(self):
        try:
            xml_file=self.indexes_xml_file_path

            # Parse the XML file
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Create a list to store Task objects
            collection_list = []
            collection_no=0
            # Iterate through the queries and execute them
            for collections_element in root.findall('collections'):
                db_name = collections_element.get('db_name')

                for query in collections_element.findall('collection'):
                    #collection_no = query.get("collection_no")
                    collection_no = collection_no + 1
                    collection_name = query.get("collection_name")
                    id_field_name = query.get("id_field_name")
                    ts_field_name = query.get("ts_field_name")
                    collection_status = query.get("collection_status")
                    data_retention_days=int(query.get("data_retention_days"))
                    description = query.text.strip()
                    archived_records = 0
                    deleted_records = 0
                    index_obj = Index(logfile=self.log_file, collection_no=collection_no,collection_name=collection_name,id_field_name=id_field_name,ts_field_name=ts_field_name,description=description, collection_status= collection_status, db_name=db_name, archived_records=archived_records, deleted_records=deleted_records, data_retention_days=data_retention_days)
                    collection_list.extend([index_obj])
                    #print (task)
                    self.total_collection = self.total_collection +1
                
            return collection_list
        
        except Exception as e:
            self.log_error(f"Exception: {str(e)}", exc_info=True)
            print (f"Exception: {str(e)}")
            return None
    
    # Read all tasks from xml file and load into task LIST and return a list
    def get_task_list(self):
        try:
            xml_file=self.indexes_xml_file_path

            #print(xml_file)

            # Parse the XML file
            tree = ET.parse(xml_file)
            root = tree.getroot()

            # Create a list to store Task objects
            task_list = []
            task_no = 0
            
            # Iterate through the queries and execute them
            for collections_element in root.findall('collections'):
                db_name = collections_element.get('db_name')
                for query in collections_element.findall('collection'):
                    task_no = query.get("collection_no")
                    task_no = int(task_no) + 1
                    task_name = query.get("collection_name")
                    task_status = query.get("collection_status")
                    task_description = query.text.strip()
                    id_field_name = query.get("id_field_name")
                    ts_field_name = query.get("ts_field_name")
                    data_retention_days = int(query.get("data_retention_days"))
                    archived_records = 0
                    deleted_records = 0
                    task = Task(taskno=task_no,taskname=task_name,status=task_status,task_description=task_description, id_field_name=id_field_name, ts_field_name=ts_field_name, db_name=db_name, archived_records=archived_records, deleted_records=deleted_records, data_retention_days=data_retention_days)
                    task_list.extend([task])
                    self.log_info (f"DB: {db_name}, Collection: {task_name}")

            return task_list
        
        except Exception as e:
            self.log_error(f"Exception: {str(e)}", exc_info=True)
            print (f"Exception: {str(e)}")
            return None