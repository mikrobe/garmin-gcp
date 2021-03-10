import logging

from google.cloud import firestore


class FirestoreClient(object):
    _LOG = logging.getLogger(__name__)

    def __init__(self, id_function, collection):
        self.client = firestore.Client()
        self.id_function = id_function
        self.collection = collection

    @staticmethod
    def identity_id(document_id):
        return document_id

    @staticmethod
    def reverse_id(document_id):
        return document_id[::-1]

    def is_exits(self, document_id):
        document_ref = self.client.collection(self.collection).document(self.id_function(document_id))
        document = document_ref.get()
        return document.exists

    def put(self, documents, id_field):
        for document in documents:
            self.client.collection(self.collection).add(document_id=self.id_function(document[id_field]), document_data=document)
