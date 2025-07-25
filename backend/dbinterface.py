from typing import Dict
from pymongo import MongoClient
from bson.objectid import ObjectId

from backend.task import Task, CreateTask, TaskId, UpdateTask


def _task_to_document(task: Task | CreateTask | UpdateTask) -> Dict:
    task_dict = dict(task)
    task_dict = {key: value for key, value in task_dict.items() if value is not None}
    return task_dict


def _id_to_query(id: TaskId):
    return {"_id": ObjectId(id)}


class MongoDBInterface:
    def __init__(self, db_name: str = "todo_app"):
        # Provide the mongodb atlas url to connect python to mongodb using pymongo
        CONNECTION_STRING = "mongodb://localhost:27017/"

        # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
        self._client = MongoClient(CONNECTION_STRING)

        # Create the database for our example (we will use the same database throughout the tutorial
        self._db = self._client[db_name]
        self._task_collection = self._db["tasks"]

    def get_task(self, id: TaskId) -> Task | None:
        result = self._task_collection.find_one(_id_to_query(id))
        if result is None:
            return None
        task = Task(
            id=str(result["_id"]),
            name=result["name"],
            isCompleted=result["isCompleted"],
        )
        return task

    def create_task(self, task: CreateTask) -> Task:
        result = self._task_collection.insert_one(_task_to_document(task))
        return Task(
            id=str(result.inserted_id), name=task.name, isCompleted=task.isCompleted
        )

    def delete_task(self, id: TaskId) -> int:
        result = self._task_collection.delete_one(_id_to_query(id))
        return result.deleted_count

    def update_task(self, id: TaskId, update_params: UpdateTask) -> Task | None:
        query = _id_to_query(id)
        update = {"$set": _task_to_document(update_params)}
        response = self._task_collection.update_one(query, update, upsert=False)
        if response.matched_count == 0:
            return None
        return self.get_task(id)

    def num_tasks(self) -> int:
        return self._task_collection.count_documents({})

    def print_tasks(self):
        for task in self._task_collection.find():
            print(task)


if __name__ == "__main__":
    db = MongoDBInterface()
    db.print_tasks()
